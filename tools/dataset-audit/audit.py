"""Reproducible, local-only qualifier audit. No application or database imports."""
from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import re
import unicodedata
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path

FIELDS = ('refperiod', 'basePeriod', 'measuringType', 'priceType', 'adjustment')
SE = {'csn', 'domstol', 'energimyndigheten', 'fohm', 'kolada', 'konj', 'lansstyrelsen', 'msb', 'riksskog', 'scb', 'sjv', 'skogsstyrelsen'}
DEFAULT_SOURCE = Path('C:/Users/ruben/Github/nordicintel-project/tmp/dataset_languages.csv')
DEFAULT_OUTPUT = Path('tmp/qualifier-audit-sv')


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def records(path):
    with path.open(encoding='utf-8') as stream:
        for line in stream:
            yield json.loads(line)


def write_record(stream, value):
    stream.write(json.dumps(value, ensure_ascii=False, separators=(',', ':')) + '\n')


def file_hash(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def csv_rows(stream):
    # This particular export escapes apostrophes/quotes in quoted cells, but
    # leaves prose apostrophes in unquoted cells untouched. Preserve both.
    csv.field_size_limit(100_000_000)
    pattern = re.compile(r"(?<!')'(?!['\"])")
    yield from csv.reader((pattern.sub("''", line) for line in stream), escapechar="'")


@lru_cache(maxsize=32768)
def norm(value):
    text = unicodedata.normalize('NFKC', html.unescape(str(value))).casefold()
    text = re.sub(r'</?[a-zA-Z][^>]*>', ' ', text)
    return ' '.join(text.split()).strip(' .')


def candidates(record):
    for dc, dim in record['metadata']['dimension'].items():
        for field in FIELDS:
            for cc, value in dim.get('extension', {}).get(field, {}).items():
                key = [*record['identity'], dc, cc, field]
                yield {'id': hashlib.sha256(json.dumps(key, ensure_ascii=False).encode()).hexdigest(), 'identity': record['identity'], 'dimension': dc, 'category': cc, 'field': field, 'value': value}


def context(record, candidate):
    """Keep evidence locations and scope; never inspect unrelated categories."""
    basic = record['basic']; meta = record['metadata']
    dim = meta['dimension'][candidate['dimension']]; cat = dim['category']; cc = candidate['category']
    result = {}
    for key in ('label', 'description'):
        if basic.get(key): result['dataset.' + key] = basic[key]
    contents = meta.get('extension', {}).get('px', {}).get('contents')
    if contents: result['dataset.contents'] = contents
    for prefix, obj in (('dataset', meta), ('dimension', dim)):
        for i, text in enumerate(obj.get('note', [])):
            result[f'{prefix}.notes[{i}]'] = text
    result['dimension.label'] = dim['label']
    if cc in cat['label']: result['category.label'] = cat['label'][cc]
    alternate = dim.get('extension', {}).get('alternativeText', {}).get(cc)
    if alternate: result['category.alternative_label'] = alternate
    for i, text in enumerate(cat.get('note', {}).get(cc, [])):
        result[f'category.notes[{i}]'] = text
    unit = cat.get('unit', {}).get(cc, {})
    label = unit.get('label') or unit.get('extension', {}).get('base')
    if label: result['unit.label'] = label
    return result


def temporal_context(record, candidate):
    """Ownership first: metric qualifiers are not keyed by observation year."""
    meta = record['metadata']
    dim = meta['dimension'][candidate['dimension']]
    return {
        'owner_dimension': candidate['dimension'],
        'owner_category': candidate['category'],
        'owner_label': dim['category']['label'].get(candidate['category']),
        'owner_roles': [role for role, codes in meta.get('role', {}).items() if candidate['dimension'] in codes],
        'time_dimensions': {
            dc: {'label': meta['dimension'][dc]['label'],
                 'category': meta['dimension'][dc]['category'],
                 'note': meta['dimension'][dc].get('note', [])}
            for dc in meta.get('role', {}).get('time', [])
        },
    }


def extract(source, output):
    output.mkdir(parents=True, exist_ok=True)
    before = source.stat()
    digest = file_hash(source)
    counts = Counter(); providers = Counter(); seen = set()
    with source.open(encoding='utf-8-sig', newline='') as stream, (output/'records.jsonl').open('w', encoding='utf-8') as dest, (output/'00-candidates.jsonl').open('w', encoding='utf-8') as initial:
        for rowno, row in enumerate(csv_rows(stream), 1):
            assert len(row) == 17, (rowno, len(row))
            counts['all_csv_records'] += 1
            if row[2] != 'sv': continue
            counts['sv_records'] += 1
            meta = json.loads(row[14]); identity = row[:3]
            assert [meta['identity'][k] for k in ('provider_code', 'dataset_code', 'language')] == identity
            assert tuple(identity) not in seen, identity
            seen.add(tuple(identity))
            if not any(any(key in dim.get('extension', {}) for key in FIELDS) for dim in meta['dimension'].values()): continue
            basic_names = ('provider_code', 'dataset_code', 'language', 'label', 'description', 'updated', 'next_release', 'time_unit', 'first_period', 'last_period', 'discontinued', 'source_url', 'doc_url')
            record = {'identity': identity, 'source_row': rowno, 'swedish_provider': row[0] in SE, 'basic': {**dict(zip(basic_names, row[:13])), 'extension': json.loads(row[13])}, 'metadata': meta}
            write_record(dest, record); counts['candidate_records'] += 1; providers[row[0]] += 1
            for candidate in candidates(record):
                write_record(initial, candidate); counts['candidate_attributes'] += 1; counts['field_' + candidate['field']] += 1
    assert (before.st_size, before.st_mtime_ns) == (source.stat().st_size, source.stat().st_mtime_ns), 'Source changed during extraction'
    dump(output/'source.json', {'source': str(source.resolve()), 'sha256': digest, 'bytes': before.st_size, 'records_sha256': file_hash(output/'records.jsonl'), 'candidates_sha256': file_hash(output/'00-candidates.jsonl'), 'scope': 'All language=sv records, including non-SE providers. Swedish-provider subset is reported separately.', 'fields': FIELDS, 'swedish_providers': sorted(SE), 'counts': dict(counts), 'providers': dict(providers)})
    print(json.dumps({'counts': dict(counts), 'providers': dict(providers)}))


GRAIN = {
    'annual': {'år', 'kalenderår', 'year', 'calendar year'},
    'semiannual': {'halvår', 'half year'},
    'quarterly': {'kvartal', 'quarter'},
    'monthly': {'månad', 'kalendermånad', 'month', 'calendar month'},
    'weekly': {'vecka', 'week'}, 'daily': {'dag', 'day'},
}


def contains_phrase(text, value):
    return bool(re.search(r'(?<!\w)' + re.escape(norm(value)) + r'(?!\w)', norm(text)))


MONTHS = ('januari', 'februari', 'mars', 'april', 'maj', 'juni', 'juli', 'augusti', 'september', 'oktober', 'november', 'december')


@lru_cache(maxsize=8192)
def calendar_text(text):
    text = norm(text)
    text = re.sub(r'\b\d{4}-(\d{2})-(\d{2})\b', lambda m: f'date:{m[2]}-{m[1]}', text)
    for month, name in enumerate(MONTHS, 1):
        text = re.sub(r'\b(\d{1,2})\s+' + name + r'\b', lambda m: f'date:{int(m[1]):02d}-{month:02d}', text)
    text = re.sub(r'\b(\d{1,2})\s*[/.]\s*(\d{1,2})(?:\.(?!\d))?', lambda m: f'date:{int(m[1]):02d}-{int(m[2]):02d}' if 1 <= int(m[1]) <= 31 and 1 <= int(m[2]) <= 12 else m[0], text)
    text = re.sub(r'\b31\s+dec\b\.?', 'date:31-12', text)
    text = re.sub(r'\b(respektive|resp\.?|varje)\s+år\b', '', text)
    return ' '.join(text.split()).strip(' .')


def explicit_date_addition(record, candidate):
    """Conservative positive finding for a simple annual day/month statement.

    No general semantic-uniqueness inference: require no alternative date,
    matching month wording, or possible year-boundary paraphrase anywhere.
    """
    if candidate['field'] != 'refperiod': return None
    if record['basic'].get('time_unit', '').casefold() != 'annual': return None
    time_ids = record['metadata'].get('role', {}).get('time', [])
    if len(time_ids) != 1: return None
    time_codes = record['metadata']['dimension'][time_ids[0]]['category']['index']
    if not time_codes or not all(re.fullmatch(r'\d{4}', code) for code in time_codes): return None
    canonical = calendar_text(candidate['value'])
    if not re.fullmatch(r'date:\d\d-\d\d', canonical): return None
    day, month = map(int, canonical.removeprefix('date:').split('-'))
    if not (1 <= day <= 31 and 1 <= month <= 12): return None
    def strings(obj, path):
        if isinstance(obj, str): yield path, obj
        elif isinstance(obj, list):
            for i, value in enumerate(obj): yield from strings(value, f'{path}[{i}]')
        elif isinstance(obj, dict):
            for key, value in obj.items():
                # Remove only the five dimension qualifier maps themselves.
                if path.startswith('metadata.dimension[') and path.endswith('].extension') and key in FIELDS: continue
                yield path + '.key', key
                yield from strings(value, f'{path}[{key}]' if path == 'metadata.dimension' else f'{path}.{key}')
    # Walk each dimension explicitly to preserve a recognizable exclusion path.
    evidence = list(strings(record['basic'], 'basic'))
    for key, value in record['metadata'].items():
        if key == 'dimension':
            for dc, dim in value.items(): evidence.extend(strings(dim, f'metadata.dimension[{dc}]'))
        else: evidence.extend(strings(value, f'metadata.{key}'))
    for path, text in evidence:
        if canonical in calendar_text(text): return None
        # Deliberately broad blockers: "dec" elsewhere can be irrelevant, but
        # a false unresolved case is preferable to asserting unique information.
        month_name = MONTHS[month-1]
        if re.search(r'\b(?:' + month_name + '|' + month_name[:3] + r'\b)', norm(text)): return None
        if re.search(r'årsskift|årsslut|årets slut|årets utgång|utgången av|ingången av|början av|slutet av|sista dagen|första dagen|referenstidpunkt|mättidpunkt', norm(text)): return None
    return outcome('additional_explicit', '10-explicit-date-not-otherwise-stated', 'all other document strings and keys, excluding the five audited maps', {'date': canonical, 'checked_text_values': len(evidence), 'comparison_sha256': hashlib.sha256(json.dumps(evidence, ensure_ascii=False).encode()).hexdigest(), 'meaning': 'The day/month statement is additional within this local document; not a claim about external documentation or source correctness.'})


def full_document_text(record):
    """Searchable evidence outside the five audited qualifier maps themselves."""
    basic = record['basic']; meta = record['metadata']
    for k in ('label', 'description'):
        if basic.get(k): yield 'dataset.' + k, basic[k]
    contents = meta.get('extension', {}).get('px', {}).get('contents')
    if contents: yield 'dataset.contents', contents
    for i, note in enumerate(meta.get('note', [])): yield f'dataset.notes[{i}]', note
    for dc, dim in meta['dimension'].items():
        yield f'dimension[{dc}].label', dim['label']
        for i, note in enumerate(dim.get('note', [])): yield f'dimension[{dc}].notes[{i}]', note
        for cc, label in dim['category']['label'].items(): yield f'dimension[{dc}].category[{cc}].label', label
        for cc, label in dim.get('extension', {}).get('alternativeText', {}).items(): yield f'dimension[{dc}].category[{cc}].alternative_label', label
        for cc, notes in dim['category'].get('note', {}).items():
            for i, note in enumerate(notes): yield f'dimension[{dc}].category[{cc}].notes[{i}]', note
        for cc, unit in dim['category'].get('unit', {}).items():
            label = unit.get('label') or unit.get('extension', {}).get('base')
            if label: yield f'dimension[{dc}].category[{cc}].unit.label', label


def positive_adjustment(text):
    text = norm(text)
    if re.search(r'icke[ -]?säsong|ej säsong|inte säsong|osäsong|ojusterad|ej kalender|icke[ -]?kalender', text): return set()
    flags = set()
    if re.search(r'säsongs?rens', text): flags.add('seasonal')
    if re.search(r'kalenderkorr|arbetsdagskorr|arbetsdagsjust', text): flags.add('working_day')
    return flags


def outcome(status, rule, path=None, evidence=None):
    return {'status': status, 'rule': rule, 'evidence_path': path, 'evidence': evidence}


def later_rules(record, candidate, through, texts):
    field = candidate['field']; value = norm(candidate['value'])
    temporal = temporal_context(record, candidate)
    if through >= 8 and field == 'refperiod':
        if value == 'maj och november resp år':
            for dc, time in temporal['time_dimensions'].items():
                codes = list(time['category']['index'])
                if not codes or not all(re.fullmatch(r'\d{4}M(?:05|11)', code) for code in codes): continue
                months = {code[-2:] for code in codes}
                notes = ' '.join(record['metadata'].get('note', []))
                if months == {'05', '11'}:
                    return outcome('represented', '08-survey-months-in-time-categories', f'dimension[{dc}].category.index', codes)
                if 'i maj varje år' in norm(notes) and 'maj och november' in norm(notes) and all(int(code[:4]) >= 2023 for code in codes):
                    return outcome('represented', '08-survey-calendar-explained-by-note-and-times', 'dataset.notes + time categories', {'notes': notes, 'codes': codes})
        if value in ('1:a halvåret (mätperiod juni), 2:a halvåret (mätperiod december)', 'kalenderår januari-december (mätperiod juni och december)', '1:a halvåret (mätperiod juni)'):
            for path, text in texts.items():
                if all(part in norm(text) for part in ('undersökningen i juni gäller första halvåret', 'decembermätningen andra halvåret')):
                    return outcome('represented', '08-training-survey-period-explained', path, text)
        if re.fullmatch(r'\d{4}', value):
            for path in ('category.label', 'category.alternative_label'):
                text = texts.get(path, '')
                if set(re.findall(r'\b\d{4}\b', text)) == {value}:
                    return outcome('represented', '08-reference-year-in-own-category-label', path, text)
    if through >= 9 and field == 'refperiod':
        if re.fullmatch(r'\d{4}(?:-\d{4})?', value):
            for dc, time in temporal['time_dimensions'].items():
                codes = set(time['category']['index'])
                if codes == {value}:
                    return outcome('represented', '09-single-time-category-agrees', f'dimension[{dc}].category.index', sorted(codes))
                if value in codes:
                    return outcome('scope_issue', '09-reference-matches-one-of-several-periods', f'dimension[{dc}].category.index', sorted(codes))
                # Different dates can be valid for different metric categories.
                # Report mismatch for review; do not assert a source error.
                if codes and all(re.fullmatch(r'\d{4}(?:-\d{4})?', code) for code in codes):
                    return outcome('scope_issue', '09-reference-outside-time-categories-needs-review', f'dimension[{dc}].category.index', sorted(codes))
    return None


def classify(record, candidate, through):
    value = candidate['value']; field = candidate['field']; cc = candidate['category']
    dim = record['metadata']['dimension'][candidate['dimension']]
    if cc not in dim['category']['index']:
        return outcome('unresolved', 'invalid_category_reference')
    if through >= 1:
        if not isinstance(value, str) or not value.strip():
            return outcome('empty', '01-empty')
        # These are classified separately, NOT asserted redundant or disposable.
        if (field, value) in {('measuringType', 'Other'), ('priceType', 'NotApplicable'), ('adjustment', 'None')}:
            return outcome('default_like', '01-default-like')
    if through >= 2 and field == 'refperiod':
        grain = record['basic']['time_unit'].casefold()
        if norm(value) in GRAIN.get(grain, set()):
            return outcome('represented', '02-time-granularity', 'dataset.time_unit', record['basic']['time_unit'])
    texts = context(record, candidate)
    later = later_rules(record, candidate, through, texts)
    if later: return later
    if through >= 4 and field == 'refperiod' and norm(value) == 'maj och november resp år':
        for path, text in texts.items():
            n = norm(text)
            if '2023' in n and 'i maj varje år' in n and 'maj och november' in n:
                # An older summary can agree with historical time categories.
                # The note alone is not evidence of a contradiction.
                return outcome('text_match', '04-historical-survey-calendar', path, text)
    if through >= 4 and field == 'refperiod' and norm(value) in ('valår', 'mandatperiod', 'läsår', 'mätmånad'):
        for path, text in full_document_text(record):
            if contains_phrase(text, value): return outcome('represented', '04-explicit-period-kind', path, text)
    if through >= 3 and field == 'refperiod':
        # Full reference phrase, not a year appearing inside coverage, nor a
        # keyword such as "månad" in "anställningstid >6 månader".
        if len(norm(value)) >= 8 and not re.fullmatch(r'[\d\W]+', norm(value)):
            for path, text in texts.items():
                if contains_phrase(text, value):
                    return outcome('text_match', '03-full-reference-phrase', path, text)
    if through >= 3 and field == 'basePeriod':
        for path, text in texts.items():
            if path not in ('category.label', 'category.alternative_label', 'unit.label'): continue
            v = re.escape(norm(value))
            if re.search(r'(?<!\w)' + v + r'\s*=\s*100(?:\D|$)', norm(text)):
                return outcome('represented', '03-explicit-index-base', path, text)
    if through >= 4:
        if field == 'refperiod':
            # Valår/Mandatperiod can be in the time dimension label, not just
            # the metric category. Do not equate arbitrary period years.
            if norm(value) in ('valår', 'mandatperiod', 'läsår', 'mätmånad'):
                for path, text in full_document_text(record):
                    if contains_phrase(text, value): return outcome('represented', '04-explicit-period-kind', path, text)
            canonical = calendar_text(value)
            if re.fullmatch(r'date:\d\d-\d\d', canonical):
                for path, text in full_document_text(record):
                    if canonical in calendar_text(text): return outcome('text_match', '04-calendar-date-elsewhere', path, text)
            if norm(value) == 'maj och november resp år':
                for path, text in texts.items():
                    if 'maj och november' in norm(text): return outcome('text_match', '04-survey-months-in-prose', path, text)
        if field == 'basePeriod':
            for path in ('category.label', 'category.alternative_label', 'unit.label'):
                text = texts.get(path, '')
                # Require a unique year in a metric-specific label; a year
                # anywhere in a long note or a coverage range does not qualify.
                years = set(re.findall(r'\b(?:18|19|20)\d{2}\b', text))
                if re.fullmatch(r'(?:18|19|20)\d{2}', value) and years == {value} and re.search(r'taxeringsvärde|penningvärde|fasta priser|prisnivå|index', norm(text)):
                    return outcome('represented', '04-specific-base-in-measure-label', path, text)
            if norm(value) == 'senast redovisat år':
                last = record['basic']['last_period']
                for path, text in texts.items():
                    if re.search(re.escape(last) + r'\s+års\s+(?:priser|penningvärde)', norm(text)):
                        return outcome('represented', '04-latest-year-price-basis', path, text)
    if through >= 5:
        if field == 'priceType':
            pattern = r'fasta priser|fastpris|penningvärde' if value == 'Fixed' else r'löpande priser|nominell'
            for path in ('category.label', 'category.alternative_label', 'unit.label'):
                text = texts.get(path, '')
                if re.search(pattern, norm(text)):
                    return outcome('represented', '05-price-basis-in-measure-label', path, text)
        if field == 'adjustment':
            expected = {'SesOnly': {'seasonal'}, 'WorkOnly': {'working_day'}, 'WorkAndSes': {'seasonal', 'working_day'}}[value]
            for path in ('category.label', 'category.alternative_label', 'unit.label'):
                text = texts.get(path, '')
                if positive_adjustment(text) == expected:
                    return outcome('represented', '05-adjustment-in-measure-label', path, text)
            # An independent "typ av data" dimension can already express
            # adjustment. Do not mistake its alternatives for one global fact.
            for dc, other in record['metadata']['dimension'].items():
                if dc == candidate['dimension']: continue
                alternatives = [(cc, label) for cc, label in other['category']['label'].items() if positive_adjustment(label)]
                if alternatives:
                    return outcome('scope_issue', '05-adjustment-varies-in-other-dimension', f'dimension[{dc}].category', alternatives)
    if through >= 6:
        # Broad lexical matches are review candidates, NOT automatic semantic
        # deductions: "genomsnittlig lön" can still be MeasuringType=Stock.
        if field == 'measuringType':
            patterns = {'Stock': r'bestånd|stock|pågående|folkmängd|befolkning|invånare', 'Flow': r'förändring|under året|under månaden|födda|döda|avlidna|invandring|utvandring', 'Average': r'medelvärde|genomsnitt|medeltal|årsmedel'}
            for path, text in texts.items():
                if re.search(patterns[value], norm(text)):
                    return outcome('semantic_match', '06-measuring-kind-wording-needs-review', path, text)
        if field in ('refperiod', 'basePeriod'):
            for path, text in full_document_text(record):
                if contains_phrase(text, value):
                    return outcome('text_match', '06-literal-value-outside-primary-context', path, text)
        if field in ('priceType', 'adjustment'):
            for path, text in full_document_text(record):
                if field == 'priceType':
                    match = re.search(r'fasta priser|fastpris|penningvärde' if value == 'Fixed' else r'löpande priser|nominell', norm(text))
                else:
                    match = positive_adjustment(text) == {'SesOnly': {'seasonal'}, 'WorkOnly': {'working_day'}, 'WorkAndSes': {'seasonal', 'working_day'}}[value]
                if match: return outcome('text_match', '06-qualifier-in-broader-context', path, text)
    if through >= 7 and field == 'refperiod':
        if norm(value) in ('månad', 'kalendermånad'):
            for path in ('category.label', 'category.alternative_label', 'unit.label'):
                text = texts.get(path, '')
                if 'månadslön' in norm(text) or 'månads- och grundlön' in norm(text):
                    return outcome('represented', '07-monthly-wage-unit-period', path, text)
    if through >= 10:
        additional = explicit_date_addition(record, candidate)
        if additional: return additional
    return outcome('remaining', 'not_resolved_by_enabled_rules')


def run(output, through):
    stage = output/f'{through:02d}-rules'; stage.mkdir(exist_ok=True)
    counts = Counter(); grouped = defaultdict(Counter); ids = defaultdict(set); se_ids = defaultdict(set)
    groups = defaultdict(lambda: {'count': 0, 'examples': []})
    dataset_rows = []
    with (stage/'decisions.jsonl').open('w', encoding='utf-8') as all_out, (stage/'remaining.jsonl').open('w', encoding='utf-8') as remain:
        for record in records(output/'records.jsonl'):
            per_dataset = Counter()
            for candidate in candidates(record):
                decision = classify(record, candidate, through)
                owner = temporal_context(record, candidate)
                item = {**candidate, **decision, 'source_row': record['source_row'], 'dataset_label': record['basic']['label'], 'category_label': owner['owner_label'], 'owner_roles': owner['owner_roles']}
                write_record(all_out, item)
                status = decision['status']; field = candidate['field']
                per_dataset[status] += 1
                counts[status] += 1; grouped[field][status] += 1
                ids[status].add(tuple(record['identity']));
                if record['swedish_provider']: se_ids[status].add(tuple(record['identity']))
                if status not in ('represented', 'empty', 'default_like'):
                    write_record(remain, item)
                    key = (field, str(candidate['value']), status)
                    group = groups[key]; group['count'] += 1
                    if len(group['examples']) < 3:
                        group['examples'].append({**item, 'context': context(record, candidate), 'time_unit': record['basic']['time_unit'], 'temporal_context': temporal_context(record, candidate)})
            dataset_rows.append({'provider_code': record['identity'][0], 'dataset_code': record['identity'][1], 'language': record['identity'][2], 'label': record['basic']['label'], 'source_row': record['source_row'], **per_dataset})
    inventory = [{'field': k[0], 'value': k[1], 'status': k[2], **v} for k, v in sorted(groups.items(), key=lambda pair: (-pair[1]['count'], pair[0]))]
    dump(stage/'inspection.json', inventory)
    summary = {'through': through, 'script_sha256': file_hash(Path(__file__)), 'attribute_counts': dict(counts), 'dataset_counts': {k: len(v) for k, v in ids.items()}, 'swedish_provider_dataset_counts': {k: len(v) for k, v in se_ids.items()}, 'by_field': {k: dict(v) for k, v in grouped.items()}, 'groups_to_inspect': len(groups)}
    dump(stage/'summary.json', summary)
    with (stage/'datasets.csv').open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=['provider_code', 'dataset_code', 'language', 'label', 'source_row', *sorted(counts)])
        writer.writeheader(); writer.writerows(dataset_rows)
    print(json.dumps(summary))


