"""ADR-020 complete training-only PLACEHOLDER BN rounding diagnostics.

No recipe changes the saved model or builds a replacement/deployment graph.
The double output recipe approximates a rounded affine expression, not a
hardware float32 FMA. NumPy/PyTorch disagreement is measured, never assumed away.
"""

import hashlib
from itertools import product

import numpy as np
import torch
from torch import nn

from .export_batchnorm import DIAGNOSTIC_NOTICE
from .export_replay import difference, validate_array

RECIPES = tuple('-'.join(parts) for parts in product(
    ('e32', 'e64'), ('r32', 'r64'), ('a32', 'a64'), ('b32', 'b64'), ('o32', 'o64')))
ORIGINS = {'python_input', 'onnx_input'}
METRICS = {'numpy_vs_native', 'torch_vs_native', 'numpy_vs_torch'}


def saved_arrays(module):
    if (not isinstance(module, nn.BatchNorm2d) or module.training or not module.affine
            or not module.track_running_stats or not np.isfinite(module.eps) or module.eps <= 0):
        raise ValueError('rounding requires saved affine eval BN with positive finite epsilon')
    arrays = [value.detach().numpy().reshape(1, -1, 1, 1).copy() for value in
              (module.weight, module.bias, module.running_mean, module.running_var)]
    if any(value.dtype != np.float32 or not np.isfinite(value).all() for value in arrays):
        raise ValueError('rounding requires finite saved float32 parameters')
    if np.any(arrays[-1] < 0):
        raise ValueError('rounding requires nonnegative saved variance')
    return arrays


def coefficients(module, recipe, engine):
    """Independent eager expressions; each cast is a declared rounding boundary."""
    if recipe not in RECIPES or engine not in ('numpy', 'torch'):
        raise ValueError('unknown declared rounding recipe/engine')
    epsilon, reciprocal, alpha_rounding, beta_rounding, _ = recipe.split('-')
    values = saved_arrays(module)
    if engine == 'numpy':
        weight, bias, mean, variance = values
        denominator = ((variance + np.float32(module.eps)).astype(np.float32) if epsilon == 'e32'
                       else variance.astype(np.float64) + np.float64(module.eps))
        inverse = ((np.float32(1) / np.sqrt(denominator.astype(np.float32))).astype(np.float32)
                   if reciprocal == 'r32' else np.float64(1) / np.sqrt(denominator.astype(np.float64)))
        alpha = ((weight * inverse.astype(np.float32)).astype(np.float32) if alpha_rounding == 'a32'
                 else (weight.astype(np.float64) * inverse.astype(np.float64)).astype(np.float32))
        beta = ((bias - (mean * alpha).astype(np.float32)).astype(np.float32) if beta_rounding == 'b32'
                else (bias.astype(np.float64) - mean.astype(np.float64) * alpha.astype(np.float64)).astype(np.float32))
    else:
        weight, bias, mean, variance = [torch.from_numpy(value) for value in values]
        with torch.inference_mode():
            denominator = ((variance + torch.tensor(module.eps, dtype=torch.float32)).float() if epsilon == 'e32'
                           else variance.double() + torch.tensor(module.eps, dtype=torch.float64))
            inverse = ((torch.tensor(1., dtype=torch.float32) / denominator.float().sqrt()).float()
                       if reciprocal == 'r32' else torch.tensor(1., dtype=torch.float64) / denominator.double().sqrt())
            alpha = ((weight * inverse.float()).float() if alpha_rounding == 'a32'
                     else (weight.double() * inverse.double()).float())
            beta = ((bias - (mean * alpha).float()).float() if beta_rounding == 'b32'
                    else (bias.double() - mean.double() * alpha.double()).float())
        denominator, inverse, alpha, beta = [value.numpy().copy() for value in (denominator, inverse, alpha, beta)]
    result = {'denominator': denominator, 'reciprocal': inverse, 'alpha': alpha, 'beta': beta}
    if any(not np.isfinite(value).all() for value in result.values()):
        raise ValueError('rounding coefficient overflow/nonfinite result')
    return result


def coefficient_cache(module):
    return {recipe: {engine: coefficients(module, recipe, engine) for engine in ('numpy', 'torch')}
            for recipe in RECIPES}


def array_record(value):
    return {'dtype': str(value.dtype), 'shape': list(value.shape),
            'bits_sha256': hashlib.sha256(np.ascontiguousarray(value).tobytes()).hexdigest()}


