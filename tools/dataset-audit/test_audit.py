import copy
import io
import unittest

import audit


def example(field='refperiod', value='31 december'):
    return {
        'identity': ['scb', 'TEST', 'sv'],
        'basic': {'label': 'Example', 'time_unit': 'Annual', 'last_period': '2024'},
        'metadata': {
            'role': {'time': ['time'], 'metric': ['measure']},
            'dimension': {
                'measure': {'label': 'Measure', 'category': {
                    'index': {'count': 0}, 'label': {'count': 'Antal'}},
                    'extension': {field: {'count': value}}},
                'time': {'label': 'År', 'category': {
                    'index': {'2024': 0}, 'label': {'2024': '2024'}}},
            },
        },
    }


def verdict(record, through=9):
    return audit.classify(record, next(audit.candidates(record)), through)


class AuditTests(unittest.TestCase):
    def test_csv_preserves_unquoted_and_escaped_apostrophes(self):
        line = 'vessel\'s,"{\'"label\'":\'"vessel\'\'s\'"}"\n'
        self.assertEqual(list(audit.csv_rows(io.StringIO(line))), [["vessel's", '{"label":"vessel\'s"}']])

    def test_grain_does_not_imply_december_31(self):
        self.assertEqual(verdict(example())['status'], 'remaining')
        self.assertEqual(verdict(example(value='Kalenderår'))['status'], 'represented')

    def test_positive_date_finding_checks_other_encodings_and_context(self):
        self.assertEqual(verdict(example(), 10)['status'], 'additional_explicit')
        record = example()
        record['metadata']['dimension']['measure']['category']['unit'] = {'count': {'decimals': 0}}
        self.assertEqual(verdict(record, 10)['status'], 'additional_explicit')
        for note in ['Avser årsskiftet.', 'Avser 2024-12-31.', 'Uppgift i december.', 'Vid årets utgång.']:
            record = example(); record['metadata']['note'] = [note]
            with self.subTest(note=note):
                self.assertNotEqual(verdict(record, 10)['status'], 'additional_explicit')
        record = example(); record['basic']['time_unit'] = 'Monthly'
        self.assertNotEqual(verdict(record, 10)['status'], 'additional_explicit')

    def test_numeric_base_in_coverage_is_not_redundancy(self):
        record = example('basePeriod', '2019')
        record['basic']['label'] = 'Index. År 2019-2024'
        self.assertNotEqual(verdict(record)['status'], 'represented')
        record['metadata']['dimension']['measure']['category']['label']['count'] = 'Index 2019=100'
        self.assertEqual(verdict(record)['status'], 'represented')

    def test_qualifier_uses_own_category_not_another_metric(self):
        record = example('priceType', 'Fixed')
        category = record['metadata']['dimension']['measure']['category']
        category['index']['other'] = 1
        category['label']['other'] = 'Fasta priser'
        self.assertEqual(verdict(record)['status'], 'text_match')

    def test_reference_year_in_metric_can_differ_from_time(self):
        record = example(value='2008')
        record['metadata']['dimension']['measure']['category']['label']['count'] = 'Totalt taxeringsvärde 2008, miljoner kr'
        self.assertEqual(verdict(record)['rule'], '08-reference-year-in-own-category-label')

    def test_matching_one_historical_year_is_not_a_contradiction(self):
        record = example(value='2004')
        record['metadata']['dimension']['time']['category'] = {
            'index': {'2004': 0, '2013': 1}, 'label': {'2004': '2004', '2013': '2013'}}
        self.assertEqual(verdict(record)['rule'], '09-reference-matches-one-of-several-periods')

    def test_historical_survey_months_are_represented(self):
        record = example(value='Maj och november resp år')
        record['metadata']['note'] = ['Från och med 2023 i maj varje år; tidigare maj och november.']
        record['metadata']['dimension']['time']['category'] = {
            'index': {'2022M05': 0, '2022M11': 1, '2023M05': 2},
            'label': {'2022M05': '2022M05', '2022M11': '2022M11', '2023M05': '2023M05'}}
        self.assertEqual(verdict(record)['status'], 'represented')
        self.assertNotEqual(verdict(record, 4)['status'], 'conflict')

    def test_adjustment_negation_and_combined_requirements(self):
        self.assertEqual(audit.positive_adjustment('icke säsongsrensad'), set())
        self.assertEqual(audit.positive_adjustment('Säsongsrensad'), {'seasonal'})
        record = example('adjustment', 'WorkAndSes')
        record['metadata']['dimension']['measure']['category']['label']['count'] = 'Säsongrensad'
        self.assertNotEqual(verdict(record)['status'], 'represented')

    def test_defaults_remain_explicitly_separate(self):
        for field, value in [('measuringType', 'Other'), ('priceType', 'NotApplicable'), ('adjustment', 'None')]:
            with self.subTest(field=field):
                self.assertEqual(verdict(example(field, value))['status'], 'default_like')

    def test_invalid_category_reference_is_not_empty(self):
        record = example(value='')
        record['metadata']['dimension']['measure']['extension']['refperiod'] = {'EliminatedValue': ''}
        self.assertEqual(verdict(record)['status'], 'unresolved')

    def test_comparison_text_and_candidate_identity_are_preserved(self):
        self.assertIn('<1 dag', audit.norm('utbildning <1 dag och >6 månader'))
        record = example()
        original = copy.deepcopy(record)
        first = list(audit.candidates(record))
        verdict(record)
        self.assertEqual(record, original)
        self.assertEqual(first, list(audit.candidates(record)))


if __name__ == '__main__':
    unittest.main()
