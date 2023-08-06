"""
Get data from spreadsheet files and parse it into
:class:`~Generator`, :class:`~powersystems.Load`,
:class:`~powersystems.Bus`, and :class:`~powersystems.Line` objects.
Also extract the time information and create all
    :class:`~schedule.Timelist` objects.
"""
import pandas as pd
from pandas import DataFrame, Timestamp, read_csv
from glob import glob
from collections import OrderedDict
    
import powersystems
from schedule import (just_one_time, get_schedule,
                      TimeIndex, make_constant_schedule)
from commonscripts import (joindir, drop_case_spaces, set_trace)

from powersystems import PowerSystem
from generators import (Generator,
                        Generator_Stochastic, Generator_nonControllable)
from config import user_config

import os
import logging

fields = dict(
    Line=[
        'name',
        'tobus',
        'frombus',
        'reactance',
        'pmax'
    ],

    Generator=[
        'name',
        'kind',
        'bus',
        'pmin', 'pmax',
        'power',  # for a non-controllable gen in an ED
        'rampratemin', 'rampratemax',
        'minuptime', 'mindowntime',
        'startupramplimit', 'shutdownramplimit',
        # for a bid points defined gen, noloadcost replaces the constant
        # polynomial
        'noloadcost',
        'costcurveequation', 'heatrateequation',
        'fuelcost',
        'startupcost', 'shutdowncost',
        'faststart',
        'mustrun',
        'sheddingallowed',
    ],

    Load=['name', 'bus', 'power'],
)

# extra fields for generator scheduling and bid specification
# these fields require parsing of additional files
# and result in additional objects being added
# to the Generator after creation
gen_extra_fields = ['observedname', 'forecastname', 'scenariosfilename',
                    'scenariosdirectory', 'costcurvepointsfilename']

fields_initial = [
    'status',
    'power',
    'hoursinstatus']


def nice_names(df):
    '''drop the case and spaces from all column names'''
    return df.rename(columns=
                     dict([(col, drop_case_spaces(col)) for col in df.columns]))


def parse_standalone(storage, times):
    '''load problem info from a pandas.HDFStore'''

    # filter timeseries data to only this stage
    timeseries = storage['data_timeseries'].ix[times.strings.values]

    # add loads
    loads = build_class_list(storage['data_loads'], powersystems.Load,
                             times, timeseries)
    # add generators
    generators = build_class_list(storage['data_generators'], Generator,
                                  times, timeseries)
    # add lines
    lines = build_class_list(storage['data_lines'], powersystems.Line,
                             times, timeseries)

    power_system = PowerSystem(generators, loads, lines)

    gen = power_system.get_generator_with_scenarios()
    if gen:
        # TODO - maybe only extract current day's values here
        scenario_values = storage['data_scenario_values']
        gen.scenario_values = scenario_values
    else:
        scenario_values = pd.Panel()

    return power_system, times, scenario_values


def _load_raw_data():
    """import data from spreadsheets"""
    datadir = user_config.directory

    if not os.path.isdir(datadir):
        raise OSError('data directory "{d}" does not exist'.format(d=datadir))
    [file_gens, file_loads, file_lines, file_init] = \
        [joindir(datadir, filename) for filename in (
            user_config.file_gens,
            user_config.file_loads, 
            user_config.file_lines, 
            user_config.file_init)]

    generators_data = nice_names(read_csv(file_gens))
    loads_data = nice_names(read_csv(file_loads))

    try:
        lines_data = nice_names(read_csv(file_lines))
    except Exception:
        lines_data = DataFrame()

    try:
        init_data = nice_names(read_csv(file_init))
    except Exception:
        init_data = DataFrame()

    return generators_data, loads_data, lines_data, init_data


