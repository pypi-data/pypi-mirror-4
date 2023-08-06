from collections import namedtuple, defaultdict

try:
    import json
except ImportError:
    import simplejson as json # python 2.5

PERIOD_NAMES_TO_HOURS = {
    'hour': 1,
    'hourly': 1, 
    'day': 24,
    'daily': 24,
    'week': 7 * 24,
    'weekly': 7 * 24,
    'fortnight': 14 * 24,
    'month': 24 * 365.0 / 12 
}

PerPeriodFrequency = namedtuple(
  'PerPeriodFrequency', ['doses_per_period', 'period_days'])
SeparatedDosesFrequency = namedtuple(
  'SeparatedDosesFrequency', ['target_sep_min_hours', 'target_sep_max_hours'])


class DosageAmountInfo(object):
    def __init__(self, dosage_unit, dosage_min, dosage_max, when_required=False):
        self.dosage_unit = dosage_unit
        self.dosage_min = dosage_min
        self.dosage_max = dosage_max
        self.when_required = when_required
    
    def __repr__(self):
        attrib_vals = u', '.join('%s=%r' % (att, getattr(self, att))
            for att in ('dosage_unit', 'dosage_min', 'dosage_max', 'when_required'))
        return '%s(%s)' % (self.__class__.__name__, attrib_vals)
    
    def __eq__(self, other):
        attribs = ['dosage_unit', 'dosage_min', 'dosage_max', 'when_required']
        return all(getattr(self, attr) == getattr(other, attr) for attr in attribs) 
    
    def __ne__(self, other):
        return not self.__eq__(other)


def read_prescriptions_without_gold(json_file):
    id_text_pairs = json.load(json_file)
    return [data[:2] for data in id_text_pairs] # ignore third if present
    
def read_prescriptions_with_gold(json_file):
    id_text_pairs = json.load(json_file)
    return [data + ([None] if len(data) < 3 else []) for data in id_text_pairs] 


def store_structured_instructions(id_instruction_pairs, id_text_pairs, output_file):
    dumpable = []
    assert len(id_instruction_pairs) == len(id_text_pairs), "Length mismatch in text/instructions"
    id_instructiondict_pairs = convert_instructions_to_dict(id_instruction_pairs)
    for pid_instructions, pid_text in zip(id_instructiondict_pairs, id_text_pairs):
        pid, instruc_attrib = pid_instructions
        pid2, text = pid_text
        assert pid == pid2, "Prescription ID mismatch"
        dumpable.append((pid, text, instruc_attrib))
    json.dump(dumpable, output_file, indent=2)


def convert_instructions_to_dict(id_instruction_pairs):
    amount_attribs = ['dosage_unit', 'dosage_min', 'dosage_max', 'when_required']
    freq_attribs = ['doses_per_period', 'period_days', 
        'target_sep_min_hours', 'target_sep_max_hours']
    for pid_instructions in id_instruction_pairs:
        pid, instructions = pid_instructions
        instruc_attrib = {}
        amount_info, freq_info = instructions
        for attr in amount_attribs:
            instruc_attrib[attr] = getattr(amount_info, attr)
        for attr in freq_attribs:
            if hasattr(freq_info, attr):
                instruc_attrib[attr] = getattr(freq_info, attr)
        yield pid, instruc_attrib