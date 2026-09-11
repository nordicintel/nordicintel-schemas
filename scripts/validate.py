"""Validate local contracts, check release readiness, or verify published URLs."""

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import urlsplit
from urllib.request import urlopen

from jsonschema import Draft202012Validator
from referencing import Registry
from referencing.jsonschema import DRAFT202012

ROOT = Path(__file__).resolve().parents[1]
DIALECT = "https://json-schema.org/draft/2020-12/schema"
BASE = "https://raw.githubusercontent.com/nordicintel/nordicintel-schemas"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def pairs(items):
    result = {}
    for key, value in items:
        require(key not in result, f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def invalid_constant(value):
    raise ValueError(f"Invalid JSON constant: {value}")


def parse(text):
    return json.loads(text, object_pairs_hook=pairs, parse_constant=invalid_constant)


def git(root, *args):
    return subprocess.check_output(
        ["git", "-C", str(root), *args], text=True, stderr=subprocess.PIPE
    ).strip()


def check_references(resource, resolver, top=True):
    """Traverse schema resources only, not example/default/const data."""
    node = resource.contents
    if isinstance(node, dict):
        require(top or "$id" not in node, "Use file-level $id only; use $defs for subschemas")
        require("$schema" not in node or node["$schema"] == DIALECT, "Wrong schema dialect")
        for keyword in ("$ref", "$dynamicRef"):
            if keyword in node:
                reference = node[keyword]
                parts = urlsplit(reference)
                require(not parts.scheme and not parts.netloc and not parts.path.startswith("/"),
                        f"Use relative references: {reference}")
                resolved = resolver.lookup(reference)
                require(isinstance(resolved.contents, (dict, bool)),
                        f"Reference does not target a schema: {reference}")
                Draft202012Validator.check_schema(resolved.contents)
    for child in resource.subresources():
        check_references(child, resolver.in_subresource(child), top=False)


def validate(root, release=False, published=False):
    version = (root / "VERSION").read_text(encoding="utf-8").strip()
    require(re.fullmatch(r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)", version),
            "VERSION must contain a numeric MAJOR.MINOR.PATCH version")
    documents = {}
    resources = []
    for path in sorted((root / "schemas").rglob("*.json")):
        require(path.name.endswith(".schema.json"), f"Expected *.schema.json: {path}")
        schema = parse(path.read_text(encoding="utf-8"))
        require(isinstance(schema, dict), f"Schema root must be an object: {path}")
        require(schema.get("$schema") == DIALECT, f"Missing/wrong $schema: {path}")
        expected = f"{BASE}/v{version}/{path.relative_to(root).as_posix()}"
        require(schema.get("$id") == expected, f"Expected $id {expected}")
        require(expected not in documents, f"Duplicate $id: {expected}")
        Draft202012Validator.check_schema(schema)
        documents[expected] = (path, schema)
        resources.append((expected, DRAFT202012.create_resource(schema)))

    # Registry has no network retriever: every reference must resolve locally.
    registry = Registry().with_resources(resources).crawl()
    count = 0
    covered = set()
    for uri, resource in resources:
        check_references(resource, registry.resolver(uri))
        path, schema = documents[uri]
        relative = path.relative_to(root / "schemas")
        example_dir = root / "examples" / relative.parent / path.name.removesuffix(".schema.json")
        validator = Draft202012Validator(schema, registry=registry)
        for kind in ("valid", "invalid"):
            examples = sorted((example_dir / kind).glob("*.json"))
            require(examples, f"Missing {kind} examples: {example_dir}")
            for example in examples:
                instance = parse(example.read_text(encoding="utf-8"))
                errors = list(validator.iter_errors(instance))
                require(bool(errors) == (kind == "invalid"),
                        f"Unexpected validation result: {example}" +
                        (f": {errors[0].message}" if errors else " (expected invalid)"))
                covered.add(example)
                count += 1
    unknown = set((root / "examples").rglob("*.json")) - covered
    require(not unknown, f"Examples without a matching schema/location: {sorted(unknown)}")

    if release or published:
        require(documents, "Cannot release or verify an empty schema collection")
        require(not git(root, "status", "--porcelain", "--untracked-files=all"),
                "Working tree must be clean; commit intended changes first")
        tag = f"v{version}"
        if release:
            require(not git(root, "tag", "--list", tag), f"Tag already exists: {tag}")
            remotes = git(root, "remote").splitlines()
            for remote in remotes:
                require(not git(root, "ls-remote", "--tags", remote, f"refs/tags/{tag}"),
                        f"Tag already exists on {remote}: {tag}")
            print(f"Release-ready commit: {git(root, 'rev-parse', 'HEAD')} (tag {tag})")
        if published:
            require(git(root, "rev-parse", f"{tag}^{{commit}}") == git(root, "rev-parse", "HEAD"),
                    f"Check out {tag} before verifying published schemas")
            for uri, (_, expected) in documents.items():
                with urlopen(uri, timeout=20) as response:
                    actual = parse(response.read().decode("utf-8"))
                require(actual == expected, f"Published schema differs: {uri}")
            print(f"Verified {len(documents)} published URLs and their locally checked references")
    print(f"Validated {len(documents)} schemas and {count} examples" +
          (" (empty scaffold; not releasable)" if not documents else ""))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--release", action="store_true", help="Check readiness without tagging or publishing")
    mode.add_argument("--published", action="store_true", help="Verify released URLs against the checked-out tag")
    args = parser.parse_args()
    try:
        validate(ROOT, args.release, args.published)
    except Exception as error:
        print(f"Validation failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
