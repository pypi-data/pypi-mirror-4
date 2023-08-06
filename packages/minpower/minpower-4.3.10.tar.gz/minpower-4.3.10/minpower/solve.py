"""
Power systems optimization problem solver
for ED, OPF, UC, and SCUC problems. The :mod:`solve`
module contains the top-level commands for creating
problems and solving them.
"""

import traceback
import sys, os, logging, subprocess
import time as timer
import argparse
import pdb

from config import user_config, parse_command_line_config
from commonscripts import joindir, StreamToLogger, set_trace
import powersystems, get_data, stochastic, results
from standalone import store_times, init_store, get_storage, repack_storage

def _set_store_filename(pid=None):
    fnm = 'stage-store.hd5'
    if user_config.output_prefix or user_config.pid:
        fnm = '{}-{}'.format(pid, fnm)

    user_config.store_filename = joindir(user_config.directory, fnm)

def solve_multistage_standalone(power_system, times, scenario_tree, data):

    stage_times = times.subdivide(
        user_config.hours_commitment, user_config.hours_overlap)

    pid = user_config.pid if user_config.pid else os.getpid()
    has_pid = user_config.output_prefix or user_config.pid

    if user_config.standalone_restart:
        # get the last stage in storage
        storage = get_storage()
        stg_start = len(storage['solve_time'].dropna())
        logging.info('Restarting on stage {}'.format(stg_start))
        stage_times_remaining = stage_times[stg_start:]
    else:
        storage = init_store(power_system, stage_times, data)
        stage_times_remaining = stage_times
        stg_start = 0
    
    for stg, t_stage in enumerate(stage_times_remaining):
        logging.info('Stage starting at {}'.format(t_stage.Start.date()))
        # store current stage times
        storage = store_times(t_stage, storage)
        storage.close()
        storage = None
        command = 'standalone_minpower {dir} {stg} {pid} {db}'.format(
                dir=user_config.directory, stg=stg + stg_start,
                pid='--pid {}'.format(pid) if has_pid else '',
                db='--debugger' if user_config.debugger else '')
        try: subprocess.check_call(command, shell=True, stdout=sys.stdout)
        except AttributeError:
            # HACK - avoid error when nose hijacks sys.stdout
            subprocess.check_call(command, shell=True)

    repack_storage()
    storage = get_storage()
    return storage, stage_times

def standaloneUC():
    '''the hook for the ``standalone_minpower`` script'''
    from standalone import store_state, load_state

    parser = argparse.ArgumentParser()
    parser.add_argument('directory', type=str, help='the problem direcory')
    parser.add_argument('stg', type=int, help='the stage number')
    parser.add_argument('--pid', default='',
        help='the process id of the parent')
    parser.add_argument('--debugger', action='store_true', default=False,
        help='do some debugging')        

    args = parser.parse_args()
    stg = args.stg
    user_config.directory = args.directory
    user_config.pid = args.pid

    try:          
        _set_store_filename(args.pid)    
        # load stage data
        power_system, times, scenario_tree = load_state()

        # override the stored config with the current command line config
        user_config.directory = args.directory
        user_config.debugger = args.debugger

        _setup_logging(args.pid)
      
        sln = create_solve_problem(power_system, times, scenario_tree, stage_number=stg)

        store = store_state(power_system, times, sln)
        store.close()
    except:
        if user_config.debugger or args.debugger:
            __, __, tb = sys.exc_info()
            traceback.print_exc()
            pdb.post_mortem(tb)            
        else:
            raise

    return

def solve_problem(datadir='.',
        shell=True,
        problemfile=False,
        csv=True,
        ):
    """
    Solve a optimization problem specified by spreadsheets in a directory.
    Read in data, create and solve the problem, and return solution.
    The problem type is determined by the data.
    All options are set within `user_config`.
    """
    user_config.directory = datadir
    
    pid = user_config.pid if user_config.pid else os.getpid()
        
    _set_store_filename(pid)
    _setup_logging(pid)

    if user_config.standalone_restart:
        store = get_storage()
        debugger = user_config.debugger  # preserve debugger state
        user_config.update(store['configuration'])
        user_config.debugger = debugger
        user_config.standalone_restart = True  # preserve restart state
        store.close()

    logging.debug(dict(user_config))
    
    start_time = timer.time()
    logging.debug('Minpower reading {}'.format(datadir))
    generators, loads, lines, times, scenario_tree, data = get_data.parsedir()
    logging.debug('data read')
    power_system = powersystems.PowerSystem(generators,loads,lines)

    logging.debug('power system initialized')
    if times.spanhrs <= user_config.hours_commitment + user_config.hours_overlap:
        solution = create_solve_problem(power_system, times, scenario_tree)
    else: #split into multiple stages and solve
        if user_config.standalone:
            stage_solutions, stage_times = solve_multistage_standalone(
                power_system, times, scenario_tree, data)
        else:
            stage_solutions, stage_times = solve_multistage(
                power_system, times, scenario_tree, data)
        solution = results.make_multistage_solution(
            power_system, stage_times, stage_solutions)

    if shell:
        if user_config.output_prefix or user_config.pid:
            stdout = sys.stdout
            sys.stdout = StreamToLogger()
            solution.show()
            sys.stdout = stdout
        solution.show()
    if csv and not user_config.standalone: solution.saveCSV()
    if user_config.visualization: solution.visualization()
    logging.info('total time: {}s'.format(timer.time()-start_time))

    if user_config.on_complete_script:
        os.system(user_config.on_complete_script)

    return solution


