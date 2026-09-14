"""Apply grouped deductions only to survivors of the saved narrowing pass."""
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
import audit as a

ROOT = a.DEFAULT_OUTPUT
OUT = ROOT / "final"
OUT.mkdir(exist_ok=True)
prior = defaultdict(list)
for item in a.records(ROOT / "09-rules/decisions.jsonl"):
    prior[tuple(item["identity"])].append(item)

FLOW = re.compile(r"förändring|utveckling|transaktion|omsättning|försälj|försåld|sålda|köpta|nybygg|nyföretag|nyregistr|nyanmäld|nybevilj|nybörjar|invandr|utvandr|inflytt|utflytt|födda|döda|dödsfall|avlid|ingångna|upplösta|examen|examiner|utsläpp|utgifter|intäkter|kostnader|inkomster|investering|produktion|producer|förbruk|användning|konsumtion|leverans|export|import|utförda|arbetade timmar|färdigställd|beviljad|påbörjad|utbetald|inbetald|förvärv|sjukfall|arbetsolyck|olyckor|bränder|insatser|händelser|under året|under kvartalet|under månaden")
STOCK = re.compile(r"bestånd|stock|ställning|balansräkning|folkmängd|befolkning|invånare|pågående|inskrivna|medlemmar|fastigheter|lägenheter|byggnader|bostäder|skolor|elever|studerande|anställda|sysselsatta|arbetsställen|företag|partisympati|svarsfördelning|skolenhet|skuld|tillgång|innehav|ägande|areal|markanvänd")
AVERAGE = re.compile(r"genomsnitt|medelvärde|medeltal|årsmedel|månadsmedel|kvartalsmedel")
GRAINS = {"annual": {"år", "året", "kalenderår", "kalenderåret", "respektive år", "1 januari - 31 december", "resultat under året"}, "quarterly": {"kvartal", "kvartalet", "kalenderkvartal"}, "monthly": {"månad", "månaden", "kalendermånad"}}
counts = Counter(); per_field = defaultdict(Counter); dataset_counts = defaultdict(set)
all_rows = []; nonredundant = []; scope = []; dataset_rows = []

def resolve(r, x, primary, alltext):
    status=x["status"]; field=x["field"]; value=a.norm(x["value"])
    if status in ("represented", "empty", "default_like", "unresolved", "scope_issue"):
        return status, x["rule"], x.get("evidence")
    # Treat matching text as repeated only in the owning category or shared
    # dataset/dimension context. Other categories can have different semantics.
    if status == "text_match":
        if field == "basePeriod":
            return "scope_issue", "base-period-number-matches-but-role-unclear", x.get("evidence")
        path=x.get("evidence_path") or ""
        if path.startswith(("category.", "unit.", "dataset.", "dimension.notes")):
            return "represented", "same-owner-or-shared-text", x.get("evidence")
        return "scope_issue", "matching-text-in-another-category", x.get("evidence")
    if field == "refperiod":
        point=a.calendar_text(value)
        if re.fullmatch(r"date:\d\d-\d\d",point):
            if point in a.calendar_text(primary):
                return "represented", "same-calendar-date-in-description", point
            if point in a.calendar_text(alltext):
                return "scope_issue", "same-calendar-date-in-other-category", point
        grain=r["basic"]["time_unit"].casefold()
        simple=re.sub(r"^(under|hela|helt|resp\.?|respektive)\s+", "", value)
        simple=re.sub(r"\s+(resp\.?|respektive) år$", "", simple)
        if simple in GRAINS.get(grain,set()):
            return "represented", "same-period-as-time-unit", grain
        for stem in ("taxeringsår", "namngivningsår", "utjämningsår", "vår", "höst"):
            if value.startswith(stem) and stem in primary:
                return "represented", "same-named-period-in-text", stem
        # Keep offsets (year before/after), days, survey windows and boundary
        # dates unless the corresponding information has actually matched.
        if value in ("kalendermånad", "månad") and re.search(r"månadslön|grundlön", primary):
            return "represented", "monthly-salary-measure", "monthly salary wording"
    if field == "measuringType":
        pattern={"stock":STOCK,"flow":FLOW,"average":AVERAGE}.get(value)
        match=pattern.search(primary) if pattern else None
        if match:
            return "represented", "measurement-kind-expressed-by-described-statistic", match.group()
    if field == "priceType":
        pattern=r"fasta priser|fastpris|penningvärde|volymförändring|volymutveckling" if value=="fixed" else r"löpande priser|nominell"
        match=re.search(pattern,primary)
        if match: return "represented", "price-concept-in-description", match.group()
    if field == "adjustment":
        expected={"sesonly":{"seasonal"},"workonly":{"working_day"},"workandses":{"seasonal","working_day"}}[value]
        if a.positive_adjustment(primary)==expected:
            return "represented", "adjustment-in-description", "matching adjustment wording"
    if field == "basePeriod":
        # A differently stated base is a source interpretation issue, not proof
        # that a new independently useful base needs to be preserved.
        if re.search(r"(?:\d{4}(?:[mk]\d{1,2})?|[a-z]+ \d{4})\s*=\s*100",primary):
            return "scope_issue", "another-index-base-already-stated", primary[:500]
    return "nonredundant", "not-expressed-after-grouped-comparison", None

