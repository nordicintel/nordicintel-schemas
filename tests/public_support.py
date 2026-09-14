"""Illustrative response projection, used only by contract tests and fixtures."""

import copy
import json
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def project(basic, metadata):
    identity = basic["identity"]
    code, lang = identity["dataset_code"], identity["language"]
    # Illustrative routing only; the catalog API will decide public identifiers.
    url = f"https://catalog.example.org/tables/{quote(code, safe='')}?lang={lang}"
    links = [{"rel": "self", "hreflang": lang, "href": url}]
    table = {
        "id": code,
        "language": lang,
        "label": basic["label"],
        "links": links,
        "variableNames": [
            metadata["dimension"][key]["label"] for key in metadata["id"]
        ],
    }
    for name in ["description", "updated", "discontinued", "source", "tags"]:
        if name in basic:
            table[name] = basic[name]
    for stored, public in [
        ("sort_code", "sortCode"),
        ("first_period", "firstPeriod"),
        ("last_period", "lastPeriod"),
        ("time_unit", "timeUnit"),
    ]:
        if stored in basic:
            table[public] = basic[stored]
    if "code" in basic.get("subject", {}):
        table["subjectCode"] = basic["subject"]["code"]
    if "paths" in basic:
        table["paths"] = [
            [
                {
                    "id": node["code"],
                    "label": node["label"],
                    **({"sortCode": node["sort_code"]} if "sort_code" in node else {}),
                }
                for node in chain["path"]
            ]
            for chain in basic["paths"]
        ]
    dataset = {
        "version": "2.0",
        "class": "dataset",
        "value": [],
        "id": copy.deepcopy(metadata["id"]),
        "dimension": copy.deepcopy(metadata["dimension"]),
        "size": [
            len(metadata["dimension"][key]["category"]["index"])
            for key in metadata["id"]
        ],
        "label": basic["label"],
    }
    for name in ["source", "updated"]:
        if name in basic:
            dataset[name] = basic[name]
    for name in ["role", "note", "link", "extension"]:
        if name in metadata:
            dataset[name] = copy.deepcopy(metadata[name])
    extension = dataset.setdefault("extension", {})
    for stored, public in [
        ("first_period", "firstPeriod"),
        ("last_period", "lastPeriod"),
        ("discontinued", "discontinued"),
        ("tags", "tags"),
    ]:
        if stored in basic:
            extension[public] = copy.deepcopy(basic[stored])
    px = extension.setdefault("px", {})
    for stored, public in [("code", "subject-code"), ("label", "subject-area")]:
        if stored in basic.get("subject", {}):
            px[public] = basic["subject"][stored]
    if "next_release" in basic:
        px["nextUpdate"] = basic["next_release"]
    listing = {
        "language": lang,
        "tables": [{k: v for k, v in table.items() if k != "language"}],
        "page": {"pageNumber": 1, "pageSize": 1, "totalElements": 1, "totalPages": 1},
        "links": [
            {
                "rel": "self",
                "hreflang": lang,
                "href": f"https://catalog.example.org/tables?lang={lang}",
            }
        ],
    }
    return {"table": table, "tables": listing, "metadata": dataset}


def error_records(validator, instance):
    return sorted(
        [
            {
                "path": "/" + "/".join(map(str, error.absolute_path)),
                "validator": error.validator,
                "message": error.message,
            }
            for error in validator.iter_errors(instance)
        ],
        key=lambda item: (item["path"], item["validator"], item["message"]),
    )