def show(output, provider, dataset):
    for record in records(output/'records.jsonl'):
        if record['identity'][:2] == [provider, dataset]:
            print(json.dumps({'record': record, 'qualifier_ownership': [temporal_context(record, c) | {'field': c['field'], 'value': c['value']} for c in candidates(record)]}, ensure_ascii=True, indent=2))
            return
    raise SystemExit('Dataset not in extracted sv candidate collection')


def verify(output, through):
    source = json.loads((output/'source.json').read_text(encoding='utf-8'))
    assert file_hash(output/'records.jsonl') == source['records_sha256']
    assert file_hash(output/'00-candidates.jsonl') == source['candidates_sha256']
    initial = {x['id']: x for x in records(output/'00-candidates.jsonl')}
    assert len(initial) == source['counts']['candidate_attributes']
    stage = output/f'{through:02d}-rules'
    seen = set(); extra = []; counts = Counter()
    for item in records(stage/'decisions.jsonl'):
        assert item['id'] not in seen
        seen.add(item['id'])
        assert {k: item[k] for k in initial[item['id']]} == initial[item['id']]
        counts[item['status']] += 1
        if item['status'] == 'additional_explicit': extra.append(item)
    assert seen == set(initial)
    summary = json.loads((stage/'summary.json').read_text(encoding='utf-8'))
    assert dict(counts) == summary['attribute_counts']
    assert summary['script_sha256'] == file_hash(Path(__file__))
    with (stage/'additional-explicit.csv').open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.writer(stream)
        writer.writerow(['provider_code', 'dataset_code', 'language', 'label', 'dimension', 'category', 'category_label', 'field', 'value', 'candidate_id', 'source_row'])
        for x in extra:
            writer.writerow([*x['identity'], x['dataset_label'], x['dimension'], x['category'], x['category_label'], x['field'], x['value'], x['id'], x['source_row']])
    result = {'candidate_ids_reconciled': len(seen), 'source_and_extraction_hashes_verified': True,
              'additional_explicit_occurrences': len(extra), 'additional_explicit_datasets': len({tuple(x['identity']) for x in extra}),
              'decisions_sha256': file_hash(stage/'decisions.jsonl')}
    dump(stage/'verification.json', result)
    print(json.dumps(result))


