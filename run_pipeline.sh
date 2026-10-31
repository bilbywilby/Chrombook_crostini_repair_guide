#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

echo "=== Running Crostini Repair Guide validation ==="

python3 - <<'PY'
from pathlib import Path
import re
import unittest
from urllib.parse import unquote, urlsplit

ROOT = Path.cwd().resolve()
README = ROOT / "README.md"
INLINE_LINK = re.compile(
    r"""!?\[[^\]]*\]\(\s*(?:<([^>]+)>|([^\s)]+))"""
)


class RepositoryChecks(unittest.TestCase):
    def test_readme_exists(self):
        self.assertTrue(README.is_file(), "README.md must exist.")

    def test_readme_title_or_frontmatter(self):
        content = README.read_text(encoding="utf-8")
        lines = content.splitlines()

        if lines and lines[0] == "---":
            closing = next(
                (
                    index
                    for index, line in enumerate(lines[1:], start=1)
                    if line in ("---", "...")
                ),
                None,
            )
            self.assertIsNotNone(
                closing,
                "README frontmatter must have a closing delimiter.",
            )

            try:
                import yaml
            except ImportError as exc:
                self.fail(
                    "README uses YAML frontmatter, but PyYAML is unavailable. "
                    "Install it in the active Python environment. "
                    f"Details: {exc}"
                )

            metadata = yaml.safe_load("\n".join(lines[1:closing]))
            self.assertIsInstance(
                metadata,
                dict,
                "README frontmatter must be a YAML mapping.",
            )
        else:
            first_content_line = next(
                (line for line in lines if line.strip()),
                "",
            )
            self.assertTrue(
                first_content_line.startswith("#"),
                "README must start with a Markdown heading or YAML frontmatter.",
            )

    def test_readme_local_inline_links_resolve(self):
        content = README.read_text(encoding="utf-8")

        for match in INLINE_LINK.finditer(content):
            raw_target = match.group(1) or match.group(2)
            parsed = urlsplit(raw_target)

            if parsed.scheme or parsed.netloc:
                continue  # External URLs are not checked for availability.

            target_path = unquote(parsed.path)
            candidate = (
                ROOT / target_path.lstrip("/")
                if target_path.startswith("/")
                else README.parent / target_path
            ).resolve()

            with self.subTest(target=raw_target):
                try:
                    candidate.relative_to(ROOT)
                except ValueError:
                    self.fail(f"README link escapes the repository: {raw_target}")

                self.assertTrue(
                    candidate.exists(),
                    f"README link target does not exist: {raw_target}",
                )

    def test_required_project_files_exist(self):
        for filename in ("SKILL.md", "build_wiki.py"):
            with self.subTest(filename=filename):
                self.assertTrue(
                    (ROOT / filename).is_file(),
                    f"{filename} must exist.",
                )


if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(RepositoryChecks)
    )
    if not result.wasSuccessful():
        raise SystemExit(1)
PY

python3 -m unittest discover -s tests -v
python3 build_wiki.py
tar -tzf crostini-repair-guide-wiki.tar.gz >/dev/null
sha256sum crostini-repair-guide-wiki.tar.gz
git diff --check
git diff --cached --check
git status --short

echo "=== Pipeline verification complete ==="