def _parse_raw_data(generators_data, loads_data, lines_data, init_data):
    # create times
    timeseries, times, generators_data, loads_data = setup_times(
        generators_data, loads_data)

    # add loads
    loads = build_class_list(loads_data, powersystems.Load, times, timeseries)

    # data modifiers
    if user_config.pmin_multiplier != 1.0:
        generators_data['pmin'] *= user_config.pmin_multiplier
        invalid_pmin = (generators_data.pmin > generators_data.pmax)
        if invalid_pmin.any():
            logging.warning('Pmin scaling resulted in Pmin>Pmax. ' +
                            'Setting Pmin=Pmax for these {} generators.'.format(
                                invalid_pmin.sum()))
            generators_data.ix[invalid_pmin, 'pmin'] = \
                generators_data.ix[invalid_pmin, 'pmax']

    if user_config.ramp_limit_multiplier != 1.0:
        generators_data['rampratemin'] *= user_config.ramp_limit_multiplier
        generators_data['rampratemax'] *= user_config.ramp_limit_multiplier

    if user_config.ignore_minhours_constraints:
        generators_data['minuptime'] = 0
        generators_data['mindowntime'] = 0
    if user_config.ignore_ramping_constraints:
        generators_data['rampratemax'] = None
        generators_data['rampratemin'] = None
    if user_config.ignore_pmin_constraints:
        generators_data['pmin'] = 0

    # add generators
    generators = build_class_list(
        generators_data, Generator, times, timeseries)

    # add lines
    lines = build_class_list(lines_data, powersystems.Line)
    # add initial conditions
    setup_initialcond(init_data, generators, times)

    # get scenario values (if applicable)
    scenario_values = setup_scenarios(generators_data, generators, times)

    # also return the raw DataFrame objects
    data = dict(
        generators=generators_data,
        loads=loads_data,
        lines=lines_data,
        init=init_data,
        timeseries=timeseries,
        scenario_values=scenario_values,
    )

    return generators, loads, lines, times, scenario_values, data


def parsedir(**filename_kwargs):
    """
    Import data from spreadsheets and build lists of
    :mod:`powersystems` classes.
    """

    generators_data, loads_data, lines_data, init_data = _load_raw_data(
        **filename_kwargs)

    return _parse_raw_data(generators_data, loads_data,
                           lines_data, init_data)


def setup_initialcond(data, generators, times):
    '''
    Take a list of initial conditions parameters and
    add information to each :class:`~Generator` object.
    '''
    if len(times) <= 1:
        return  # for UC,ED no need to set initial status

    if len(data) == 0:
        logging.warning('''No generation initial conditions file found.
            Setting to defaults.''')
        for gen in generators:
            gen.set_initial_condition()
        return

    # begin by setting initial condition for all generators to off
    for g in generators:
        g.set_initial_condition(status=False, power=0)

    names = [g.name for g in generators]

    if not 'name' in data.columns:
        # assume they are in order
        data['name'] = names

    if 'power' not in data.columns:
        raise KeyError('initial conditions file should contain "power".')

    # add initial conditions for generators
    # which are specified in the initial file
    for i, row in data.iterrows():
        g = names.index(row['name'])
        kwds = row[fields_initial].dropna().to_dict()
        generators[g].set_initial_condition(**kwds)
    return


def build_class_list(data, model, times=None, timeseries=None):
    """
    Create list of class instances from the row of a DataFrame.
    """
    datadir = user_config.directory
    is_generator = (model == Generator)

    all_models = []

    if 'schedulename' in data.columns:
        data['schedule'] = None

    for i, row in data.iterrows():
        row_model = model
        row = row.dropna()

        power = row.get('power')
        schedulename = row.get('schedulename')

        if is_generator:
            # get all those extra things which need to be parsed
            observed_name = row.get('observedname')
            forecast_name = row.get('forecastname')

            scenariosfilename = row.get('scenariosfilename')
            scenariosdirectory = row.get('scenariosdirectory')

            if scenariosdirectory and user_config.scenarios_directory:
                # override the scenarios directory with the one \
                # specified in the commandline options
                scenariosdirectory = user_config.scenarios_directory
                data.ix[i,
                        'scenariosdirectory'] = user_config.scenarios_directory

            bid_points_filename = row.get('costcurvepointsfilename')

        if is_generator:
            if schedulename or power or \
                (forecast_name and user_config.deterministic_solve) or \
                    (observed_name and user_config.perfect_solve):
                row_model = Generator_nonControllable
            elif scenariosdirectory or scenariosfilename:
                row_model = Generator_Stochastic

        # warn about fields not in model
        valid_fields = pd.Index(fields[model.__name__] + ['schedulename'])
        if is_generator:
            valid_fields = valid_fields.union(pd.Index(gen_extra_fields))
        invalid_fields = row.index.diff(valid_fields)
        if len(invalid_fields) > 0:
            raise ValueError('invalid fields in model:: {}'.format(
                invalid_fields.tolist()))
            # logging.warning

        kwds = row[row.index.isin(fields[model.__name__])].to_dict()

        # add in any schedules
        if schedulename:
            kwds['schedule'] = timeseries[schedulename]
        elif pd.notnull(power):
            # a constant power schedule
            kwds['schedule'] = make_constant_schedule(times, power)
            kwds.pop('power')

        if is_generator:
            if observed_name:
                kwds['observed_values'] = timeseries[observed_name]

            if user_config.perfect_solve and observed_name:
                # for a perfect information solve forecast = observed
                kwds['schedule'] = kwds['observed_values'] \
                    = timeseries[observed_name]
            elif forecast_name:
                kwds['schedule'] = timeseries[forecast_name]

            if scenariosdirectory:
                try:
                    kwds['observed_values'] = timeseries[observed_name]
                except:
                    raise IOError('''you must provide an
                        observed filename for a rolling stochastic UC''')

            # add a custom bid points file with {power, cost} columns
            if bid_points_filename:
                kwds['bid_points'] = read_bid_points(
                    joindir(datadir, bid_points_filename))
                kwds['costcurveequation'] = None

        try:
            obj = row_model(index=i, **kwds)
        except TypeError:
            print '{} model got unexpected parameter'.format(model)
            raise

        all_models.append(obj)

    return all_models


