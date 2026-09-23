"""Generate the schema reference and check staged Python using Ruff (no runtime deps)."""

import argparse
import html
import json
import subprocess
import sys
from pathlib import Path

SCHEMA = "schemas/dataset-metadata.schema.json"
REFERENCE = "DATASET-METADATA-REFERENCE.md"


def cell(value: str) -> str:
    return html.escape(value, quote=False).replace("|", "&#124;").replace("\n", "<br>")


def render(schema: dict) -> str:
    """Document reachable properties; expand scalar refs, link shared object shapes once."""
    sections = [("Dataset", schema, "jstat")]
    references = {}

    def resolve(node: dict, seen: tuple = ()) -> dict:
        if not isinstance(node, dict):
            return {} if node else {"description": "Not allowed."}
        if "$ref" not in node:
            return node
        reference = node["$ref"]
        if not reference.startswith("#/") or reference in seen:
            raise ValueError(
                f"Unsupported external or cyclic alias reference: {reference}"
            )
        target = schema
        for part in reference[2:].split("/"):
            target = target[part.replace("~1", "/").replace("~0", "~")]
        return resolve(target, (*seen, reference)) | {
            key: value for key, value in node.items() if key != "$ref"
        }

    def types(node: dict, seen: tuple = ()) -> str:
        if node.get("$ref") in seen:
            return "object"
        seen = (*seen, node.get("$ref")) if "$ref" in node else seen
        node = resolve(node)
        alternatives = node.get("oneOf", node.get("anyOf", []))
        if "type" not in node and alternatives:
            return " / ".join(dict.fromkeys(types(item, seen) for item in alternatives))
        values = node.get("type")
        if values is None:
            if "const" in node:
                value = node["const"]
                values = {
                    str: "string",
                    bool: "boolean",
                    int: "integer",
                    float: "number",
                    list: "array",
                    dict: "object",
                    type(None): "null",
                }[type(value)]
            else:
                values = "object" if "properties" in node else "any"
        values = [values] if isinstance(values, str) else values
        result = []
        for value in values:
            if value == "array" and isinstance(node.get("items"), dict):
                value = f"array<{types(node['items'], seen)}>"
            result.append(value)
        return " / ".join(result)

    def children(node: dict, prefix: str, source: str) -> list[str]:
        node = resolve(node)
        rows = []
        properties = dict(node.get("properties", {}))
        required = set(node.get("required", []))
        for keyword in ("allOf", "anyOf", "oneOf"):
            branches = [resolve(branch) for branch in node.get(keyword, [])]
            for branch in branches:
                for name, definition in branch.get("properties", {}).items():
                    properties.setdefault(name, definition)
            groups = [set(branch.get("required", [])) for branch in branches]
            if groups:
                required.update(
                    set.union(*groups)
                    if keyword == "allOf"
                    else set.intersection(*groups)
                )
        for name, definition in properties.items():
            path = f"{prefix}.{name}" if prefix else name
            origin = "nordicintel" if name == "nordicintel" else source
            rows.extend(property_rows(path, definition, name in required, origin))
        # Dynamic keys are useful only when their values have documented structure.
        dynamic = list(node.get("patternProperties", {}).values())
        if isinstance(node.get("additionalProperties"), dict):
            dynamic.append(node["additionalProperties"])
        for index, definition in enumerate(dynamic):
            path = f"{prefix}.{{key}}" if prefix else "{key}"
            if len(dynamic) > 1:
                path += f"[{index + 1}]"
            origin = "nordicintel" if "nordicintel" in properties else source
            rows.extend(nested(definition, path, origin))
        if isinstance(node.get("items"), dict):
            rows.extend(nested(node["items"], prefix + "[]", source))
        return rows

    def nested(definition: dict, path: str, source: str) -> list[str]:
        target = resolve(definition)
        if "$ref" in definition and target.get("properties"):
            return property_rows(path, definition, False, source)
        return children(target, path, source)

    def property_rows(
        path: str, definition: dict, required: bool, source: str
    ) -> list[str]:
        target = resolve(definition)
        description = target.get("description", "")
        if "const" in target:
            description += (
                " Fixed value: " + json.dumps(target["const"], ensure_ascii=False) + "."
            )
        elif "enum" in target:
            description += (
                " Allowed: " + json.dumps(target["enum"], ensure_ascii=False) + "."
            )
        if target.get("additionalProperties") is True:
            description += " Additional properties allowed."
        conditions = target.get("anyOf", target.get("oneOf", []))
        required_groups = [
            item["required"] for item in conditions if item.get("required")
        ]
        if required_groups:
            description += (
                " Conditional required groups: " + json.dumps(required_groups) + "."
            )
        examples = target.get("examples", [])
        columns = [
            f"`{cell(path)}`",
            source,
            str(required).lower(),
            cell(types(definition)),
            cell(description.strip()),
            "<code>" + cell(json.dumps(examples, ensure_ascii=False)) + "</code>",
        ]
        reference = definition.get("$ref")
        shared = reference and target.get("properties")
        if shared:
            key = (reference, source)
            if key not in references:
                references[key] = len(sections)
                sections.append((reference.rsplit("/", 1)[-1], target, source))
            columns[4] += f" See [properties](#section-{references[key]})."
        rows = ["| " + " | ".join(columns) + " |"]
        if not shared:
            rows.extend(children(target, path, source))
        return rows

    output = [
        "# Dataset metadata property reference",
        "",
        f"Generated from [`{SCHEMA}`]({SCHEMA}); do not edit by hand.",
        "",
        "`required` means required within the containing object, not necessarily at the root. "
        "Conditional requirements are noted in descriptions; consult the schema for full constraints.",
        "",
        "`jstat` marks standard JSON-stat2 fields; `nordicintel` marks fields inside "
        "the NordicIntel namespace and custom namespace conventions (including nested objects). Provider/adapter namespace "
        "contents are open and have no fixed property inventory.",
        "",
        "Paths are relative to each section; `{key}` is a dynamic map key and `[]` an array item. "
        "Shared objects are documented once. Primitive map entries, unused definitions and "
        "arbitrary additional properties are omitted. Examples come only from schema annotations.",
        "",
    ]
    index = 0
    while index < len(sections):
        title, node, source = sections[index]
        output.extend(
            [
                f'<a id="section-{index}"></a>',
                "",
                f"## {cell(title)}",
                "",
                "| Property | Source | Required | Type | Description | Examples |",
                "| --- | --- | --- | --- | --- | --- |",
            ]
        )
        output.extend(children(node, "", source))
        output.append("")
        index += 1
    return "\n".join(output)


