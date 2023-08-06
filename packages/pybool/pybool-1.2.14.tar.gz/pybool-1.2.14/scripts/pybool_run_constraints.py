#!/usr/bin/python
#
# Copyright John Reid 2010, 2011
#


"""
Find good networks.
"""

import logging, time, sys, numpy as N
from optparse import OptionParser
from pybool import io, network
from collections import defaultdict




def run_constraints(meta_data, options, num_engines=1, engine_id=-1):
    """
    Generate and evaluate networks
    """
    import copy, logging
    from collections import defaultdict
    from pybool import network
    logging.info('Running constraints %d engines id=%d', num_engines, engine_id)
    num_evaluated = 0
    mismatches = 0
    broken_condition_counts = defaultdict(int)
    default_networks = list() # networks that satisfy the constraints in the wild-type
    all_condition_networks = list() # networks that satisfy the constraints in all conditions
    network_generator = network.BooleanNetworkGenerator(meta_data)
    for i, net in enumerate(network_generator()):
    
        # only test this network if we are not running in parallel or its index matches ours modulo number of engines.
        if num_engines < 2 or (i % num_engines == engine_id):
            broken_condition, mm = network.evaluate_all_conditions(net)
            broken_condition_counts[broken_condition] += 1
            if meta_data.default_condition != broken_condition:
                default_networks.append(copy.deepcopy(net))
            if None == broken_condition:
                all_condition_networks.append(copy.deepcopy(net))
            mismatches += mm
            num_evaluated += 1
    
        if options.max_to_try == i+1:
            break
    
    return num_evaluated, mismatches, broken_condition_counts, default_networks, all_condition_networks
        

def add_default_dicts(to_add_to, added):
    for key, value in added.iteritems():
        to_add_to[key] += value
        
        
        
logging.basicConfig(level=logging.INFO, format="%(message)s")

#
# parse arguments
#
usage = 'USAGE: %s <constraints module>' % sys.argv[0]
parser = OptionParser(usage=usage)
parser.add_option(
    "-p",
    "--parallel",
    dest="parallel",
    action='store_true',
    help="Use ipython controller and engines to run in parallel."
)
parser.add_option(
    "-o",
    "--output-dir",
    default='pyboolOutput',
    help="Directory to store output in."
)
parser.add_option(
    "-m",
    dest="max_to_try",
    default=None,
    type='int',
    help="Maximum number of networks to try. 0 for all."
)
parser.add_option(
    "--plot",
    dest="plot_networks",
    type='int',
    default=0,
    help="Number of networks to plot, with their realisations. -1 for all, 0 for none."
)
parser.add_option(
    "--black-and-white",
    dest="black_and_white",
    action='store_true',
    help="Plot graphs in black and white."
)
parser.add_option(
    "--use-LaTeX",
    dest="use_latex",
    action='store_true',
    help="Plot publication quality graphs using dot2tex and the LaTeX tikz package."
)
parser.add_option(
    "-F",
    dest="formats",
    action='append',
    default=['png'],
    help="Plot graphs in given format (e.g. png, eps, svg, pdf). You can have more than one -F option on the command line."
)
options, args = parser.parse_args()
if len(args) != 1:
    parser.print_help()
    raise RuntimeError(usage)
logging.info('Options:')
for option in parser.option_list:
    if option.dest:
        logging.info('%32s: %-32s * %s', option.dest, str(getattr(options, option.dest)), option.help)
constraints_file = args[0]
io.ensure_dir_exists(options.output_dir)


logging.info('Importing constraints from python module %s', constraints_file)
exec 'import %s as constraints' % constraints_file


#
# Set up meta-data
#
meta_data = constraints.MetaData()
io.summarise_meta_data(meta_data)
restrictions_graph = io.graph_restrictions(meta_data, options)
if restrictions_graph:
    io.write_graph(restrictions_graph, io.output_file(options, 'net-restrictions'), options)




#
# Run the constraints
#
start = time.time()
if options.parallel:
    # find out how many engines we have
    from IPython.kernel import client
    mec = client.MultiEngineClient()
    mec_ids = mec.get_ids()
    logging.info('Parallelising constraints on to %d engines.' % len(mec_ids))
    
    # push python objects to engines
    mec.push(dict(meta_data=meta_data, options=options))
    mec.push_function(dict(run_constraints=run_constraints))
    
    # run constraints and wait for results
    pr_list = [
        mec.execute('results = run_constraints(meta_data, options, %d, %d)' % (len(mec_ids), i), targets=(_id,), block=False)
        for i, _id in enumerate(mec_ids)
    ]
    mec.barrier(pr_list)
    
    # gather results from engines
    results = mec.pull('results')
    num_evaluated = 0
    mismatches = 0
    broken_condition_counts = defaultdict(int)
    default_networks = list() # networks that satisfy the constraints in the wild-type
    all_condition_networks = list() # networks that satisfy the constraints in all conditions
    for _num_evaluated, _mismatches, _broken_condition_counts, _default_networks, _all_condition_networks in results:
        num_evaluated += _num_evaluated
        mismatches += _mismatches
        add_default_dicts(broken_condition_counts, _broken_condition_counts)
        default_networks += _default_networks
        all_condition_networks += _all_condition_networks
else:
    num_evaluated, mismatches, broken_condition_counts, default_networks, all_condition_networks = run_constraints(meta_data, options)
elapsed = time.time() - start



#
# Log info about what happened
#
logging.info('Evaluated %d networks in %.1f seconds. %.1f/sec', num_evaluated, elapsed, num_evaluated/elapsed)
logging.info('Total mismatches = %d', mismatches)
logging.info(
    'Found %d networks which match the default condition "%s" (%d distinct Js).',
    len(default_networks),
    meta_data.default_condition,
    len(list(network.filter_unique_Js(default_networks)))
)
logging.info(
    'Found %d consistent networks which match all conditions (%d distinct Js).',
    len(all_condition_networks),
    len(list(network.filter_unique_Js(all_condition_networks)))
)
for condition in meta_data.conditions:
    logging.info('Condition broken count: %7s = %d', condition, broken_condition_counts[condition])



#
# Pickle good networks
#
import cPickle
all_conditions_filename = 'all-conditions-networks.pickle'
logging.info('Pickling good networks to %s', all_conditions_filename)
cPickle.dump(all_condition_networks, open(io.output_file(options, all_conditions_filename), 'w'))



#
# Plot some network realisations if requested
#
if options.plot_networks:
    logging.info('Plotting %s network(s) and realisations.', options.plot_networks == -1 and 'all' or str(options.plot_networks))
    import pylab as P
    #io.configure_matplotlib_for_tex()
    condition = meta_data.default_condition
    P.close('all')
    for i, net in enumerate(all_condition_networks[:options.plot_networks]):
        
        # plot realisations
        fig = io.plot_network_realisations(net)
        P.savefig(io.output_file(options, 'net-realisations-%03d.eps' % (i+1)))
        P.savefig(io.output_file(options, 'net-realisations-%03d.png' % (i+1)))
        P.close()

        # graph network
        graph = io.graph_network(net, options)
        if graph:
            io.write_graph(graph, io.output_file(options, 'net-%003d' % (i+1)), options)


#
# Summarise possible regulations
#
possible_Js = io.summarise_possible_networks(meta_data, all_condition_networks)
consistent_graph = io.graph_restrictions(meta_data, options, possible_Js)
if consistent_graph:
    io.write_graph(consistent_graph, io.output_file(options, 'net-consistent'), options)