def read_bid_points(filename):
    bid_points = read_csv(filename)
    # return a dataframe of bidpoints
    return bid_points[['power', 'cost']].astype(float)


def setup_times(generators_data, loads_data):
    """
    Create a :class:`~schedule.TimeIndex` object
    from the schedule files.

    Also create a unified DataFrame of all the schedules, `timeseries`.

    If there are no schedule files (as in ED,OPF),
    create an index with just a single time.
    """
    fcol = 'schedulefilename'
    ncol = 'schedulename'

    loads_data[ncol] = None
    generators_data[ncol] = None

    if fcol not in loads_data.columns:
        loads_data[fcol] = None
    if fcol not in generators_data.columns:
        generators_data[fcol] = None

    datadir = user_config.directory

    timeseries = {}

    def filter_notnull(df, col):
        return df[df[col].notnull()]

    for i, load in filter_notnull(loads_data, fcol).iterrows():
        name = 'd{}'.format(i)
        loads_data.ix[i, ncol] = name
        timeseries[name] = get_schedule(joindir(datadir, load[fcol])) * \
            user_config.load_multiplier + user_config.load_adder

    for i, gen in filter_notnull(generators_data, fcol).iterrows():
        name = 'g{}'.format(i)
        generators_data.ix[i, ncol] = name
        timeseries[name] = get_schedule(joindir(datadir, gen[fcol]))

    # handle observed and forecast power
    fobscol = 'observedfilename'
    obscol = 'observedname'
    ffcstcol = 'forecastfilename'
    fcstcol = 'forecastname'

    obs_name = None    
    if fobscol in generators_data:
        generators_data[obscol] = None
        for i, gen in filter_notnull(generators_data, fobscol).iterrows():
            obs_name = 'g{}_observations'.format(i)
            generators_data.ix[i, obscol] = obs_name
            timeseries[obs_name] = get_schedule(joindir(datadir, gen[fobscol]))
            if user_config.wind_multiplier != 1.0:
                timeseries[obs_name] *= user_config.wind_multiplier
                
        generators_data = generators_data.drop(fobscol, axis=1)
    
    fcst_name = None
    if ffcstcol in generators_data:
        generators_data[fcstcol] = None
        for i, gen in filter_notnull(generators_data, ffcstcol).iterrows():
            fcst_name = 'g{}_forecast'.format(i)
            generators_data.ix[i, fcstcol] = fcst_name
            timeseries[fcst_name] = get_schedule(joindir(datadir, gen[ffcstcol])) * \
                user_config.wind_multiplier + user_config.wind_forecast_adder

            if user_config.wind_error_multiplier != 1.0:
                logging.debug('scaling wind forecast error')
                obs_name = 'g{}_observations'.format(i)
                error = timeseries[fcst_name] - timeseries[obs_name]
                timeseries[fcst_name] = timeseries[obs_name] + \
                    error * user_config.wind_error_multiplier

            if (timeseries[fcst_name] < 0).any():
                print timeseries[fcst_name].describe()
                logging.warning('Wind forecast must always be at least zero.')
                timeseries[fcst_name][timeseries[fcst_name] < 0] = 0
                
        generators_data = generators_data.drop(ffcstcol, axis=1)

    generators_data = generators_data.drop(fcol, axis=1)
    loads_data = loads_data.drop(fcol, axis=1)

    if len(timeseries) == 0:
        # this is a ED or OPF problem - only one time
        return DataFrame(), just_one_time(), generators_data, loads_data

    timeseries = DataFrame(timeseries)
    times = TimeIndex(timeseries.index)
    timeseries.index = times.strings.values

    if user_config.wind_capacity_factor != 0:
        if len(filter_notnull(generators_data, obscol)) != 1:
            raise NotImplementedError(
                'wind capacity factor only works with one wind generator')
            
        all_loads = timeseries[filter(lambda col: col.startswith('d'),
            timeseries.columns)]

        capf_current = timeseries[obs_name].sum() / all_loads.sum(axis=1).sum()
        
        wind_mult = user_config.wind_capacity_factor / capf_current
        user_config.wind_multiplier = wind_mult

        logging.info('scaling wind from a c.f. of {} to a c.f. of {}'.format(
            capf_current, user_config.wind_capacity_factor
            ))
        timeseries[obs_name] *= wind_mult
        if fcst_name:
            timeseries[fcst_name] *= wind_mult        
        
    return timeseries, times, generators_data, loads_data