with (OUT/"decisions.jsonl").open("w",encoding="utf8") as dest:
 for r in a.records(ROOT/"records.jsonl"):
    items=prior.pop(tuple(r["identity"])); local=Counter(); kept=[]
    alltext=a.norm(" ".join(text for _,text in a.full_document_text(r)))
    for x in items:
        ctx=a.context(r,x)
        primary=a.norm(" ".join(ctx.values()))
        status,rule,evidence=resolve(r,x,primary,alltext)
        z={**x,"previous_status":x["status"],"status":status,"rule":rule,"evidence":evidence}
        a.write_record(dest,z); counts[status]+=1; per_field[x["field"]][status]+=1
        dataset_counts[status].add(tuple(r["identity"])); local[status]+=1
        row=[*r["identity"],r["basic"]["label"],x["dimension"],x["category"],ctx.get("category.label",""),x["field"],x["value"],rule,r["source_row"]]
        if status=="nonredundant": nonredundant.append(row);kept.append({"dimension":x["dimension"],"category":x["category"],"category_label":ctx.get("category.label"),"field":x["field"],"value":x["value"]})
        elif status in ("scope_issue","unresolved"): scope.append(row)
    if kept: dataset_rows.append({"identity":r["identity"],"label":r["basic"]["label"],"source_row":r["source_row"],"fields":kept})
assert not prior
header=["provider_code","dataset_code","language","label","dimension","category","category_label","field","value","reason","source_row"]
for name,rows in [("nonredundant-attributes.csv",nonredundant),("scope-questions.csv",scope)]:
 with (OUT/name).open("w",encoding="utf-8-sig",newline="") as f:
    w=csv.writer(f);w.writerow(header);w.writerows(rows)
with (OUT/"nonredundant-datasets.jsonl").open("w",encoding="utf8") as f:
 for r in dataset_rows:a.write_record(f,r)
with (OUT/"nonredundant-datasets.csv").open("w",encoding="utf-8-sig",newline="") as f:
 w=csv.writer(f);w.writerow(["provider_code","dataset_code","language","label","fields","source_row"])
 for r in dataset_rows:w.writerow([*r["identity"],r["label"],", ".join(sorted({x["field"] for x in r["fields"]})),r["source_row"]])
summary={"attributes":dict(counts),"datasets":{k:len(v) for k,v in dataset_counts.items()},"by_field":{k:dict(v) for k,v in per_field.items()},"method":"Grouped semantic deductions on saved pass 09 survivors; not individual certification. Scope ambiguities are exported separately.","source_sha256":json.loads((ROOT/"source.json").read_text(encoding="utf8"))["sha256"],"input_decisions_sha256":a.file_hash(ROOT/"09-rules/decisions.jsonl"),"script_sha256":a.file_hash(Path(__file__))}
a.dump(OUT/"summary.json",summary)
print(json.dumps(summary))
