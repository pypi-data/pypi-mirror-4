import re

from string import Template
from os import path
import os

from clearwrap import clearparser
from structurx import numbers

from structurx.config import settings

_CONFIG_DIR =  path.join(settings.CLEARPARSER_EXTRA, 'config')
_RAW_DEP_CONFIG = path.join(_CONFIG_DIR, 'AUTO-config_dep_en_medical.xml')
_PREPOS_DEP_CONFIG = path.join(_CONFIG_DIR, 'AUTO-config_dep_en_medical-prepos.xml')
_DEP_MODEL = path.join(settings.CLEARPARSER_EXTRA, 'model', 'en_dep_medical.jar')
_POS_MODEL = path.join(settings.CLEARPARSER_EXTRA, 'model', 'en_pos_medical.jar')


SENT_SPLIT_RE = re.compile(ur' - (?=[A-Z])|\*[ *]*| Date Opened[./]+')
UNCAP_WORDS_RE = re.compile(ur'\b[A-Z]{2,}\b')
WRITTEN_NUMS_PTN = ur'half|one|two|three|four|five|six|seven|eight|nine|ten'
WRITTEN_NUMS_RE = re.compile(ur'\b%s\b' % WRITTEN_NUMS_PTN)
NORM_RANGES_RE = re.compile(
    ur'\b(\d+(?:\.\d+)?) to (\d+(?:\.\d+)?)\b', re.IGNORECASE)
DIGIT_UNIT_RE = re.compile(ur'\b([\d.-]+)([a-z]+)\b', flags=re.IGNORECASE)
ABBREVS_RE = re.compile(ur'\b(s/c|sc|im|bt|ab)\b', re.IGNORECASE)
ABBREVS_TO_EXPANDED = {
    u's/c': 'subcutaneously', u'sc': u'subcutaneously', 
    u'im': 'intramuscularly', u'bt': u'bedtime', u'ab': u'at bedtime'}
POS_FIX_RE = re.compile(ur'^(?![0-9])(?!One)(\w+)\t(?!VB)\w+', re.IGNORECASE)
STRIP_PAREN_SUFF_RE = re.compile(ur' \(=\w+\)$', re.IGNORECASE)
ADD_PAREN_RE = re.compile(ur'\b(as directed|#?prn#?)\b', re.IGNORECASE)
REMOVE_HASH_RE = re.compile(ur'\b#(\w+)#\b')

def _segment_sentences(instruction_text):
    split_sents = SENT_SPLIT_RE.split(instruction_text)
    return [s for s in split_sents if s]    

def parse_instruction_text_bulk(id_text_pairs):
    id_text_pairs = [(tid, text) for tid, text in id_text_pairs if text] # remove empty
    id_sentence_pairs = []
    for tid, text in sorted(id_text_pairs):
        id_sentence_pairs.append((tid, _segment_sentences(text)))
    for tid, sentences in id_sentence_pairs:
        sentences[:] = [s.rstrip() for s in sentences if s.rstrip()] # remove empty/WS-only sentences
    all_sentences = []
    for _, sents in id_sentence_pairs:
        all_sentences.extend(sents)
    parsed = get_clearparser_wrapper().parse_in_bulk(all_sentences)
    id_parsed_pairs = []
    curr_index = 0
    prev_index = None
    for tid, sents in id_sentence_pairs:
        next_index = curr_index + len(sents)
        id_parsed_pairs.append((tid, parsed[curr_index:next_index]))
        prev_index = curr_index
        curr_index = next_index
    assert prev_index == len(parsed) - 1, "Error matching parsed sentences to raw; found %d but expected %d" % (len(parsed), prev_index + 1)
    return id_parsed_pairs

def get_clearparser_wrapper():
    check_models()
    write_configs()
    return RxClearWrapper(_PREPOS_DEP_CONFIG, _RAW_DEP_CONFIG,
      _DEP_MODEL, settings.CLEARPARSER_BASE)

def convert_range_to_hyphenated_arabic(re_match):
    """convert e.g. 'five to ten' or '5-10' to '5-10'
    """
    first = re_match.group(1).lower()
    second = re_match.group(2).lower()
    from_arabic = numbers.WRITTEN_NUMS_TO_ARABIC.get(first, first)
    to_arabic = numbers.WRITTEN_NUMS_TO_ARABIC.get(second, second)
    return u'%s-%s' % (from_arabic, to_arabic)