def coefficient_records(module, cache):
    return {'notice': DIAGNOSTIC_NOTICE,
            'saved_parameters': {key: array_record(value) for key, value in zip(
                ('weight', 'bias', 'mean', 'variance'), saved_arrays(module))},
            'epsilon_bits': {key: np.asarray(module.eps, dtype=dtype).tobytes().hex()
                             for key, dtype in (('float32', np.float32), ('float64', np.float64))},
            'recipes': {recipe: {engine: {key: array_record(value) for key, value in arrays.items()}
                        for engine, arrays in engines.items()} for recipe, engines in cache.items()}}


def apply_recipe(value, recipe, constants, engine):
    value = validate_array(value)
    if recipe not in RECIPES or engine not in ('numpy', 'torch'):
        raise ValueError('unknown declared rounding recipe/engine')
    alpha, beta = constants['alpha'], constants['beta']
    if value.shape[1] != alpha.shape[1]:
        raise ValueError('rounding channel mismatch')
    if engine == 'numpy':
        output = ((value * alpha).astype(np.float32) + beta if recipe.endswith('o32')
                  else (value.astype(np.float64) * alpha.astype(np.float64) + beta.astype(np.float64)).astype(np.float32))
    else:
        x, a, b = [torch.from_numpy(item) for item in (value, alpha, beta)]
        with torch.inference_mode():
            output = ((x * a).float() + b if recipe.endswith('o32') else (x.double() * a.double() + b.double()).float())
        output = output.numpy().copy()
    return validate_array(output)


def rounding_differences(value, native, cache):
    result = {}
    for recipe in RECIPES:
        numpy_output, torch_output = [apply_recipe(value, recipe, cache[recipe][engine], engine)
                                     for engine in ('numpy', 'torch')]
        result[recipe] = {'numpy_vs_native': difference(native, numpy_output),
                          'torch_vs_native': difference(native, torch_output),
                          'numpy_vs_torch': difference(numpy_output, torch_output)}
    return result


def validate_rounding_scope(protocol, graph, errors):
    if (protocol.get('rounding_recipes') != list(RECIPES)
            or protocol.get('rounding_engines') != ['numpy', 'torch']):
        raise ValueError('rounding declared recipe/engine scope mismatch')
    if graph['original_operator'] != 'BatchNormalization':
        if 'rounding_coefficients' in graph or 'rounding' in errors:
            raise ValueError('rounding must not replace Conv')
        return
    if (set(graph.get('rounding_coefficients', {}).get('recipes', {})) != set(RECIPES)
            or set(errors.get('rounding', {})) != ORIGINS
            or any(set(origin) != set(RECIPES) or any(set(row) != METRICS for row in origin.values())
                   for origin in errors['rounding'].values())):
        raise ValueError('rounding layer/origin/recipe/metric scope mismatch')


def audit_rounding_coefficients(model, report):
    """No inference: recheck every saved BN, both engines and coefficient bits."""
    # Selection/parameter matching is checked by the graph audits. Recheck all
    # saved modules rather than trusting an aggregate's selected subset.
    expected = {name: module for name, module in model.named_modules() if isinstance(module, nn.BatchNorm2d)}
    actual = {name: graph for name, graph in report['diagnostics']['operator_graphs'].items()
              if graph['original_operator'] == 'BatchNormalization'}
    if (list(actual) != list(expected) or report['protocol']['decision'] != 'ADR-020'
            or not expected):
        raise ValueError('rounding complete saved BN scope mismatch')
    for name, module in expected.items():
        validate_rounding_scope(report['protocol'], actual[name], report['diagnostics']['operators'][name])
        if actual[name]['rounding_coefficients'] != coefficient_records(module, coefficient_cache(module)):
            raise ValueError('rounding saved/coefficient bits mismatch')
    return {'notice': DIAGNOSTIC_NOTICE, 'status': 'PASS', 'layers': len(expected),
            'recipes_per_layer': len(RECIPES), 'engines': ['numpy', 'torch'],
            'saved_parameters_and_epsilon_bits': True, 'coefficient_reconstruction': True}


def main(argv=None):
    from .export_replay import main as replay_main
    return replay_main(argv, promoted=True, complete=True, rounding=True)


if __name__ == '__main__':
    raise SystemExit(main())
