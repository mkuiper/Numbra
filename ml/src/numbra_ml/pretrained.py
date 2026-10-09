"""Anonymous, revision/checksum-pinned ADR-005 checkpoint acquisition.

No hub client, credential lookup, pickle loading, or implicit model download.
The publisher declares Apache-2.0; this is not a warranty about image rights.
"""

import argparse
import hashlib
import json
from pathlib import Path
import sys
from urllib.request import urlopen

from . import PLACEHOLDER_NOTICE
from .prepare import repository_root

MODEL_NAME = "mobilenetv3_small_100.lamb_in1k"
REVISION = "1824797e7887cbec1990e4adbd6675960a36c589"
BASE_URL = f"https://huggingface.co/timm/{MODEL_NAME}/resolve/{REVISION}"
FILES = {
    "README.md": (4386, "3950face80991c4f91fb1ead491d787639e08a737f948fd630dd938ae8f78c18"),
    "config.json": (586, "07194b4b5f5140b0d1d1b80c49b6568b726c6e2f88858340cb7618061816b6e8"),
    "model.safetensors": (10241912, "46d2c063b18125884c48937afa4c49e18128869e52e8db96df48bf0a4d7ff697"),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def ignored_path(repo: Path, path: Path) -> Path:
    """Confine data/weight writes and inputs to this checkout's ignored data/."""
    path = path if path.is_absolute() else repo / path
    allowed = repo / "data"
    resolved = path.resolve()
    if allowed.is_symlink() or not resolved.is_relative_to(allowed) or resolved == allowed:
        raise ValueError("path must be below this repository's ignored data/ directory")
    return resolved


def verify_checkpoint(directory: Path) -> dict:
    for name, (size, digest) in FILES.items():
        path = directory / name
        if (not path.is_file() or path.is_symlink() or path.stat().st_size != size
                or sha256(path) != digest):
            raise ValueError(f"pinned pretrained file missing or checksum mismatch: {name}")
    if "license: apache-2.0" not in (directory / "README.md").read_text():
        raise ValueError("publisher licence declaration unavailable")
    return {"notice": PLACEHOLDER_NOTICE, "model": MODEL_NAME, "revision": REVISION,
            "publisher_declared_licence": "Apache-2.0", "url": BASE_URL,
            "files": {name: {"bytes": size, "sha256": digest}
                      for name, (size, digest) in FILES.items()},
            "warning": "ImageNet pretraining; no clinical training or image-rights warranty"}


def acquire(directory: Path) -> dict:
    """Fetch fixed public files; refuse corrupt existing files instead of replacing."""
    directory.mkdir(parents=True, exist_ok=True)
    # Verify the card/config before downloading any weights, even on a fresh run.
    for name, (size, digest) in FILES.items():
        path = directory / name
        if not path.exists():
            with urlopen(f"{BASE_URL}/{name}", timeout=60) as response:
                content = response.read(size + 1)
            if len(content) != size or hashlib.sha256(content).hexdigest() != digest:
                raise ValueError(f"download checksum mismatch: {name}")
            with path.open("xb") as stream:
                stream.write(content)
        if path.is_symlink() or path.stat().st_size != size or sha256(path) != digest:
            raise ValueError(f"existing pinned file checksum mismatch: {name}")
        if name == "README.md" and "license: apache-2.0" not in path.read_text():
            raise ValueError("publisher licence declaration unavailable")
    return verify_checkpoint(directory)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=PLACEHOLDER_NOTICE)
    parser.add_argument("--output", type=Path, default=Path("data/pretrained/mobilenetv3-small"))
    args = parser.parse_args(argv)
    try:
        directory = ignored_path(repository_root(), args.output)
        evidence = acquire(directory)
    except (ValueError, OSError) as exc:
        print(f"PLACEHOLDER checkpoint acquisition failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(evidence, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
