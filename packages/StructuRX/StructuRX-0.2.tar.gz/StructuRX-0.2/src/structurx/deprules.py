from __future__ import division

import re
import warnings
import calendar
import logging; logging.basicConfig(); log = logging.getLogger(__name__)
from itertools import takewhile
from os import path
import sys
from datetime import datetime

try:
    import json
except ImportError:
    import simplejson as json # python 2.5

from clearwrap import clearparser
from structurx import numbers, rxparse, evaluate
from structurx import DosageAmountInfo, SeparatedDosesFrequency, PerPeriodFrequency
from structurx.config import settings

import structurx

log.setLevel(logging.INFO)

DAILY_TIME_EVENTS = set([
  'morning', 'evening', 'afternoon', 'night', 'breakfast', 'lunch', 'dinner', 
  'midday', 'bedtime'])

WEEKLY_TIME_EVENTS = set(
  [calendar.day_name[i].lower() for i in range(6)] + 
  [calendar.day_abbr[i].lower() for i in range(6)])


def interpret_from_json_and_store(input_json_file, output_json_file=None,
        parse_cache=None):
    """Annotates the values in the supplied JSON, writing to output_json_file
    if supplied, and returning the results if there are gold annotations
    on the input_json_file.
    """
    id_text_pairs = structurx.read_prescriptions_without_gold(input_json_file)
    id_testpred_pairs = get_structured_instructions(id_text_pairs, parse_cache)
    if output_json_file:
        structurx.store_structured_instructions(id_testpred_pairs, id_text_pairs,
            output_json_file)
    input_json_file.seek(0)
    id_testpreddict_pairs = structurx.convert_instructions_to_dict(id_testpred_pairs)
    return evaluate.score_instructions_from_json(
        input_json_file, id_testpreddict_pairs)


def get_structured_instructions(id_text_pairs, parse_cache_fname=None):
    instructions = []
    id_dep_graph_pairs = get_dep_graphs(id_text_pairs, parse_cache_fname)
    for pid, dep_graphs in id_dep_graph_pairs:
        struct_inst = structured_instructions_from_deps(dep_graphs)
        instructions.append((pid, struct_inst))
    return instructions

def get_dep_graphs(id_text_pairs, cache_fname=None):
    all_dep_graphs = []
    all_raw = get_raw_parsed_instructions(id_text_pairs, cache_fname)
    for sid, raw_parses in all_raw:
        dep_graphs = []
        for raw in raw_parses:
            dep_graph = clearparser.DependencyGraph.from_clear_parse(
                raw, graph_label=sid)
            dep_graphs.append(dep_graph)
        all_dep_graphs.append((sid, dep_graphs))
    return all_dep_graphs


def get_raw_parsed_instructions(id_text_pairs, cache_fname=None):
    if cache_fname:
        if not path.exists(cache_fname):
            _parse_and_cache(id_text_pairs, cache_fname)
        with open(cache_fname) as f:
            parsed = json.load(f)
            log.debug("Read %d parses from cache at %s", len(parsed), cache_fname)
        #sanity-check the cache:
        found_sids = set(sid for sid, _ in parsed)
        requested_sids = set(sid for sid, _ in id_text_pairs)
        if not found_sids == requested_sids:
            raise InvalidCacheException("Mismatch between cached IDs and expected IDs"
                " (missing: %r; extraneous: %r)", requested_sids - found_sids,
                found_sids - requested_sids)
    else:
        parsed = force_parse_instructions(id_text_pairs)
    return parsed


class InvalidCacheException(Exception):
    pass

def _parse_and_cache(id_text_pairs, fname):
    parsed_pairs = force_parse_instructions(id_text_pairs)
    with open(fname, 'w') as f:
        json.dump(parsed_pairs, f)
        log.debug("Wrote %d parses to cache at %s", len(parsed_pairs), fname)


def force_parse_instructions(id_text_pairs):
    return rxparse.parse_instruction_text_bulk(id_text_pairs)


