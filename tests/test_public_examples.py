"""Structural checks against unchanged, offline upstream references."""

import copy
import contextlib
import io
import unittest
from unittest.mock import patch

import yaml
from jsonschema.validators import validator_for
from openapi_schema_validator import OAS30Validator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT4

from public_support import ROOT, error_records, load, project
from scripts.validate import validate


class PublicExamplesTests(unittest.TestCase):
    def test_shared_collection_validation_is_offline(self):
        with patch(
            "socket.socket", side_effect=AssertionError("Unexpected networking")
        ):
            with contextlib.redirect_stdout(io.StringIO()):
                validate(ROOT)

    @classmethod
    def setUpClass(cls):
        cls.spec = yaml.safe_load(
            (ROOT / "tests/reference/pxweb/PxAPI-2.yml").read_text(encoding="utf-8")
        )
        uri = "https://reference.example.org/pxweb"
        registry = Registry().with_resource(
            uri, Resource.from_contents(cls.spec, default_specification=DRAFT4)
        )
        cls.validators = {
            key: OAS30Validator(
                {"$ref": uri + "#/components/schemas/" + name},
                registry=registry,
                format_checker=OAS30Validator.FORMAT_CHECKER,
            )
            for key, name in [
                ("table", "TableResponse"),
                ("tables", "TablesResponse"),
                ("metadata", "Dataset"),
            ]
        }
        js = load(ROOT / "tests/reference/jsonstat/dataset.json")
        cls.jsonstat = validator_for(js)(js)

    def test_real_response_fixtures_and_exact_known_gaps_offline(self):
        gaps = load(ROOT / "tests/public/expected-pxweb-gaps.json")
        seen = set()
        with patch(
            "socket.socket",
            side_effect=AssertionError("Offline validation attempted networking"),
        ):
            for basic_path in sorted(
                (ROOT / "examples/dataset/valid").glob("real-*.json")
            ):
                metadata = load(
                    ROOT / "examples/dataset-metadata/valid" / basic_path.name
                )
                for kind, response in project(load(basic_path), metadata).items():
                    key = f"{basic_path.stem}/{kind}"
                    with self.subTest(key=key):
                        self.assertEqual(
                            response,
                            load(
                                ROOT / "tests/public" / basic_path.stem / f"{kind}.json"
                            ),
                        )
                        self.assertEqual(
                            error_records(self.validators[kind], response), gaps[key]
                        )
                        if kind == "metadata":
                            self.jsonstat.validate(response)
                    seen.add(key)
        self.assertEqual(seen, set(gaps))

    def test_contact_without_raw_is_a_public_compatibility_gap(self):
        basic = load(ROOT / "examples/dataset/valid/minimal.json")
        metadata = load(ROOT / "examples/dataset-metadata/valid/minimal.json")
        metadata["extension"] = {"contact": [{"name": "Statistics team"}]}
        response = project(basic, metadata)["metadata"]
        self.assertEqual(
            error_records(self.validators["metadata"], response),
            [
                {
                    "path": "/extension/contact/0",
                    "validator": "required",
                    "message": "'raw' is a required property",
                }
            ],
        )

    def test_invalid_public_dimension_type_is_not_hidden_by_expected_gaps(self):
        response = copy.deepcopy(
            load(ROOT / "tests/public/real-kolada-municipality-sv/metadata.json")
        )
        response["dimension"] = []
        self.assertTrue(error_records(self.validators["metadata"], response))
        self.assertTrue(list(self.jsonstat.iter_errors(response)))