class RxClearWrapper(clearparser.ClearWrapper):
    def preprocess_raw(self, sentences):
        sentences = self._strip_paren_suffixes(sentences)
        sentences = self._uncapitalize(sentences)
        sentences = self._written_nums_to_arabic(sentences)
        sentences = self._normalize_ranges(sentences)
        sentences = self._normalize_abbreviations(sentences)
        sentences = self._split_unit_from_digits(sentences)
        sentences = self._add_parentheses(sentences)
        sentences = self._remove_hashes(sentences)
        num_empty = sum(not len(s) for s in sentences)
        assert not num_empty, "Found %d empty sentences" % num_empty
        return sentences
    
    def _strip_paren_suffixes(self, sentences):
        suff_stripped = [
            STRIP_PAREN_SUFF_RE.sub('', sent) for sent in sentences]
        return [sent if len(sent) else '##EMPTY##.' 
            for sent in suff_stripped]
    
    def _uncapitalize(self, sentences):
        return [
            UNCAP_WORDS_RE.sub(lambda x: x.group().lower(), sent) 
            for sent in sentences]
    
    def _written_nums_to_arabic(self, sentences):
        return [
            WRITTEN_NUMS_RE.sub(
                lambda x: numbers.WRITTEN_NUMS_TO_ARABIC[x.group().lower()], sent)
            for sent in sentences]
    
    def _normalize_ranges(self, sentences):
        return [
            NORM_RANGES_RE.sub(convert_range_to_hyphenated_arabic, sent)
            for sent in sentences]
    
    def _normalize_abbreviations(self, sentences):
        return [
            ABBREVS_RE.sub(
                lambda x: ABBREVS_TO_EXPANDED[x.group(1).lower()], sent)
            for sent in sentences]
    
    def _split_unit_from_digits(self, sentences):
        return [
            DIGIT_UNIT_RE.sub(ur'\1 \2', sent)
            for sent in sentences]
    
    def _add_parentheses(self, sentences):
        return [
            ADD_PAREN_RE.sub(ur'(\1)', sent) for sent in sentences]
    
    def _remove_hashes(self, sentences):
        return [
            REMOVE_HASH_RE.sub(ur'\1', sent) for sent in sentences]
    
    def postprocess_pos_tags(self, pos_tagged_fname, postprocessed_fname):
        with open(pos_tagged_fname) as orig_file:
            contents = orig_file.read()
        by_sentence = contents.split(u'\n\n')
        new_by_sentence = [POS_FIX_RE.sub(r'\1\tVB', sent) for sent in by_sentence]
        with open(postprocessed_fname, 'w') as new_file:
            new_file.write(u'\n\n'.join(new_by_sentence))


def check_models():
    if not path.exists(_POS_MODEL):
        raise ConfigurationError("Model for POS tagging was not found "
            " at the expected location (%r); Please download the model "
            " from %s and save it here" % (_POS_MODEL, CP_MODEL_URL))
    if not path.exists(_DEP_MODEL):
        raise ConfigurationError("Model for parsing was not found "
            " at the expected location (%r); Please download the model "
            " from %s and save it here" % (_DEP_MODEL, CP_MODEL_URL))

def write_configs():
    subs = {
        'clearparser_base': settings.CLEARPARSER_BASE,
        'med_pos_model': _POS_MODEL,
        'format': 'raw',
    }
    tmpl = Template(CLEARPARSER_MEDICAL_TEMPLATE)
    if not path.exists(_CONFIG_DIR):
        os.mkdir(_CONFIG_DIR)
    with open(_RAW_DEP_CONFIG, 'w') as f:
        f.write(tmpl.substitute(subs))
    subs['format'] = 'pos'
    with open(_PREPOS_DEP_CONFIG, 'w') as f:
        f.write(tmpl.substitute(subs))


CLEARPARSER_MEDICAL_TEMPLATE = """
<configuration>
	<common>
		<language>en</language>
		<format>$format</format>
		<parser>shift-pop</parser>
	</common>
	<classify>
		<algorithm name="lib" l="1" c="0.1" e="0.1" b="-1"/>
		<threads>2</threads>
	</classify>
	<predict>
		<tok_model>$clearparser_base/model/en_tok_opennlp.jar</tok_model>
		<pos_model>$med_pos_model</pos_model>
		<morph_dict>$clearparser_base/model/en_dict-1.0.jar</morph_dict>
	</predict>
</configuration>
"""
