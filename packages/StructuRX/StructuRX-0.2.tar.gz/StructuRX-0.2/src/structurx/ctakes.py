from os import path
import codecs
from xml.etree import ElementTree as elemtree
import glob
import warnings
import logging; logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

try:
    import json
except ImportError:
    import simplejson as json # python 2.5


import structurx
from structurx import numbers, evaluate

CTAKES_MED_PREFIX = 'Aspirin '  # prefix hack to get cTAKES to recognise some meds

POST_WRITE_INSTRUCTIONS = """
    The files have now been written out. You now need to set up a CPE (CollectionProcessingEngine)
    descriptor in cTakes. First duplicate the 'cTAKESdesc' tree from under the cTAKES root.
    (this is needed so you can set the UMLS credentials in a component in an
    aggregate processing engine, which doesn't seem to be possible in UIMA).
    You'll also need to customise 'drugnerdesc/analysisengine/DictionaryLookupAnnotatorUMLS.xml' 
    to add in a UMLS username/password at settings UMLSPW and UMLSUser. 
    
    After this, it's just a standard UIMA processing setup. Run the UIMA CPE GUI 
    using './runctakesCPE.sh' from the cTAKES directory. You'll want to
    base your CPE on 
    'drugnerdesc/collection_processing_engine/DrugNER_PlainText_CPE.xml',
    so load that CPE descriptor. 
    (Since you have duplicated the entire tree, the analysis engine 
    DrugAggregatePlaintextUMLSProcessor.xml should already point to the correct
    edited copy of DictionaryLookupAnnotatorUMLS.xml). 
    From the GUI, select as the input directory the holding directory here:
        %s 
    and set the output directory to the cTAKES output path:
        %s 
    
    You might want to save the CPE at this stage. (Instead of using the GUI,
     you might find it easier to just edit the XML in a new copy of 
     'DrugNER_PlainText_CPE.xml', and then load that in the GUI later)
    
    Then hit the play button at the bottom to run the CPE
    and the annotation  should magically happen. 
    
    After this, you can run the same StructuRX command again and 
    the predictions should be written out as JSON.
"""



def store_and_eval_ctakes_predictions(input_json_file, ctakes_output_path, 
        output_json_file=None, with_defaults=False):
    """Store predictions derived from cTAKES in the supplied output file,
    and return a triple of (results, errors, baseline_results) if there
    are gold annotations in the supplied input_json_file)
    """
    id_text_pairs = structurx.read_prescriptions_without_gold(input_json_file)
    preds = get_ctakes_predictions(id_text_pairs, ctakes_output_path, with_defaults)
    if output_json_file:
        structurx.store_structured_instructions(preds, id_text_pairs, output_json_file)
    id_testpreddict_pairs = structurx.convert_instructions_to_dict(preds)
    input_json_file.seek(0)
    return evaluate.score_instructions_from_json(
        input_json_file, id_testpreddict_pairs)


def write_scripts_for_ctakes(id_text_pairs, ctakes_holding_path):
    """Write plain-text files (one per file) for subsequent processing with the 
    cTAKES GUI.
    """
    observed_text = set()
    for sid, script_text in id_text_pairs:
        if script_text in observed_text:
            continue
        out_fname = path.join(ctakes_holding_path, 'rx_%s' % sid)
        with codecs.open(out_fname, 'w', encoding='UTF-8') as f:
            f.write(_get_med_prefixed(script_text))

def _get_med_prefixed(script_text):
    return CTAKES_MED_PREFIX + script_text + '\n'
    

def read_ctakes_predictions(input_path, defaults=None):
    if defaults is None:
        defaults = {}
    med_ann_prefix = 'edu.mayo.bmi.uima.core.type.refsem.'
    preds = {}
    for fname in glob.glob(path.join(input_path, '*')):
        root = elemtree.parse(fname)
        sofa_elem = root.find('uima.cas.Sofa')
        sent_text = sofa_elem.get('sofaString')
        dosage_units = set()
        amounts = set()
        periods = set()
        doses_per_periods = set()
        for child in root.iter():
            if not child.tag.startswith(med_ann_prefix):
                continue
            tag_stem = child.tag[len(med_ann_prefix):]
            logger.debug("Found tag stem %r" % tag_stem)
            if tag_stem == 'MedicationDosage':
                dosage_val = child.get('value', None)
                if dosage_val:
                    amounts.add(float(dosage_val))
            elif tag_stem == 'MedicationForm':
                unit = child.get('value', None)
                if unit:
                    dosage_units.add(unit)
            elif tag_stem == 'MedicationStrength':
                unit = child.get('unit', None)
                if unit:
                    dosage_units.add(unit)
                amount_raw = child.get('number', None)
                if amount_raw:
                    amount = numbers.written_num_to_float(amount_raw)
                    amounts.add(amount)
            elif tag_stem == 'MedicationFrequency':
                freq_raw = child.get('number', None)
                if freq_raw:
                    dose_freq = numbers.written_num_to_float(freq_raw)
                    logger.debug("Found frequency - raw: %r; conv: %r" % 
                        (freq_raw, dose_freq))
                    doses_per_periods.add(dose_freq)
                else:
                    logger.info("No freq number found where expected for %r" % sent_text)
                    doses_per_periods.add(1)
                freq_unit = child.get('unit', None)
                if freq_unit:
                    period_hours = structurx.PERIOD_NAMES_TO_HOURS.get(
                        freq_unit, None)
                    logger.debug("Found frequency unit - raw: %r, num hours: %r" % 
                        (freq_unit, period_hours))
                    if period_hours is not None:
                        period_days = period_hours / 24.0
                        periods.add(period_days)
                else:
                    logger.info("No freq unit found where expected for %r" % sent_text)

        def get_single_value(all_vals, name, default=None):
            if len(all_vals) == 1:
                return all_vals.pop()
            elif len(all_vals) > 1:
                warnings.warn("Multiple %s found for %r: %r" % 
                    (name, sent_text, all_vals))
            else:
                logger.debug("No %s found for %r" % (name, sent_text))
            return default

        dosage_unit = get_single_value(dosage_units, 'dosage_units', '')
        amount = get_single_value(amounts, 'amounts')
        amount_info = structurx.DosageAmountInfo(dosage_unit, amount, amount)
        doses_per_period = get_single_value(doses_per_periods, 
            'doses_per_periods', defaults.get('doses_per_period', None))
        period_days = get_single_value(periods, 'periods', 
            defaults.get('period_days', None))
        if doses_per_period is not None and period_days is not None:
            freq_info = structurx.PerPeriodFrequency(doses_per_period, period_days)
        else:
            logger.debug("No frequency information found for %r" % sent_text)
            freq_info = None
        preds[sent_text] = (amount_info, freq_info)
    return preds


def get_ctakes_predictions(id_text_pairs, ctakes_output_path, with_defaults=False):
    if with_defaults:
        defaults = {'doses_per_period': 1, 'period_hours': 24}
    else:
        defaults = None
    preds = read_ctakes_predictions(ctakes_output_path, defaults)
    outputs = []
    for sid, script_text in id_text_pairs:
        try:
            pred_for_text = preds[_get_med_prefixed(script_text)]
        except KeyError:
            warnings.warn("No match found for '%s'" % script_text)
            continue
        amt_info, freq_info = pred_for_text
        dosage_info = (amt_info, freq_info)
        outputs.append((sid, dosage_info))
    return outputs



def write_scripts_for_ctakes_from_json(input_json_file, ctakes_holding_path):
    id_text_pairs = structurx.read_prescriptions_without_gold(input_json_file)
    write_scripts_for_ctakes(id_text_pairs, ctakes_holding_path)