def inspect(output, stage, field, limit):
    data = json.loads((output/f'{stage:02d}-rules'/'inspection.json').read_text(encoding='utf-8'))
    for group in [g for g in data if not field or g['field'] == field][:limit]:
        sample = group['examples'][0]
        print(json.dumps({'field': group['field'], 'value': group['value'], 'count': group['count'], 'status': group['status'], 'identity': sample['identity'], 'category': sample['category'], 'time_unit': sample['time_unit'], 'context': {k: v[:1000] for k, v in sample['context'].items()}}, ensure_ascii=True))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('extract', 'run', 'inspect', 'show', 'verify'))
    parser.add_argument('--source', type=Path, default=DEFAULT_SOURCE)
    parser.add_argument('--output', type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument('--through', type=int, default=1)
    parser.add_argument('--field', choices=FIELDS)
    parser.add_argument('--limit', type=int, default=10)
    parser.add_argument('--provider', default='scb')
    parser.add_argument('--dataset')
    args = parser.parse_args()
    if args.command == 'extract': extract(args.source, args.output)
    elif args.command == 'run': run(args.output, args.through)
    elif args.command == 'show': show(args.output, args.provider, args.dataset)
    elif args.command == 'verify': verify(args.output, args.through)
    else: inspect(args.output, args.through, args.field, args.limit)


if __name__ == '__main__': main()