def git(*arguments: str) -> bytes:
    return subprocess.run(
        ["git", *arguments], check=True, stdout=subprocess.PIPE
    ).stdout


def staged(path: str) -> bytes:
    return git("show", f":{path}")


def check_python(paths: list[str]) -> None:
    for path in paths:
        content = staged(path)
        for command in (["check"], ["format", "--check"]):
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "ruff",
                    *command,
                    "--config",
                    "ruff.toml",
                    "--stdin-filename",
                    path,
                    "-",
                ],
                input=content,
                check=True,
            )


def generate(*, from_index: bool) -> None:
    content = staged(SCHEMA) if from_index else Path(SCHEMA).read_bytes()
    result = render(json.loads(content)).encode("utf-8")
    destination = Path(REFERENCE)
    if from_index:
        if git("diff", "--cached", "--name-only", "--diff-filter=D", "--", REFERENCE):
            raise ValueError(f"Refusing to overwrite staged deletion of {REFERENCE}.")
        tracked = git("ls-files", "--", REFERENCE).strip()
        if tracked and not destination.exists():
            raise ValueError(f"Refusing to overwrite local deletion of {REFERENCE}.")
        if destination.exists() and (not tracked or git("diff", "--", REFERENCE)):
            if destination.read_bytes() != result:
                raise ValueError(
                    f"Refusing to overwrite local edits to {REFERENCE}. Save or restore them first."
                )
        if (
            tracked
            and staged(REFERENCE) != result
            and git("diff", "--cached", "--", REFERENCE)
        ):
            baseline = git("show", f"HEAD:{SCHEMA}")
            expected = render(json.loads(baseline)).encode("utf-8")
            if staged(REFERENCE) not in (expected, result):
                raise ValueError(f"Refusing to overwrite staged edits to {REFERENCE}.")
    if not destination.exists() or destination.read_bytes() != result:
        destination.write_bytes(result)
    if from_index:
        git("add", "--", REFERENCE)
    print(f"Generated {REFERENCE}" + (" from staged schema." if from_index else "."))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--generate",
        action="store_true",
        help="Generate from working-tree schema, without staging.",
    )
    arguments = parser.parse_args()
    if arguments.generate:
        generate(from_index=False)
        return
    changes = (
        git("diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z")
        .decode()
        .split("\0")
    )
    python_paths = [path for path in changes if path.endswith((".py", ".pyi"))]
    if "ruff.toml" in changes:
        python_paths = [
            path
            for path in git("ls-files", "-z").decode().split("\0")
            if path.endswith((".py", ".pyi"))
        ]
    check_python(python_paths)
    if SCHEMA in changes:
        generate(from_index=True)


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as error:
        print(f"Pre-commit failed: {error}", file=sys.stderr)
        print(
            "For Python fixes: python -m ruff check --fix .githooks && python -m ruff format .githooks; then restage.",
            file=sys.stderr,
        )
        sys.exit(1)
