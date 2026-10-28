#!/usr/bin/env python3
"""Check this repository's files and examples using only the Python standard library.

This is a narrow structural check, not a full YAML/Markdown parser or an
assessment of a model's writing. Markdown checks cover simple inline and
reference links to local files; URL targets and heading fragments are ignored.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote


SKILL_PATH = Path("skills/ali-style")
REQUIRED_FILES = (
    SKILL_PATH / "SKILL.md",
    SKILL_PATH / "references/style-examples.md",
    SKILL_PATH / "agents/openai.yaml",
    SKILL_PATH / "assets/icon.svg",
)
IGNORED_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__"}
INLINE_LINK = re.compile(
    r"!?\[[^\]\n]*\]\(\s*(?:<([^>\n]+)>|([^\s()]+))"
    r"(?:\s+[\"'][^\n]*?[\"'])?\s*\)"
)
REFERENCE_LINK = re.compile(r"^\s{0,3}\[[^\]\n]+\]:\s*(?:<([^>\n]+)>|(\S+))", re.M)


def inside(path: Path, root: Path) -> bool:
    """Include symlink resolution when checking the allowed repository boundary."""
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def read_text(path: Path, root: Path, errors: list[str]) -> str | None:
    label = path.relative_to(root).as_posix()
    if not inside(path, root):
        errors.append(f"{label}: file resolves outside the repository")
        return None
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        errors.append(f"{label}: cannot read UTF-8 text ({exc})")
        return None


def simple_scalar(raw: str) -> str | None:
    """Read the plain/quoted one-line scalar forms used in this repository."""
    value = raw.strip()
    if value.startswith(("'", '"')):
        return value[1:-1].strip() if len(value) >= 2 and value[-1] == value[0] else None
    value = re.split(r"\s+#", value, maxsplit=1)[0].strip()
    if not value or value.startswith(("#", "[", "{")) or value in {"null", "~"}:
        return None
    return value


def check_frontmatter(text: str, errors: list[str]) -> None:
    label = "skills/ali-style/SKILL.md"
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        errors.append(f"{label}: frontmatter must start with ---")
        return
    try:
        end = lines.index("---", 1)
    except ValueError:
        errors.append(f"{label}: missing closing frontmatter delimiter ---")
        return
    fields: dict[str, str] = {}
    front = lines[1:end]
    for index, line in enumerate(front):
        match = re.match(r"^(name|description):\s*(.*)$", line)
        if not match:
            continue
        key, raw = match.groups()
        if key in fields:
            errors.append(f"{label}: duplicate frontmatter field {key}")
        value = simple_scalar(raw)
        if key == "description" and re.fullmatch(r"[>|][+-]?", raw.strip()):
            block = []
            for continuation in front[index + 1 :]:
                if continuation.strip() and not continuation.startswith((" ", "\t")):
                    break
                block.append(continuation.strip())
            value = " ".join(block).strip()
        fields[key] = value or ""
    name = fields.get("name", "")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) or len(name) > 64:
        errors.append(f"{label}: name must be a lowercase, hyphenated skill name")
    elif name != SKILL_PATH.name:
        errors.append(f"{label}: name must match directory name {SKILL_PATH.name!r}")
    if not fields.get("description", "").strip():
        errors.append(f"{label}: description must contain non-empty text")


def without_code_fences(text: str) -> str:
    output = []
    fence_character = ""
    fence_length = 0
    for line in text.splitlines():
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if fence_character:
            if marker and marker[1][0] == fence_character and len(marker[1]) >= fence_length and not marker[2].strip():
                fence_character = ""
            continue
        if marker:
            fence_character, fence_length = marker[1][0], len(marker[1])
            continue
        output.append(line)
    return "\n".join(output)


def check_markdown(path: Path, text: str, root: Path, errors: list[str]) -> None:
    text = without_code_fences(text)
    label = path.relative_to(root).as_posix()
    targets = [match[1] or match[2] for pattern in (INLINE_LINK, REFERENCE_LINK) for match in pattern.finditer(text)]
    for target in targets:
        if target.startswith(("#", "//")) or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
            continue
        local = unquote(target.split("#", 1)[0].split("?", 1)[0])
        if not local:
            continue
        destination = (root / local.lstrip("/")) if local.startswith("/") else path.parent / local
        if not inside(destination, root):
            errors.append(f"{label}: local link leaves the repository: {target}")
        elif not destination.exists():
            errors.append(f"{label}: local link target does not exist: {target}")


def check_icons(text: str, root: Path, errors: list[str]) -> None:
    label = "skills/ali-style/agents/openai.yaml"
    icons = list(re.finditer(r"^\s+(icon_small|icon_large):\s*(.*?)\s*$", text, re.M))
    if not icons:
        errors.append(f"{label}: expected at least one local icon reference")
    for icon in icons:
        value = simple_scalar(icon[2])
        if not value:
            errors.append(f"{label}: {icon[1]} must name a local file")
            continue
        destination = root / SKILL_PATH / value
        if not inside(destination, root / SKILL_PATH):
            errors.append(f"{label}: {icon[1]} leaves the skill directory")
        elif not destination.is_file():
            errors.append(f"{label}: {icon[1]} target does not exist: {value}")


def check_cases(text: str, errors: list[str]) -> None:
    label = "evals/cases.json"
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        errors.append(f"{label}: invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}")
        return
    if not isinstance(data, dict):
        errors.append(f"{label}: top level must be an object")
        return
    if type(data.get("schema_version")) is not int or data["schema_version"] != 1:
        errors.append(f"{label}: schema_version must be the integer 1")
    cases = data.get("cases")
    if not isinstance(cases, list) or not cases:
        errors.append(f"{label}: cases must be a non-empty array")
        return
    ids = set()
    for index, case in enumerate(cases, 1):
        location = f"{label}: case {index}"
        if not isinstance(case, dict):
            errors.append(f"{location} must be an object")
            continue
        for key in ("id", "category", "prompt"):
            if not isinstance(case.get(key), str) or not case[key].strip():
                errors.append(f"{location}: {key} must be a non-empty string")
        case_id = case.get("id")
        if isinstance(case_id, str) and case_id.strip():
            if case_id in ids:
                errors.append(f"{location}: duplicate id {case_id!r}")
            ids.add(case_id)
        if type(case.get("should_trigger")) is not bool:
            errors.append(f"{location}: should_trigger must be a JSON boolean")
        checks = case.get("checks")
        if not isinstance(checks, list) or not checks or any(not isinstance(item, str) or not item.strip() for item in checks):
            errors.append(f"{location}: checks must be a non-empty array of non-empty strings")
        if "machine_checks" in case:
            rules = case["machine_checks"]
            if not isinstance(rules, dict) or not rules:
                errors.append(f"{location}: machine_checks must be a non-empty object")
                continue
            unknown = set(rules) - {"max_chars", "required_literals"}
            if unknown:
                errors.append(f"{location}: unknown machine_checks: {', '.join(sorted(unknown))}")
            if "max_chars" in rules and (type(rules["max_chars"]) is not int or rules["max_chars"] <= 0):
                errors.append(f"{location}: max_chars must be a positive integer")
            if "required_literals" in rules:
                literals = rules["required_literals"]
                if not isinstance(literals, list) or not literals or any(not isinstance(item, str) or not item.strip() for item in literals):
                    errors.append(f"{location}: required_literals must be a non-empty array of non-empty strings")


def validate_repository(root: Path) -> list[str]:
    root = root.resolve()
    errors: list[str] = []
    if not root.is_dir():
        return [f"Repository root is not a directory: {root}"]
    for relative in REQUIRED_FILES:
        path = root / relative
        if not inside(path, root) or not path.is_file():
            errors.append(f"{relative.as_posix()}: required skill file is missing or outside the repository")
        elif path.stat().st_size == 0:
            errors.append(f"{relative.as_posix()}: required skill file is empty")
    skill_file = root / SKILL_PATH / "SKILL.md"
    if skill_file.is_file():
        text = read_text(skill_file, root, errors)
        if text is not None:
            check_frontmatter(text, errors)
    for path in sorted(root.rglob("*.md")):
        if any(part in IGNORED_DIRS for part in path.relative_to(root).parts):
            continue
        text = read_text(path, root, errors)
        if text is not None:
            check_markdown(path, text, root, errors)
    metadata = root / SKILL_PATH / "agents/openai.yaml"
    if metadata.is_file():
        text = read_text(metadata, root, errors)
        if text is not None:
            check_icons(text, root, errors)
    cases_path = root / "evals/cases.json"
    text = read_text(cases_path, root, errors)
    if text is not None:
        check_cases(text, errors)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1], help="repository root (defaults to this script's repository)")
    args = parser.parse_args()
    errors = validate_repository(args.root)
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        print(f"Repository validation failed: {len(errors)} problem(s).", file=sys.stderr)
        return 1
    print("Repository structure passed: skill files, basic metadata, local links, icons and evaluation case data.")
    print("Model responses and writing quality are not evaluated by this command.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
