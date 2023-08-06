from __future__ import division
import logging; log = logging.getLogger(__name__)
import codecs
from datetime import datetime
from os import path
from collections import defaultdict

try:
    import json
except ImportError:
    import simplejson as json # python 2.5

import structurx

logging.basicConfig()
log.setLevel(logging.DEBUG)

EVAL_FIELD_COMBS = [
    ('dosage_min',),
    ('dosage_max',),
    ('dosage_unit',),
    ('dosage_min', 'dosage_max',),
    ('dosage_min', 'dosage_max', 'dosage_unit',),
    ('when_required',),
    ('period_days',),
    ('doses_per_period',),
    ('period_days', 'doses_per_period',),
    ('target_sep_min_hours',),
    ('target_sep_max_hours',),
    ('target_sep_min_hours', 'target_sep_max_hours',),
    ('dosage_min', 'dosage_max', 'dosage_unit', 'when_required',
        'period_days', 'doses_per_period',),
    ('dosage_min', 'dosage_max', 'dosage_unit', 'when_required',
        'target_sep_min_hours', 'target_sep_max_hours',),
]

def get_all_eval_fields():
    all_fields = set()
    for fg in EVAL_FIELD_COMBS:
        all_fields.update(fg)
    return all_fields

class ByFieldGroupResults(object):
    def __init__(self):
        self.comparable = 0
        self.correct = 0
    
    @property
    def accuracy(self):
        try:
            return self.correct / self.comparable
        except ZeroDivisionError:
            return float('nan')
    
    def __str__(self):
        return '%0.3f (%d from %d)' % (self.accuracy, self.correct, self.comparable)
    
    def __unicode__(self):
        return str(self)

class NoAttrib(object):
    # sentinel for attributes which are not on test instance
    def __init__(self):
        pass
    
    def __eq__(self, other):
        return isinstance(other, self.__class__)
    
    def __ne__(self, other):
        return not self == other
        
    def __repr__(self):
        return 'NoAttrib()'
    
    def __unicode__(self):
        return u'NA'
    
    def __str__(self):
        return 'NA'

def score_instructions_from_json(input_json_file, id_testpreddict_pairs):
    id_text_gold_triples = structurx.read_prescriptions_with_gold(input_json_file)
    if any(gold_instrucs is not None for _, _, gold_instrucs in id_text_gold_triples):
        return score_instructions(id_text_gold_triples, id_testpreddict_pairs)
    else:
        return None


def score_instructions(id_text_goldann_triples, id_testpred_pairs, 
        distinct_text=False):
    field_groups = EVAL_FIELD_COMBS + [None]
    results = dict((fg, ByFieldGroupResults()) for fg in field_groups)
    base_results = dict((fg, ByFieldGroupResults()) for fg in field_groups)
    observed_text = set()
    errors = []
    all_fields = get_all_eval_fields()
    majority_vals = get_majority_baseline(id_text_goldann_triples)
    log.debug("Majority values are: %r", majority_vals)
    for gold_data, test_data in zip(id_text_goldann_triples, id_testpred_pairs):
        sid, text, gold_anns = gold_data
        sid2, test_preds = test_data
        assert sid == sid2, "Mismatch between prescription IDs"
        if distinct_text and text in observed_text:
            log.info(u"Skipping %s" % gold_anns)
            continue
        observed_text.add(text)
        log.info(u"Evaluating %r against %r" % (gold_anns, test_preds))
        gold_vals = dict((f, gold_anns.get(f, NoAttrib())) for f in all_fields)
        test_vals = dict((f, test_preds.get(f, NoAttrib())) for f in all_fields)
        for fieldgroup in EVAL_FIELD_COMBS:
            if not all(f in gold_anns for f in fieldgroup):
                # missing_fields = [f for f in fieldgroup if not hasattr(gold_anns, f)]
                # log.debug("Gold ann %r is missing fields: %r from %r" % (
                #     gold_anns, missing_fields, fieldgroup))
                continue
            results[fieldgroup].comparable += 1
            correct = all(gold_anns[f] == test_vals[f]
                for f in fieldgroup)
            if correct:
                results[fieldgroup].correct += 1
            base_results[fieldgroup].comparable += 1
            base_correct = all(gold_anns[f] == majority_vals[f]
                for f in fieldgroup)
            if base_correct:
                base_results[fieldgroup].correct += 1
        results[None].comparable += 1
        all_correct = all(test_vals[f] == gold_vals[f] for f in all_fields)
        if all_correct:
            results[None].correct += 1
        else:
            errors_for_item = {}
            for f in all_fields:
                if gold_vals[f] != test_vals[f]:
                    log.debug("For field %s, %r doesn't match %r" % (f, gold_vals[f], test_vals[f]))
                    errors_for_item[f] = (gold_vals[f], test_vals[f])
            errors.append((sid, errors_for_item))
        if all(majority_vals[f] == gold_vals[f] for f in all_fields):
            base_results[None].correct += 1
        base_results[None].comparable += 1
        if log.level <= logging.DEBUG:
            matching = [f 
                for f in all_fields 
                if getattr(gold_anns, f, NoAttrib()) == getattr(test_preds, f, NoAttrib())]
            log.debug("Results for %s: MATCHING: %r; WRONG: %r" % (
                gold_anns, matching, sorted(set(all_fields) - set(matching))))
    
    results_list = [(fg, results[fg]) for fg in field_groups]
    base_results_list = [(fg, base_results[fg]) for fg in field_groups]
    return results_list, errors, base_results_list


def get_majority_baseline(id_text_goldann_triples):
    all_fields = get_all_eval_fields()
    val_counts = defaultdict(lambda: defaultdict(int))
    field_combs = defaultdict(int)
    for _, _, gold_ann in id_text_goldann_triples:
        gold_vals = dict((f, gold_ann.get(f, NoAttrib())) for f in all_fields)
        log.debug("Gold ann: %r; Gold values: %r", gold_ann, gold_vals)
        for f in all_fields:
            val_counts[f][gold_vals[f]] += 1
        known_fields = frozenset(f for f in all_fields if f in gold_ann)
        field_combs[known_fields] += 1
    best_comb = sorted(field_combs.iteritems(), key=lambda x: x[1])[-1][0] # most freq
    majority_vals = {}
    for f in all_fields:
        if f not in best_comb:
            majority_vals[f] = NoAttrib()
            continue
        obs_vals = val_counts[f].items()
        obs_vals.sort(key=lambda x: x[1])
        log.debug("Sorted values for %r: %r", f, obs_vals)
        majority_vals[f] = obs_vals[-1][0]
    return majority_vals
        
class InstructionAnnotationError(Exception):
    pass

class ExistingAnnotationError(InstructionAnnotationError):
    pass



