"""Research-stage checks; no patient data or third-party dependencies required."""

from pathlib import Path
import re
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]


class RepositoryContractTests(unittest.TestCase):
    def test_sensitive_and_generated_paths_are_ignored(self):
        paths = [
            "data/raw/example/image.jpg",
            "data/manifests/example.jsonl",
            ".firecrawl/page.md",
            "ml/.venv/bin/python",
            "ml/output/model.pt",
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
        files = [ROOT / "README.md", ROOT / "AGENTS.md"]
        for folder in ("docs", "research", "decisions", "ml", "app", "reviews"):
            files.extend((ROOT / folder).rglob("*.md"))
        for file in files:
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

    def test_research_documents_keep_uncertainty_sections(self):
        for file in (ROOT / "research").glob("[0-9][0-9]-*.md"):
            with self.subTest(file=file.name):
                content = file.read_text()
                self.assertIn("## Open questions", content)
                self.assertIn("## Confidence", content)
                self.assertLess(content.index("## Open questions"), content.index("## Confidence"))
                self.assertRegex(content, r"https://[^\s)]+")


if __name__ == "__main__":
    unittest.main()
