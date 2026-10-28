#!/usr/bin/env python3
"""Create response records and report explicit checks without calling a model.

Exit codes: 0 = created (pending/unrun cases allowed), 1 = report contains a
recorded failure, 2 = invalid input or I/O error. Success is not a quality score.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path

from validate_repo import check_cases


DEFAULT_CASES = Path(__file__).resolve().parents[1] / "evals/cases.json"
METADATA_FIELDS = ("client", "model", "skill_revision", "date")
REVIEW_STATUSES = {"pending", "pass", "fail"}


def unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key!r}")
        result[key] = value
    return result


def load_json(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)
    if not isinstance(data, dict) or type(data.get("schema_version")) is not int or data["schema_version"] != 1:
        raise ValueError(f"{path}: expected an object with integer schema_version 1")
    return data


def load_cases(path: Path) -> list[dict]:
    data = load_json(path)
    errors: list[str] = []
    check_cases(json.dumps(data, ensure_ascii=False), errors)
    if errors:
        raise ValueError("; ".join(errors))
    return data["cases"]


def make_template(cases: list[dict], selected: list[str] | None = None) -> dict:
    ids = [case["id"] for case in cases]
    if selected is not None:
        if len(selected) != len(set(selected)):
            raise ValueError("Repeated --case IDs are not allowed")
        unknown = set(selected) - set(ids)
        if unknown:
            raise ValueError(f"Unknown case IDs: {', '.join(sorted(unknown))}")
    return {
        "schema_version": 1,
        "metadata": {**dict.fromkeys(METADATA_FIELDS), "explicit_skill_selection": None},
        "responses": [
            {"case_id": case_id, "output": "", "manual_review": {"status": "pending", "notes": ""}}
            for case_id in ids if selected is None or case_id in selected
        ],
    }


def validate_responses(data: dict, cases: list[dict]) -> dict[str, dict]:
    metadata = data.get("metadata")
    if not isinstance(metadata, dict):
        raise ValueError("metadata must be an object")
    for field in METADATA_FIELDS:
        if metadata.get(field) is not None and not isinstance(metadata[field], str):
            raise ValueError(f"metadata.{field} must be a string or null")
    explicit = metadata.get("explicit_skill_selection")
    if explicit is not None and type(explicit) is not bool:
        raise ValueError("metadata.explicit_skill_selection must be a boolean or null")
    if not isinstance(data.get("responses"), list):
        raise ValueError("responses must be an array")
    known = {case["id"] for case in cases}
    records = {}
    for index, record in enumerate(data["responses"], 1):
        if not isinstance(record, dict) or not isinstance(record.get("case_id"), str):
            raise ValueError(f"response {index}: expected an object with string case_id")
        case_id = record["case_id"]
        if case_id not in known:
            raise ValueError(f"Unknown response case_id: {case_id!r}")
        if case_id in records:
            raise ValueError(f"Duplicate response case_id: {case_id!r}")
        if not isinstance(record.get("output", ""), str):
            raise ValueError(f"{case_id}: output must be a string")
        review = record.get("manual_review", {})
        if not isinstance(review, dict) or not isinstance(review.get("status", "pending"), str) or review.get("status", "pending") not in REVIEW_STATUSES:
            raise ValueError(f"{case_id}: manual_review.status must be pending, pass or fail")
        if not isinstance(review.get("notes", ""), str):
            raise ValueError(f"{case_id}: manual_review.notes must be a string")
        records[case_id] = record
    return records


def mechanical_checks(output: str, rules: dict) -> list[tuple[bool, str]]:
    """Count Unicode code points except CR/LF; literal matching is exact."""
    results = []
    if "max_chars" in rules:
        count = len(output.replace("\r", "").replace("\n", ""))
        results.append((count <= rules["max_chars"], f"字符数 {count} / 上限 {rules['max_chars']}"))
    for literal in rules.get("required_literals", []):
        results.append((literal in output, f"原样包含：{literal}"))
    return results


def inline(value: object) -> str:
    """Escape untrusted metadata, IDs and check descriptions in Markdown."""
    text = html.escape(str(value), quote=False).replace("\r", " ").replace("\n", " ")
    text = re.sub(r"([\\`*_{}\[\]()#+.!-])", r"\\\1", text)
    return text.replace("|", "&#124;")


def code_block(text: str) -> str:
    # A longer fence prevents output containing Markdown fences from escaping.
    length = max([2] + [len(run) for run in re.findall(r"`+", text)]) + 1
    fence = "`" * length
    return f"{fence}text\n{text}\n{fence}"


def build_report(cases: list[dict], data: dict) -> tuple[str, bool]:
    records = validate_responses(data, cases)
    rows = []
    for case in cases:
        record = records.get(case["id"], {})
        output = record.get("output", "")
        ran = bool(output.strip())
        checks = mechanical_checks(output, case.get("machine_checks", {})) if ran else []
        auto = ("FAIL" if any(not ok for ok, _ in checks) else "PASS") if checks else "NO CHECKS"
        manual = record.get("manual_review", {}).get("status", "pending").upper()
        rows.append({"case": case, "record": record, "output": output, "ran": ran,
                     "checks": checks, "auto": auto if ran else "NOT RUN", "manual": manual if ran else "NOT RUN"})
    recorded = sum(row["ran"] for row in rows)
    failed = sum(row["auto"] == "FAIL" or row["manual"] == "FAIL" for row in rows)
    lines = [
        "# 阿里味输出评估记录", "",
        "本工具不调用模型。机械检查只核对已声明的字数和原样文本；人工结果来自记录者填写，未经工具独立核实。",
        "机械检查通过不代表事实准确、语气合适或客户端自动触发已经验证。未运行与待复核均不计为通过。", "",
        "## 运行信息", "", "以下信息由记录者填写；空项表示未记录。", "",
    ]
    for field in (*METADATA_FIELDS, "explicit_skill_selection"):
        value = data["metadata"].get(field)
        label = "未记录" if value is None or value == "" else str(value).lower() if type(value) is bool else value
        lines.append(f"- {field}: {inline(label)}")
    lines += ["", "## 覆盖情况", "", f"- 案例总数：{len(rows)}；已记录非空输出：{recorded}；NOT RUN：{len(rows) - recorded}。"]
    lines.append("- 机械检查：" + "；".join(f"{status} {sum(row['auto'] == status for row in rows)}" for status in ("PASS", "FAIL", "NO CHECKS")) + "。")
    lines.append("- 人工复核：" + "；".join(f"{status} {sum(row['manual'] == status for row in rows)}" for status in ("PASS", "FAIL", "PENDING")) + "。")
    lines += [f"- 有记录失败的案例：{failed}。", "", "| 案例 | 输出 | 机械检查 | 人工复核 |", "| --- | --- | --- | --- |"]
    for row in rows:
        lines.append(f"| {inline(row['case']['id'])} | {'RECORDED' if row['ran'] else 'NOT RUN'} | {row['auto']} | {row['manual']} |")
    lines += ["", "字符数按 Unicode 码点计算，标点、空格和制表符计入，CR/LF 不计；组合字符与 emoji 可能占多个码点。",
              "原样文本检查区分大小写，不合并或删除空白，不转换全角、半角或 Unicode 形式。NO CHECKS 表示该案例未配置机械规则。", ""]
    for row in rows:
        case, record = row["case"], row["record"]
        lines += [f"## {inline(case['id'])}", "",
                  f"分类：{inline(case['category'])}；预期触发：{str(case['should_trigger']).lower()}（案例期望，不是触发观测结果）。", "",
                  "### 原始请求", "", code_block(case["prompt"]), "", "### 输出", ""]
        lines += [code_block(row["output"])] if row["ran"] else ["NOT RUN：没有记录非空输出。"]
        review = record.get("manual_review", {})
        if not row["ran"] and review.get("status", "pending") != "pending":
            lines += ["", "已填写的人工结论未计入统计，因为没有可复核的输出。"]
        lines += ["", f"机械检查：{row['auto']}；人工复核：{row['manual']}。", ""]
        lines += [f"- {'PASS' if ok else 'FAIL'}：{inline(message)}" for ok, message in row["checks"]]
        lines += ["", "### 人工检查项", ""] + [f"- {inline(item)}" for item in case["checks"]]
        if review.get("notes", ""):
            lines += ["", "### 复核备注", "", code_block(review["notes"])]
        lines.append("")
    return "\n".join(lines), bool(failed)


def write_output(path: Path, text: str, force: bool, sources: list[Path]) -> None:
    if path.resolve() in {source.resolve() for source in sources}:
        raise ValueError("Output must not overwrite a cases or responses input file")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w" if force else "x", encoding="utf-8", newline="\n") as stream:
        stream.write(text)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subcommands = parser.add_subparsers(dest="command", required=True)
    for name, help_text in (("template", "Create blank records; does not run a model"), ("report", "Report saved outputs; does not run a model")):
        command = subcommands.add_parser(name, help=help_text, epilog=__doc__)
        command.add_argument("--cases", type=Path, default=DEFAULT_CASES, help="case JSON (default: repository evals/cases.json)")
        command.add_argument("--output", type=Path, required=True, help="destination; existing files are preserved by default")
        command.add_argument("--force", action="store_true", help="replace an existing output file")
        if name == "template":
            command.add_argument("--case", dest="case_ids", action="append", help="include this case ID; repeat to select several")
        else:
            command.add_argument("--responses", type=Path, required=True, help="response record JSON")
    args = parser.parse_args(argv)
    try:
        cases = load_cases(args.cases)
        sources = [args.cases]
        failed = False
        if args.command == "template":
            content = json.dumps(make_template(cases, args.case_ids), ensure_ascii=False, indent=2) + "\n"
        else:
            sources.append(args.responses)
            content, failed = build_report(cases, load_json(args.responses))
        write_output(args.output, content, args.force, sources)
    except (OSError, ValueError, UnicodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(f"Created {args.output}. No model was called.")
    if args.command == "report":
        print("Recorded failures found." if failed else "No recorded failures; pending or unrun cases may remain.")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
