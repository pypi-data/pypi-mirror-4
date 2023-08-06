"""Test cases for StructuRX. 

Run using:
$ python -m unittest structurx.tests
as usual
"""

import unittest
import os

from structurx import DosageAmountInfo, PerPeriodFrequency, SeparatedDosesFrequency
import structurx

class RxInterpretTestCase(unittest.TestCase):
    test_sentences = [
        (1, 'Take ONE to TWO tablets TWICE a day. Keep refrigerated.'), 
        (2, 'Take TWO capsules every FOUR to SIX hours when required.')
    ]
    
    expected_results = [
        (1,
        (DosageAmountInfo(dosage_unit=u'tablet', dosage_min=1.0, dosage_max=2.0, when_required=False),
        PerPeriodFrequency(doses_per_period=2, period_days=1.0))),
        (2,
        (DosageAmountInfo(dosage_unit=u'capsule', dosage_min=2.0, dosage_max=2.0, when_required=True),
        SeparatedDosesFrequency(target_sep_min_hours=4.0, target_sep_max_hours=6.0)))
    ]
    
    cache = 'test-parses-cache.json'

    def setUp(self):
        self.results = structurx.get_structured_instructions(
            self.test_sentences, self.cache)
        self.results_from_cache = structurx.get_structured_instructions(
            self.test_sentences, self.cache)
    
    def tearDown(self):
        os.unlink(self.cache)
        
    def test_outputs(self):
        self.assertEqual(self.results, self.expected_results)
        self.assertEqual(self.results_from_cache, self.expected_results)



if __name__ == '__main__':
    unittest.main()