def structured_instructions_from_deps(dep_graphs, defaults=None):
    for dep_graph in dep_graphs:
        for tcn in dep_graph.top_content_nodes():
            amt_info, freq_info = InstructionFromDepsInterpreter(
                dep_graph, tcn, defaults=defaults).get()
            if amt_info or freq_info:
                return amt_info, freq_info
    return None, None


class InstructionFromDepsInterpreter(object):
    """Interpret structured instructions from dependency graphs
    using a rule-based approach."""
    def __init__(self, dep_graph, top_content_node, defaults=None):
        log.debug("Handling Med %r" % dep_graph.graph_label)
        self.dep_graph = dep_graph
        self.top_content_node = top_content_node
        self.defaults = defaults
        if self.defaults is None:
            self.defaults = {}
    
    def get(self):
        return self._get_structured_instructions()
    
    def _get_structured_instructions(self):
        dosage_amount_info = None
        # usually dosage info is the direct object of the verb ('OBJ')
        dir_obj_nodes = self.dep_graph.predecessors_for_label(self.top_content_node, u'OBJ')
        for obj_node in dir_obj_nodes:
            dosage_amount_info = self._get_dosage_amount_from_object(obj_node)
            if dosage_amount_info:
                break #XXX - should maybe do more principle ordering here instead of arbitrary?
    
        dosage_freq_info_opts = []
        # next, look for TMP predecessors of either the main verb
        # or one of its direct objects - these usually hold freq info
        poss_tmp_nodes = []
        for node in [self.top_content_node] + dir_obj_nodes:
            poss_tmp_nodes.extend(
              self.dep_graph.predecessors_for_label(node, u'TMP'))
        log.debug(u"Found %d possible TMP nodes" % len(poss_tmp_nodes))
        dosage_freq_info_opts = [
          self._get_dosage_freq_from_tmp(tmp_node) 
          for tmp_node in poss_tmp_nodes]
        log.debug(
          u"Found %d possible TMP nodes yielding %d sets of instructions" % 
          (len(poss_tmp_nodes), sum(1 for dfi in dosage_freq_info_opts if dfi)))
        dosage_freq_info = None
        for dfi in dosage_freq_info_opts:
            if dfi:
                dosage_freq_info = dfi
                break
        if dosage_freq_info is None:
            try:
                period_hours = self.defaults['period_hours']
                doses_per_period = self.defaults['doses_per_period']
                dosage_freq_info = PerPeriodFrequency(
                    doses_per_period, period_hours / 24.0)
            except KeyError:
                pass
        if not dosage_amount_info:
            dosage_amount_info = DosageAmountInfo('', None, None)
        dosage_amount_info.when_required = self._is_only_when_required()
        return dosage_amount_info, dosage_freq_info
    
    def _is_only_when_required(self):
        """Check if the prescription is 'when required' ---
        look for 'when' linked to 'required' node anywhere in the graph"""
        required_node = None
        for node in self.dep_graph.nodes:
            if getattr(node, 'form', None) == u'required':
                required_node = node
                break
        if required_node:
            for predec in self.dep_graph.predecessors(required_node):
                if predec.form == u'when':
                    return True
        return False
    
    def _get_dosage_freq_from_tmp(self, tmp_node):
        if tmp_node.form == u'daily':
            log.debug("Found a TMP node 'daily'")
            return PerPeriodFrequency(1, 1)
        elif tmp_node.pos == u'IN': # preposition - eg in, at, before, after
            pmod_predecs = self.dep_graph.predecessors_for_label(tmp_node, u'PMOD')
            # look for e.g. 'at bedtime', 'in the morning', 'on mondays' etc
            log.debug(
              u"Found node with POS 'IN' as TMP predecessor: %s; "
              u"it has %d PMOD predecessors: %s" % (
                clearparser.node_flp(tmp_node), 
                len(pmod_predecs),
                u','.join(clearparser.node_form_pos(pn) for pn in pmod_predecs)))
            for pmod_node in pmod_predecs:
                if pmod_node.lemma.lower() in DAILY_TIME_EVENTS:
                    log.debug(u"'%s' denotes a daily event" % clearparser.node_flp(pmod_node))
                    return PerPeriodFrequency(1, 1)
                elif pmod_node.lemma.lower() in WEEKLY_TIME_EVENTS:
                    log.debug(u"'%s' denotes a weekly event" % clearparser.node_flp(pmod_node))
                    return PerPeriodFrequency(1, 7)
        elif tmp_node.lemma in (u'once', u'twice', u'time'):
            return self._get_dosage_freq_from_tmp_times_per_period(tmp_node)
        elif tmp_node.lemma in (u'hour', u'day', u'week', u'fortnight', u'month'):
            return self._get_dosage_freq_from_tmp_sep_doses(tmp_node)
    
    def _get_dosage_freq_from_tmp_sep_doses(self, tmp_node):
        nmod_predecs = self.dep_graph.predecessors_for_label(tmp_node, u'NMOD')
        has_every_or_each = any(nmn.lemma in (u'every', u'each') for nmn in nmod_predecs)
        if not has_every_or_each:
            warnings.warn("No NMOD 'every' or 'each' found for TMP node %s for graph %r; not returning dosage separation" % 
              (clearparser.node_flp(tmp_node), self.dep_graph.graph_label))
        sep_mult_min, sep_mult_min = None, None
        for nmn in nmod_predecs:
            if nmn.pos == u'CD':
                sep_mult_min, sep_mult_max = _written_num_range_to_float_range(nmn.form)
        if sep_mult_min is None:
            return None
        sep_unit_in_hours = None
        try:
            sep_unit_in_hours = structurx.PERIOD_NAMES_TO_HOURS[tmp_node.lemma]
        except KeyError:
            warnings.warn(
              "Could not determine separation unit for lemma '%s'" % tmp_node.lemma)
            return None
        if has_every_or_each:
            return SeparatedDosesFrequency(
              sep_mult_min * sep_unit_in_hours, sep_mult_max * sep_unit_in_hours)
        else:
            return None
    
    def _get_dosage_freq_from_tmp_times_per_period(self, tmp_node):
            # here we're looking for structures like
            # 'twice a day', 'weekly', 'three times a week', 'twice daily' etc
        if tmp_node.lemma == u'time':
            doses_per_period = None
            # find out *how many* times
            nmod_predecs = self.dep_graph.predecessors_for_label(tmp_node, u'NMOD')
            for nmod_node in nmod_predecs:
                if nmod_node.pos == u'CD':
                    doses_per_period = numbers.written_num_to_int(nmod_node.form)
            if doses_per_period is None:
                warnings.warn(
                  "Could not determine doses per period for %s/%s "
                  "with NMOD children %s" % (
                    tmp_node.form, tmp_node.pos, 
                    ', '.join(clearparser.node_flp(nmn) for nmn in nmod_predecs)))
        elif tmp_node.form == u'once':
            doses_per_period = 1
        elif tmp_node.form == u'twice':
            doses_per_period = 2
        
        period_hours = None
        for tmp_node_tmp in self.dep_graph.predecessors_for_label(tmp_node, u'TMP'):
            # determining the period referred to
            # - eg 'daily', or '(twice) a week'
            period_lem = tmp_node_tmp.lemma
            try:
                period_hours = structurx.PERIOD_NAMES_TO_HOURS[period_lem]
            except KeyError:
                warnings.warn(
                  "Could not determine period for lemma '%s'" % period_lem)
                continue
            log.debug("Period is %0.1f hours" % period_hours)
            break
        
        if doses_per_period is None:
            doses_per_period = self.defaults.get('doses_per_period', None)
            if doses_per_period is not None:
                log.debug("Setting doses_per_period to default value of %r" %
                    doses_per_period)
            else:
                log.debug("No default found for doses_per_period")
        if period_hours is None:
            period_hours = self.defaults.get('period_hours', None)
            if period_hours is not None:
                log.debug("Setting period_hours to default value of %r" % period_hours)
            else:
                log.debug("No default found for doses_per_period")
        
        if doses_per_period is None or period_hours is None:
            warnings.warn("Incomplete per-period dosage found")
            return None #XXX maybe return partial here?
        else:
            return PerPeriodFrequency(doses_per_period, period_hours / 24.0)
    
    def _get_dosage_amount_from_object(self, obj_node):
        dosage_unit = None
        dosage_min = None
        dosage_max = None
        digit_unit_match = rxparse.DIGIT_UNIT_RE.match(obj_node.form)
        if digit_unit_match: # handle unspaced dosage/units - e.g. 200mL
            # should be POS of 'CD' but many o thers exist - e.g. 'VBZ', 'LS', 'NNP'
            warnings.warn("Got digit/unit match (should be unnecessary now) for %s" % 
                clearparser.node_flp(obj_node))
            dosage_unit = digit_unit_match.group(2).lower()
            dosage_min, dosage_max = _written_num_range_to_float_range(
                digit_unit_match.group(1))
            return DosageAmountInfo(dosage_unit, dosage_min, dosage_max)
        elif obj_node.pos in (u'NN', u'NNS'): # handle dosage and units separated - unit should be the head
            log.debug("Got NN/NNS match for %s" % clearparser.node_flp(obj_node))
            dosage_unit = obj_node.lemma
            nmod_predecs = self.dep_graph.predecessors_for_label(obj_node, u'NMOD')
            nmod_predecs_cd_pos = [nmn 
                for nmn in nmod_predecs 
                if nmn.pos in (u'CD', u'LS')] # CD is best but we sometime get LS it seems
            if len(nmod_predecs_cd_pos) == 1:
                cd_node = nmod_predecs_cd_pos[0]
                if cd_node.form in (u'a', u'an'):
                    dosage_min, dosage_max = 1.0, 1.0
                else:
                    # should just use obj_node.form here but seomtimes we get '200mL mL'
                    # so we remove the first 'mL'
                    form = rxparse.DIGIT_UNIT_RE.sub(ur'\1', cd_node.form)
                    log.debug("Getting dosage amount information from '%s'" % form)
                    dosage_min, dosage_max = _written_num_range_to_float_range(form)
                    dosage_min_rep = "" if dosage_min is None else "%0.2f" % dosage_min 
                    dosage_max_rep = "" if dosage_max is None else "%0.2f" % dosage_max 
                    log.debug(("Dosage: %s--%s" % (dosage_min_rep, dosage_max_rep)))
            else:
                warnings.warn(
                    "%d (!=1) NMOD children with POS of 'CD' - can't eval" % len(nmod_predecs_cd_pos))
            # if dosage_max is None:
            #     warnings.warn(u"Could not determine dosage for Med %r" % self.dep_graph.graph_label)
            return DosageAmountInfo(dosage_unit, dosage_min, dosage_max)
        elif obj_node.pos == u'CD': # dosage only - units have disappeared somewhere
            log.debug("Only have dosage information - no units for %s" % clearparser.node_flp(obj_node)) 
            dosage_min, dosage_max = _written_num_range_to_float_range(
              obj_node.form)
            return DosageAmountInfo('', dosage_min, dosage_max)
        else:
            warnings.warn("Can't interpret OBJ node %s" % clearparser.node_flp(obj_node))   
    
    
def _written_num_range_to_value_range(form, valtype):
    if u'-' in form:
        try:
            lower, upper = form.split(u'-')
        except ValueError:
            warnings.warn(u"Couldn't interpret range '%s'" % form)
            return None
        lower_val = numbers.written_num_to_value(lower, valtype)
        upper_val = numbers.written_num_to_value(upper, valtype)
        return (lower_val, upper_val)
    else:
        val = numbers.written_num_to_value(form, valtype)
        return (val, val)

def _written_num_range_to_float_range(form):
    return _written_num_range_to_value_range(form, float)

