"""Research-stage checks; no patient data or third-party dependencies required."""

from pathlib import Path
import re
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


def builder_markdown_files():
    # Include new Builder documents before staging, but never installed packages
    # or generated output. The previous rglob walked ignored ml/.venv wheels.
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z", "--", "*.md"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    )
    folders = {"docs", "research", "decisions", "ml", "app", "reviews"}
    return sorted({ROOT / name for name in result.stdout.split("\0") if name and
                   (name in {"README.md", "AGENTS.md"} or Path(name).parts[0] in folders)})


class RepositoryContractTests(unittest.TestCase):
    def test_sensitive_and_generated_paths_are_ignored(self):
        paths = [
            "data/raw/example/image.jpg",
            "data/manifests/example.jsonl",
            ".firecrawl/page.md",
            "ml/.venv/bin/python",
            "tests/.tmp/generated.png",
            "ml/tests/.tmp/fixture.jsonl",
            "ml/output/model.pt",
            "ml/output/model.safetensors",
            "ml/output/model.tflite",
            "app/local.properties",
            "app/build/outputs/apk/debug/app-debug.apk",
            ".env",
            ".env.local",
            "app/signing.jks",
            "credentials/private.key",
        ]
        for path in paths:
            with self.subTest(path=path):
                result = subprocess.run(
                    ["git", "check-ignore", "--no-index", "-q", path],
                    cwd=ROOT,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, path)

    def test_no_data_directory_files_are_tracked(self):
        result = subprocess.run(
            ["git", "ls-files", "--", "data/"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertEqual(result.stdout, "", "Patient data must never be tracked")

    def test_builder_markdown_local_links_resolve(self):
        for file in builder_markdown_files():
            # Protected harness/reviewer files have their own independent ownership.
            if file.name.startswith(("REVIEW-", "CHECK-", "GATE")):
                continue
            if file.name in {"ROADMAP.md", "AUTOPILOT.md"}:
                continue
            for target in re.findall(r"(?<!!)\[[^\]]+\]\(([^\s)]+)\)", file.read_text()):
                if "://" in target or target.startswith("#"):
                    continue
                with self.subTest(file=str(file.relative_to(ROOT)), target=target):
                    self.assertTrue((file.parent / target.split("#")[0]).exists())

    def test_builder_markdown_discovery_keeps_new_docs_and_excludes_installed_files(self):
        ignored = ROOT / 'ml/.tmp'
        ignored.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=ROOT / 'docs', prefix='contract-fixture-') as builder_dir:
            with tempfile.TemporaryDirectory(dir=ignored) as ignored_dir:
                builder = Path(builder_dir) / 'new-builder.md'
                third_party = Path(ignored_dir) / 'third-party.md'
                # A broken Builder link must still enter the normal check. A
                # broken link in ignored dependencies must not change its scope.
                for file in (builder, third_party):
                    file.write_text('[broken](does-not-exist.md)')
                files = builder_markdown_files()
                self.assertIn(builder, files)
                self.assertNotIn(third_party, files)
                self.assertIn(ROOT / 'docs/ML-EXPORT.md', files)

    def test_research_documents_keep_uncertainty_sections(self):
        for file in (ROOT / "research").glob("[0-9][0-9]-*.md"):
            with self.subTest(file=file.name):
                content = file.read_text()
                self.assertIn("## Open questions", content)
                self.assertIn("## Confidence", content)
                self.assertLess(content.index("## Open questions"), content.index("## Confidence"))
                self.assertRegex(content, r"https://[^\s)]+")

    def test_builder_research_citations_have_source_register_entries(self):
        # Evidence bookkeeping, not a validation of the source's factual claims.
        url_pattern = r"https?://[^\s)]+"
        registered = set(re.findall(url_pattern, (ROOT / "research/sources.md").read_text()))
        for folder in ("research", "docs", "decisions"):
            for file in (ROOT / folder).glob("*.md"):
                if file.name in {"sources.md", "ROADMAP.md", "AUTOPILOT.md"}:
                    continue
                for url in set(re.findall(url_pattern, file.read_text())):
                    with self.subTest(file=str(file.relative_to(ROOT)), source=url):
                        self.assertIn(url, registered, "Add source evidence and access limits")


if __name__ == "__main__":
    unittest.main()
