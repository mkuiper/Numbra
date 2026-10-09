# ADR-020 — Complete PLACEHOLDER BatchNorm coefficient-rounding replay

Date: 2026-10-10

Status: Accepted (autopilot) — pending human review

## Context

ADR-019 finds local native arithmetic differences at every saved BN and most
Conv layers. Both promoted BN expressions reproduce their specified Python
formula but fail to reproduce native BN. Every baseline export remains rejected;
ADR-012's labelled toy diagnostic workaround remains in force.

## Decision — declared before execution

Replay all saved BNs in module order, matched one-to-one against the preserved
ONNX graph using ADR-019's exact parameter/geometry validation. Use all and only
152 ordered training component index images on both exact native Python inputs
and preserved-ORT inputs. Copy pre-activation boundaries before in-place timm
activations. Check native replay and tapped/original logits; retain original
saved weights, fitted scaling/head, temperature, threshold and ADR-011 budgets.

Predeclare the complete Cartesian product of these five binary rounding choices
(32 recipes, no favourable subset or adaptive recipe additions):

1. Epsilon sum: `e32` = float32(var + float32(eps)); `e64` =
   float64(var) + float64(saved Python eps).
2. Reciprocal: `r32` = float32(1 / float32(sqrt(float32(sum))));
   `r64` = 1 / sqrt(float64(sum)), retaining float64.
3. Alpha: `a32` = float32(weight * float32(reciprocal));
   `a64` = float32(float64(weight) * float64(reciprocal)).
4. Beta: `b32` = float32(bias - float32(mean * alpha));
   `b64` = float32(float64(bias) - float64(mean) * float64(alpha)).
5. Output: `o32` = float32(float32(x * alpha) + beta);
   `o64` = float32(float64(x) * float64(alpha) + float64(beta)).

All saved tensors retain their original float32 bits. The recipes may collapse
to identical arithmetic for some choices; report them all. `o64` is a rounded
float64 diagnostic, not a claim to implement a hardware float32 FMA. Implement
expressions independently in NumPy and eager PyTorch; record coefficient bits,
epsilon bits, expression disagreement and both native-relative errors rather
than presuming the engines' square roots are identical. This is a hypothesis
experiment, not an assertion about the native kernel's implementation.

Audit complete recipe/origin/layer/component scope, reconstruct aggregates from
ignored ordered details, recheck coefficient and saved-state bits, graph hashes,
source/dependency provenance, and exact prior preserved-control logits. No new
quantisation fit, frozen test/held-out/stress inference, full-model replacement,
reference/budget change or deployment selection. Tapped graphs and all results
are **PLACEHOLDER diagnostic only, never bundle**. Exit 0 means diagnostic evidence
was written; M4 remains incomplete regardless of any locally matching recipe.

## Consequences

This bounded experiment addresses coefficient rounding only. It does not fix
Conv kernel drift, establish whole-model parity, select quantisation scope, or
prove mobile operator support/performance. A separately predeclared candidate
and unchanged full acceptance checks are necessary before bundling.

## Observed follow-through — 2026-10-09 UTC

[Complete aggregate evidence](../ml/reports/PLACEHOLDER-m4-bn-rounding2.json)
retains all 152 ordered training components, every saved 34 BN and all 32
recipes on both origins. The unchanged native/primitive/promoted controls still
cover 53 Conv/34 BN and 517 serialized/runtime graph records. All coefficient,
aggregate and runtime audits pass; saved state is unchanged. The independent
no-inference audit rechecks saved model/preparation/retained/source provenance,
coefficient reconstruction, ordered IDs, exact prior ADR-019 ordered logits and
all prior per-operator metrics, and exact preserved-control parity.

Both `e32-r32-a32-b64-o64` and `e32-r32-a64-b64-o64` match native Python exactly
at all 34 BNs, on both origins across every tested training input, in both
NumPy and eager PyTorch. These recipes use the float32 epsilon sum and
square-root/reciprocal, round beta from double arithmetic and round the double
output affine expression once. Their alpha choices collapse on these parameters.
The corresponding e64/r32 recipes match 23/34 layers; remaining 28 recipes match
no layer across all tested inputs. All 32 recipes' NumPy/PyTorch output errors
are zero at all layers on both origins. Float64 reciprocal bits nevertheless
differ at 23 (e32/r64) or 19 (e64/r64) BNs; these differences do not change the
observed rounded float32 coefficients/outputs. All recipes remain reported.

The initial run was deliberately interrupted before a report was written after
spotting that sorted JSON dictionaries cannot encode module order. The corrected
audit uses the explicit selection list, with a regression. Original partial
graphs/logs remain ignored. No complete-model replacement, quantisation fit,
frozen inference or deployment selection occurred. Preserved control still FAILS
ADR-011: raw/probability maxima 0.000240326/0.00000279320, 26/29 violations, zero
flips. The first full check passed 419 tests; after the order correction the
fresh full check passed 419 tests in 77.60s. M4 remains incomplete.

Next predeclare a single all-BN `e32-r32-a32-b64-o64` candidate and unchanged
preserved control for training-only whole-model testing, auditing every saved
coefficient and actual runtime Cast/Mul/Add expression. No favourable layer
subset or changed reference/budget; local agreement does not prove unseen-input
or whole-model agreement. Conv drift, selective QDQ and mobile double arithmetic
support/performance remain unresolved before acceptance/bundling.

## Open questions

- Does any declared recipe reproduce native BN across every tested layer/input?
- Can local arithmetic findings motivate a finite deployable conversion strategy?
- Do humans accept continued diagnostic work while M4 remains blocked?

## Confidence

High for the tested finite training-only protocol and observed local agreement.
Whole-model parity, mobile execution and clinical validity remain unverified.