def solve_multistage(power_system, times, scenario_tree=None, data=None):
    stage_times = times.subdivide(
        user_config.hours_commitment, user_config.hours_overlap)

    stage_solutions = []

    for stg, t_stage in enumerate(stage_times):
        logging.info('Stage starting at {}'.format(t_stage.Start.date()))
        # solve
        solution = create_solve_problem(
            power_system, t_stage, scenario_tree, stg)
        # add to stage solutions
        stage_solutions.append(solution)
        # reset model
        power_system.reset_model()
        # set inital state for next stage
        if stg < len(stage_times)-1:
            power_system.set_initialconditions(stage_times[stg+1].initialTime)

    return stage_solutions, stage_times


def create_solve_problem(power_system, times, scenario_tree=None,
    stage_number=None, rerun=False):
    '''create and solve an optimization problem.'''
    
    create_problem(power_system, times, scenario_tree,
        stage_number, rerun)
    
    instance = power_system.solve_problem(times)

    logging.debug('solved... get results')

    sln = results.make_solution(power_system, times)
    
    power_system.disallow_shedding()

    # resolve with observed power and fixed status
    if sln.is_stochastic:
        power_system.resolve_stochastic_with_observed(instance, sln)
    elif user_config.deterministic_solve or user_config.perfect_solve:
        power_system.resolve_determinisitc_with_observed(sln)
   
    if len(times)>1:
        power_system.get_finalconditions(sln)

        power_system.disallow_shedding()
        sln.stage_number = stage_number
    
    return sln

def create_problem(power_system, times, scenario_tree=None,
    stage_number=None, rerun=False):
    """Create an optimization problem."""

    logging.debug('initialized problem')
    power_system.create_variables(times)
    logging.debug('created variables')
    power_system.create_objective(times)
    logging.debug('created objective')
    power_system.create_constraints(times)
    logging.debug('created constraints')

    if scenario_tree is not None and sum(scenario_tree.shape) > 0 and not rerun:
        stochastic.construct_simple_scenario_tree(
            power_system, times, time_stage=stage_number)
        stochastic.define_stage_variables(power_system, times)
        stochastic.create_problem_with_scenarios(power_system, times)
    return

def _setup_logging(pid=None):
    ''' set up the logging to report on the status'''
    kwds = dict(
        level=int(user_config.logging_level) if not user_config.debugger else logging.DEBUG,
        datefmt='%Y-%m-%d %H:%M:%S',
        format='%(asctime)s %(levelname)s: %(message)s')
    # log to file if pid is set, unless in debugging mode
    if (user_config.output_prefix or user_config.pid) \
        and not user_config.debugger:
        kwds['filename'] = joindir(user_config.directory,
            '{}.log'.format(pid))
    if (user_config.logging_level > 10) and (not 'filename' in kwds):
        # don't log the time if debugging isn't turned on
        kwds['format'] = '%(levelname)s: %(message)s'
    logging.basicConfig(**kwds)


def main():
    '''
    The command line interface for minpower. For more info use:
    ``minpower --help``
    '''

    args = parse_command_line_config(
        argparse.ArgumentParser(description='Minpower command line interface'))
    
    directory = user_config.directory

    if not os.path.isdir(directory):
        msg = 'There is no folder named "{}".'.format(directory)
        raise OSError(msg)
    
    if args['profile']:
        print 'run profile'
        import cProfile
        prof = cProfile.Profile()
        prof.runcall(solve_problem, directory)
        prof.dump_stats('minpower.profile')

    else:
        #solve the problem with those arguments
        try: solve_problem(directory)
        except:
            if args['debugger']:
                __, __, tb = sys.exc_info()
                traceback.print_exc()
                pdb.post_mortem(tb)
            else: raise

# for use in dev
if __name__=='__main__': main()
