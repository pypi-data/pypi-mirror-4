#!/usr/bin/env python
import sys
import optparse
from contextlib import nested
from os import path
import os

from structurx import config, deprules, ctakes

def print_results(results):
    for fieldgroup, acc in results:
        print u"%s:\t%s" % (', '.join(fieldgroup) if fieldgroup else 'ALL', acc)


def main():
    usage = "usage: %prog [options] input_path output_path"
    epilog = "Run with '-d' for help on input and output formats"
    parser = optparse.OptionParser(usage=usage, epilog=epilog)
    parser.add_option('-c', '--parse-cache-path', dest='cache_path',
        help='Cache parses (using deprules mode) to this location instead of '
            'inputfile.cached-parses.json; ')
    parser.add_option('-n', '--no-cache', dest='do_cache',
        action='store_false', default=True)
    parser.add_option('-d', '--detailed-help', action='store_true', 
        dest='detailed_help')
    parser.add_option('-m', '--mode', dest='mode', 
        help="Method to use to determine values (one of 'deprules', 'ctakes')"
        " (default: %default)", default='deprules')
    parser.add_option('--ctakes-holding-dir', dest='ctakes_holding_dir',
        help="Directory to hold temporary files containing sentences for cTAKES")
    parser.add_option('--ctakes-output-dir', dest='ctakes_output_dir',
        help="Directory holding output from  cTAKES")
    parser.add_option('--no-ctakes-defaults', dest='add_ctakes_defaults',
        action='store_false', default=True)
        
    options, args = parser.parse_args()
    if options.detailed_help:
        parser.print_usage()
        config.show_settings_help()
        print DETAILED_HELP
        return
    try:
        input_fname, output_fname = args
    except ValueError:
        parser.error("Exactly two arguments are required")
    
    if options.mode == 'deprules':
        if options.do_cache:
            if options.cache_path is None:
                options.cache_path = input_fname + '.parsecache.json'
        else:
            options.cache_path = None
        with nested(open(input_fname), open(output_fname, 'w')) as (inf, outf):
            eval_res = deprules.interpret_from_json_and_store(inf, outf, options.cache_path)
            if eval_res:
                results, errors, baseline = eval_res
                print "RESULTS:"
                print_results(results)
                print "\nMAJORITY BASELINE:"
                print_results(baseline)
            else:
                print "No results, as gold annotations were not found in %s" % input_fname
    elif options.mode == 'ctakes':
        if not options.ctakes_output_dir:
            options.ctakes_output_dir = input_fname + '-ctakes-output'
        if path.exists(options.ctakes_output_dir) and os.listdir(options.ctakes_output_dir):
            # cTakes has already been run, it seems
            print >> sys.stderr, \
                "Found files in %s; assuming cTAKES has been run" % options.ctakes_output_dir
            with nested(open(input_fname), open(output_fname, 'w')) as (inf, outf):
                eval_res = ctakes.store_and_eval_ctakes_predictions(inf, 
                    options.ctakes_output_dir, outf, options.add_ctakes_defaults)
                if eval_res:
                    results, errors, baseline = eval_res
                    print "RESULTS:"
                    print_results(results)
                    print "\nMAJORITY BASELINE:"
                    print_results(baseline)
                else:
                    print "No results, as gold annotations were not found in %s" % input_fname

        else:
            if not options.ctakes_holding_dir:
                options.ctakes_holding_dir = input_fname + '-ctakes-holding'
            if not path.exists(options.ctakes_holding_dir):
                os.mkdir(options.ctakes_holding_dir)
            if not path.exists(options.ctakes_output_dir):
                os.mkdir(options.ctakes_output_dir)
            with open(input_fname) as inf:
                ctakes.write_scripts_for_ctakes_from_json(inf, options.ctakes_holding_dir)
                print ctakes.POST_WRITE_INSTRUCTIONS % (
                    options.ctakes_holding_dir, options.ctakes_output_dir)
    else:
        parser.error("Invalid mode '%s'" % options.mode)

DETAILED_HELP = """
The expected input file format is JSON; the data 
should be an arbitrarily long list of pairs or triples (i.e. lists of length 2 or 3); 
the first element in each list is the (preferably unique) ID, and the second 
element is the prescription text, possible consisting of multiple 
sentences. For example:

[
    [1, "Take ONE to TWO tablets TWICE a day. Keep refrigerated."], 
    [2, "Take TWO capsules every FOUR to SIX hours when required"]
]

The optional third element is the gold values for the annotation, which is the 
same format as the output format described below.

The output format is the same, except the third element
will always be present. This third element is a hash of relevant prescription information, 
which is selected from the following fields:

**DOSAGE**
[Fields related to dosage size]
* dosage_min: (AmtMin) The minimum allowed quantity of the drug per dosage, 
    w/o units, such as '1' or '50'.
* dosage_max: (AmtMax) The maximum allowed quantity of the drug per dosage,
    w/o units. May be the same as DoseAmtMin.
* dosage_units: (AmtUnits) The unit in which DoseAmtMin and DoseAmtMax are 
    measured, such as 'tablet' or 'mg'.
* when_required: (Opt) Whether the dosages are optional.

**FREQUENCY - PER WINDOW**
[Fields related to dosage frequency, for regimens specified as dosages within a
    time window such as 'twice daily' or 'three times per week';]
* period_days: (PerWdwDays) The length in days of the dosage window.
* doses_per_period: (DosesPerWdw) How many dosages should occur in the given 
    time window. 

**FREQUENCY - SEPARATED DOSES**
[Dosage frequency fields, For regimens specified by time-separation, such as
    'every 4-6 hours']
* target_sep_min_hours: (SepMinHrs) The minimum length of separation in hours.
* target_sep_max_hours: (SepMaxHrs) Specifies the upper rather than lower 
    range of dosage separation in hours.

The CamelCased alternate names are those used in [1]; 
Please refer to this paper for further explanations of the fields.

If the mode selected is 'deprules', it uses the cascade of rules applied to the 
dependency parses of the sentences described in [1]. If the mode is 'ctakes', it 
applies the cTAKES drug NER pipeline, using the methods described in [2]. In
each case upstream software is required -- ClearParser for the first and
cTAKES for the second. If you attempt to run the script, configuration
instructions will be supplied.

[1] A. MacKinlay and K. Verspoor. 2012. Extracting structured information from 
 free-text medication prescriptions using dependencies. DTMBIO 2012
[2] A. MacKinlay and K. Verspoor. 2013. A Comparison of Strategies for 
 Extracting Structured Information from Free-Text Medication Prescriptions.
 LOUHI 2013.

"""


if __name__ == "__main__":
    main()