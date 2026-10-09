"""Local PLACEHOLDER source snapshots, never historical inference authentication."""

import hashlib
import re
import subprocess

from .train import json_text


def checked_file(root, relative):
    path = root / relative
    if (root.is_symlink() or path.resolve() != path.absolute() or not path.is_file()
            or path.is_symlink() or path.parent.is_symlink()):
        raise ValueError('PLACEHOLDER missing/unsafe evidence file')
    return path


def checkout_context(repo, recorded):
    commit = recorded.get('git_commit')
    if (not isinstance(commit, str) or not re.fullmatch(r'[0-9a-f]{40}', commit)
            or type(recorded.get('git_dirty')) is not bool
            or subprocess.run(['git', 'cat-file', '-e', commit + '^{commit}'], cwd=repo,
                              capture_output=True).returncode):
        raise ValueError('PLACEHOLDER invalid recorded checkout context')


def audit_environment(repo, recorded, current, *, source_commit=None):
    """Keep live dependency checks; optionally bind old code to one exact commit.

    A report written with dirty code can be committed subsequently. The caller
    must supply that full local commit explicitly. No source fields are removed
    or rewritten, and historical logits are not authenticated by this check.
    """
    checkout_context(repo, recorded)
    source_keys = ('source_files_sha256', 'source_tree_sha256')
    dependency_keys = ('dependencies', 'dependency_lock_sha256', 'export_dependency_lock_sha256')
    for key in dependency_keys:
        if recorded[key] != current[key]:
            raise ValueError('PLACEHOLDER source/dependency provenance mismatch')
    if source_commit is None:
        if any(recorded[key] != current[key] for key in source_keys):
            raise ValueError('PLACEHOLDER source/dependency provenance mismatch')
        return {'notice': 'PLACEHOLDER source provenance only', 'status': 'PASS',
                'source': 'current code', 'live_dependencies_exact': True}
    if (not isinstance(source_commit, str) or not re.fullmatch(r'[0-9a-f]{40}', source_commit)
            or subprocess.run(['git', 'cat-file', '-e', source_commit + '^{commit}'],
                              cwd=repo, capture_output=True).returncode):
        raise ValueError('PLACEHOLDER invalid source snapshot commit')
    names = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', source_commit,
                                     '--', 'ml/src/numbra_ml'], cwd=repo, text=True).splitlines()
    names = sorted(name for name in names if re.fullmatch(r'ml/src/numbra_ml/[^/]+\.py', name))
    code = {name: hashlib.sha256(subprocess.check_output(
        ['git', 'show', source_commit + ':' + name], cwd=repo)).hexdigest() for name in names}
    if (not code or code != recorded['source_files_sha256']
            or hashlib.sha256(json_text(code).encode()).hexdigest() != recorded['source_tree_sha256']):
        raise ValueError('PLACEHOLDER complete historical source snapshot mismatch')
    return {'notice': 'PLACEHOLDER source provenance only', 'status': 'PASS',
            'source': 'exact local commit snapshot', 'source_commit': source_commit,
            'source_files': len(code), 'live_dependencies_exact': True,
            'historical_inference_authentication': False}
