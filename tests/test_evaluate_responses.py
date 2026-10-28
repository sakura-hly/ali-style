"""Tests for trustworthy bookkeeping of saved model responses."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from evaluate_responses import build_report, load_cases, make_template, mechanical_checks


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/evaluate_responses.py"


class ResponseEvaluationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.cases = [
            {"id": "short", "category": "format", "should_trigger": True, "prompt": "三字以内：计划上线。", "checks": ["保留计划状态"], "machine_checks": {"max_chars": 3, "required_literals": ["计划"]}},
            {"id": "manual", "category": "meaning", "should_trigger": True, "prompt": "改写进度。", "checks": ["保留进度"]},
        ]
        self.cases_path = self.root / "cases.json"
        self.save(self.cases_path, {"schema_version": 1, "cases": self.cases})

    def save(self, path: Path, value: object) -> None:
        path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")

    def run_cli(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)

    def report_cli(self, data: dict) -> subprocess.CompletedProcess:
        responses = self.root / "responses.json"
        self.save(responses, data)
        return self.run_cli("report", "--cases", str(self.cases_path), "--responses", str(responses), "--output", str(self.root / "report.md"), "--force")

    def test_template_subset_and_no_overwrite(self) -> None:
        output = self.root / "records.json"
        args = ("template", "--cases", str(self.cases_path), "--case", "manual", "--output", str(output))
        result = self.run_cli(*args)
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual([row["case_id"] for row in data["responses"]], ["manual"])
        self.assertIsNone(data["metadata"]["explicit_skill_selection"])
        original = output.read_bytes()
        self.assertEqual(self.run_cli(*args).returncode, 2)
        self.assertEqual(output.read_bytes(), original)
        self.assertEqual(self.run_cli(*args, "--force").returncode, 0)
        with self.assertRaisesRegex(ValueError, "Unknown case"):
            make_template(self.cases, ["absent"])

    def test_missing_blank_and_pending_are_not_passes(self) -> None:
        data = make_template(self.cases, ["short"])
        data["responses"][0].update(output=" \r\n\t", manual_review={"status": "pass"})
        report, failed = build_report(self.cases, data)
        self.assertFalse(failed)
        self.assertIn("已记录非空输出：0；NOT RUN：2", report)
        self.assertIn("人工复核：PASS 0；FAIL 0；PENDING 0", report)
        self.assertIn("已填写的人工结论未计入统计", report)
        data["responses"][0]["output"] = "计划"
        data["responses"][0]["manual_review"] = {"status": "pending"}
        report, failed = build_report(self.cases, data)
        self.assertFalse(failed)
        self.assertIn("| short | RECORDED | PASS | PENDING |", report)
        self.assertIn("| manual | NOT RUN | NOT RUN | NOT RUN |", report)

    def test_failures_are_reported_and_cli_returns_one(self) -> None:
        data = make_template(self.cases)
        data["responses"][0]["output"] = "已经上线啦"
        data["responses"][1].update(output="主导整体改造。", manual_review={"status": "fail", "notes": "原文只有参与。"})
        result = self.report_cli(data)
        self.assertEqual(result.returncode, 1, result.stderr)
        report = (self.root / "report.md").read_text(encoding="utf-8")
        self.assertIn("有记录失败的案例：2", report)
        self.assertIn("| manual | RECORDED | NO CHECKS | FAIL |", report)
        self.assertIn("字符数 5 / 上限 3", report)
        self.assertIn("FAIL：原样包含：计划", report)

    def test_duplicate_unknown_and_malformed_responses_fail(self) -> None:
        base = make_template(self.cases)
        duplicate = copy.deepcopy(base)
        duplicate["responses"].append(duplicate["responses"][0])
        unknown = copy.deepcopy(base)
        unknown["responses"][0]["case_id"] = "missing"
        malformed = copy.deepcopy(base)
        malformed["responses"][0]["output"] = False
        bad_metadata = copy.deepcopy(base)
        bad_metadata["metadata"]["explicit_skill_selection"] = "false"
        bad_review = copy.deepcopy(base)
        bad_review["responses"][0]["manual_review"]["status"] = []
        bad_version = copy.deepcopy(base)
        bad_version["schema_version"] = True
        for data in (duplicate, unknown, malformed, bad_metadata, bad_review, bad_version):
            with self.subTest(data=data):
                self.assertEqual(self.report_cli(data).returncode, 2)

    def test_case_rules_reject_boolean_limits_and_unknown_rules(self) -> None:
        for rules in ({"max_chars": True}, {"max_chars": 0}, {"required_literals": [""]}, {"minimum_chars": 2}):
            with self.subTest(rules=rules):
                cases = copy.deepcopy(self.cases)
                cases[0]["machine_checks"] = rules
                self.save(self.cases_path, {"schema_version": 1, "cases": cases})
                with self.assertRaises(ValueError):
                    load_cases(self.cases_path)

    def test_unicode_count_and_literal_whitespace_are_exact(self) -> None:
        result = mechanical_checks("计\r\n划 😀e\u0301", {"max_chars": 6, "required_literals": ["计划", "计\r\n划"]})
        self.assertTrue(result[0][0])  # Two Chinese + space + emoji + e + combining accent.
        self.assertIn("字符数 6", result[0][1])
        self.assertFalse(result[1][0])  # Literal matching does not remove line endings.
        self.assertTrue(result[2][0])

    def test_output_fences_and_metadata_cannot_escape_markdown(self) -> None:
        data = make_template(self.cases)
        data["metadata"]["client"] = "<img src=x onerror=alert(1)>|[click](https://example.com)\n# heading"
        output = "```\n<script>alert(1)</script>\n| x |\n````\n# heading"
        data["responses"][0]["output"] = output
        report, _ = build_report(self.cases, data)
        self.assertIn("&lt;img", report)
        self.assertIn("&#124;\\[click\\]", report)
        self.assertIn("`````text\n" + output + "\n`````", report)
        self.assertNotIn("\n# heading\n```\n", report)

    def test_json_duplicate_keys_and_input_overwrite_fail(self) -> None:
        responses = self.root / "responses.json"
        responses.write_text('{"schema_version":1,"schema_version":1,"metadata":{},"responses":[]}', encoding="utf-8")
        result = self.run_cli("report", "--cases", str(self.cases_path), "--responses", str(responses), "--output", str(self.root / "report.md"))
        self.assertEqual(result.returncode, 2)
        self.assertIn("Duplicate JSON key", result.stderr)
        original = self.cases_path.read_bytes()
        result = self.run_cli("template", "--cases", str(self.cases_path), "--output", str(self.cases_path), "--force")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(self.cases_path.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