def _parse_scenario_day(filename):
    logging.debug('reading scenarios from %s', filename)
    data = read_csv(filename, parse_dates=True, index_col=0)

    # select subset of scenarios
    Nscenarios = user_config.scenarios
    if Nscenarios:
        data = data[data.index < Nscenarios]
        data['probability'] = data['probability'] / sum(data['probability'])

    # return the data with probability column first
    return data[data.columns.drop('probability').insert(0, 'probability')]


def setup_scenarios(gen_data, generators, times):

    col = 'scenariosdirectory'
    scenario_values = pd.Panel()
    if user_config.deterministic_solve or user_config.perfect_solve or \
            (not col in gen_data.columns):
        # a deterministic problem
        return scenario_values

    gen_params = gen_data[gen_data[col].notnull()]
    if len(gen_params) > 1:
        raise NotImplementedError('more than one generator with scenarios.')

    gen = generators[gen_params.index[0]]
    gen.has_scenarios = True

    # directory of scenario values where each file is one day
    scenarios_directory = gen_params['scenariosdirectory'].values[0]

    searchstr = "*.csv"

    filenames = sorted(glob(joindir(user_config.directory,
                                    joindir(scenarios_directory, searchstr))))
    if not filenames:
        raise IOError('no scenario files in "{}"'.format(scenarios_directory))

    alldata = OrderedDict()
    for i, f in enumerate(filenames):
        data = _parse_scenario_day(f)
        # label scenarios for the day with the date
        date = Timestamp(data.columns.drop('probability')[0]).date()
        alldata[date] = data

    # TODO - assumes one hour intervals!!
    hrs = user_config.hours_commitment + user_config.hours_overlap

    # make scenarios into a pd.Panel with axes: day, scenario, {prob, [hours]}
    scenario_values = pd.Panel(
        items=alldata.keys(),
        major_axis=range(max([len(dat) for dat in alldata.values()])),
        minor_axis=['probability'] + range(hrs)
    )

    for day, scenarios in alldata.iteritems():
        if 'probability' == scenarios.columns[-1]:
            # reoder so that probability is the first column
            scenarios = scenarios[
                scenarios.columns[:-1].insert(0, 'probability')]
        # rename the times into just hour offsets
        scenarios = scenarios.rename(columns=dict(zip(scenarios.columns,
            ['probability'] + range(len(scenarios.columns) - 1))))

        # and take the number of hours needed
        scenarios = scenarios[scenarios.columns[:1 + hrs]]
        
        scenario_values[day] = scenarios

    if user_config.wind_multiplier != 1.0:
        scenario_values *= user_config.wind_multiplier
        svt = scenario_values.transpose(2, 1, 0)
        svt['probability'] *= 1 / user_config.wind_multiplier
        scenario_values = svt.transpose(2, 1, 0)

    gen.scenario_values = scenario_values
    # defer scenario tree construction until actual time stage starts
    return scenario_values


def _has_valid_attr(obj, name):
    return getattr(obj, name, None) is not None
