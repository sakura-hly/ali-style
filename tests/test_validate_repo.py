"""Regression tests for practical repository packaging mistakes."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from validate_repo import validate_repository


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/validate_repo.py"


class RepositoryValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.write("skills/ali-style/SKILL.md", "---\nname: ali-style\ndescription: >-\n  改写中文素材。\n  保留原始事实。\n---\n# 阿里味\n[示例](references/style-examples.md#example)\n")
        self.write("skills/ali-style/references/style-examples.md", "# 示例\n")
        self.write("skills/ali-style/assets/icon.svg", '<svg xmlns="http://www.w3.org/2000/svg"/>\n')
        self.write("skills/ali-style/agents/openai.yaml", 'interface:\n  icon_small: "assets/icon.svg"\n  icon_large: assets/icon.svg\n')
        self.write("README.md", "# 示例仓库\n[技能](skills/ali-style/SKILL.md)\n[网页](https://example.com/missing)\n[页内](#section)\n[参考][skill]\n\n[skill]: skills/ali-style/SKILL.md\n\n```markdown\n[代码示例](missing-example.md)\n```\n")
        self.cases = {"schema_version": 1, "cases": [{"id": "progress-01", "category": "progress", "should_trigger": True, "prompt": "用阿里味改写：计划下周上线。", "checks": ["保留计划状态"]}]}
        self.save_cases()

    def write(self, name: str, text: str) -> None:
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def save_cases(self) -> None:
        self.write("evals/cases.json", json.dumps(self.cases, ensure_ascii=False))

    def errors(self) -> str:
        return "\n".join(validate_repository(self.root))

    def test_valid_bundle_and_cli(self) -> None:
        self.assertEqual(validate_repository(self.root), [])
        result = subprocess.run([sys.executable, str(SCRIPT), "--root", str(self.root)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("not evaluated", result.stdout)

    def test_missing_install_file_fails_cli(self) -> None:
        (self.root / "skills/ali-style/SKILL.md").unlink()
        self.assertIn("required skill file is missing", self.errors())
        result = subprocess.run([sys.executable, str(SCRIPT), "--root", str(self.root)], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("SKILL.md", result.stderr)

    def test_wrong_frontmatter_name_and_empty_description(self) -> None:
        self.write("skills/ali-style/SKILL.md", "---\nname: other-skill\ndescription: >-\n---\n# 示例\n")
        errors = self.errors()
        self.assertIn("name must match directory", errors)
        self.assertIn("description must contain non-empty text", errors)

    def test_broken_link_and_link_outside_repository(self) -> None:
        self.write("README.md", "[示例](docs/missing.md#section)\n[越界](../outside.md)\n")
        errors = self.errors()
        self.assertIn("local link target does not exist: docs/missing.md#section", errors)
        self.assertIn("local link leaves the repository", errors)

    def test_icon_path_is_relative_to_skill_root(self) -> None:
        self.write("skills/ali-style/agents/openai.yaml", "interface:\n  icon_small: assets/missing.svg\n")
        self.assertIn("icon_small target does not exist: assets/missing.svg", self.errors())

    def test_invalid_evaluation_case_data(self) -> None:
        self.cases["cases"].append(dict(self.cases["cases"][0]))
        self.cases["cases"][1]["should_trigger"] = "false"
        self.cases["cases"][1]["checks"] = []
        self.save_cases()
        errors = self.errors()
        self.assertIn("duplicate id", errors)
        self.assertIn("should_trigger must be a JSON boolean", errors)
        self.assertIn("checks must be a non-empty array", errors)


if __name__ == "__main__":
    unittest.main()
