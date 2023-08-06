WRITTEN_NUMS_TO_ARABIC = {
  'one': '1', 'two': '2', 'three': '3', 'four': '4', 'five': '5',
  'six': '6', 'seven': '7', 'eight': '8', 'nine': '9', 'ten': '10',
  'half': '0.5'}

def written_num_to_value(form, valtype):
    arabic_val = WRITTEN_NUMS_TO_ARABIC.get(form.lower(), form.lower())
    try:
        numeric_val = valtype(arabic_val)
    except ValueError:
        warnings.warn("Could not convert '%s' to %s" % (form, valtype.__name__))
        return None
    return numeric_val

def written_num_to_float(form):
    return written_num_to_value(form, float)

def written_num_to_int(form):
    return written_num_to_value(form, int)
