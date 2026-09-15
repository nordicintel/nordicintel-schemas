"""Exercise the validation/release interface using disposable collections."""

import contextlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from scripts.validate import BASE, DIALECT, parse, validate


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "VERSION").write_text("0.1.0\n", encoding="utf-8")
        self.schema = {
            "$schema": DIALECT,
            "$id": f"{BASE}/v0.1.0/schemas/value.schema.json",
            "type": "string",
        }

    def write(self, path, data):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(data), encoding="utf-8")

    def collection(self):
        self.write("schemas/value.schema.json", self.schema)
        self.write("examples/value/valid/string.json", "hello")
        self.write("examples/value/invalid/number.json", 3)

    def check(self, **kwargs):
        with contextlib.redirect_stdout(io.StringIO()):
            validate(self.root, **kwargs)

    def test_empty_scaffold_not_releasable(self):
        self.check()
        with self.assertRaisesRegex(ValueError, "empty schema collection"):
            self.check(release=True)

    def test_valid_collection_and_relative_reference(self):
        self.collection()
        self.write("schemas/other.schema.json", {
            "$schema": DIALECT,
            "$id": f"{BASE}/v0.1.0/schemas/other.schema.json",
            "$ref": "value.schema.json",
        })
        self.write("examples/other/valid/string.json", "hello")
        self.write("examples/other/invalid/number.json", 3)
        self.check()

    def test_invalid_schema_and_wrong_id(self):
        for change in ({"type": "not-a-type"}, {"$id": "https://wrong.example/schema"}):
            with self.subTest(change=change):
                self.collection()
                self.write("schemas/value.schema.json", self.schema | change)
                with self.assertRaises(Exception):
                    self.check()

    def test_unexercised_broken_reference_is_rejected(self):
        self.collection()
        self.write("schemas/value.schema.json", self.schema | {
            "$defs": {"unused": {"$ref": "missing.schema.json"}}
        })
        with self.assertRaises(Exception):
            self.check()

    def test_reference_like_example_data_is_not_a_schema(self):
        self.schema["type"] = "object"
        self.collection()
        self.write("examples/value/valid/string.json", {})
        self.write("schemas/value.schema.json", self.schema | {
            "examples": [{"$ref": "ordinary data", "$id": "ordinary data"}]
        })
        self.check()

    def test_inline_annotations_resolve_references_and_enforce_formats(self):
        self.collection()
        for keyword in ["examples", "default"]:
            for format_name, good, bad in [
                ("email", "stats@example.org", "no-at-sign"),
                ("uri", "https://example.org/data", "/relative"),
                ("date", "2026-09-15", "2026-02-30"),
                ("date-time", "2026-09-15T09:00:00Z", "2026-09-15T09:00:00"),
            ]:
                with self.subTest(keyword=keyword, format=format_name):
                    schema = self.schema | {
                        "$defs": {
                            "text": {"type": "string", "format": format_name},
                            "usage": {"$ref": "#/$defs/text"},
                        }
                    }
                    usage = schema["$defs"]["usage"]
                    usage[keyword] = [good] if keyword == "examples" else good
                    self.write("schemas/value.schema.json", schema)
                    self.check()
                    usage[keyword] = [bad] if keyword == "examples" else bad
                    self.write("schemas/value.schema.json", schema)
                    with self.assertRaisesRegex(ValueError, "Invalid inline"):
                        self.check()

    def test_incorrect_examples(self):
        self.collection()
        self.write("examples/value/invalid/number.json", "actually valid")
        with self.assertRaisesRegex(ValueError, "Unexpected validation result"):
            self.check()

    def test_duplicate_keys_rejected(self):
        with self.assertRaisesRegex(ValueError, "Duplicate JSON key"):
            parse('{"a": 1, "a": 2}')

    def test_uri_format_is_enforced_by_validation(self):
        self.schema["format"] = "uri"
        self.collection()
        self.write("examples/value/valid/string.json", "https://example.org/about")
        self.write("examples/value/invalid/number.json", "https://example.org/%zz")
        self.check()
        self.write("examples/value/valid/string.json", "https://example.org/%zz")
        with self.assertRaisesRegex(ValueError, "Unexpected validation result"):
            self.check()

    def test_release_clean_tree_and_tag(self):
        self.collection()
        def git(*args):
            subprocess.run(["git", "-C", str(self.root), *args], check=True,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        git("init", "-b", "main")
        with self.assertRaisesRegex(ValueError, "Working tree must be clean"):
            self.check(release=True)
        git("add", ".")
        git("-c", "user.name=Test", "-c", "user.email=test@example.invalid",
            "-c", "commit.gpgsign=false", "commit", "-m", "fixture")
        self.check(release=True)
        git("tag", "v0.1.0")
        with self.assertRaisesRegex(ValueError, "Tag already exists"):
            self.check(release=True)
        with patch("scripts.validate.urlopen") as fetch:
            fetch.return_value.__enter__.return_value.read.return_value = json.dumps(self.schema).encode()
            self.check(published=True)
            fetch.assert_called_once_with(self.schema["$id"], timeout=20)
            fetch.return_value.__enter__.return_value.read.return_value = b'{}'
            with self.assertRaisesRegex(ValueError, "Published schema differs"):
                self.check(published=True)


if __name__ == "__main__":
    unittest.main()
