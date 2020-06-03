"""
Python 3.6
common_emip_funcs.py

Common functions used in ESMValTool diagnostic scripts as part of the 
Emissions-MIP (EMIP) project.

Matt Nicholson
19 May 2020
"""
import os
import iris
import logging
import matplotlib.pyplot as plt
import numpy as np
from itertools import groupby, chain

from esmvaltool.diag_scripts.shared import group_metadata, run_diagnostic
from esmvalcore.preprocessor import area_statistics


# === Variable Processing Functions ============================================

class Variables:
    """
    Simple class to hold some variable metadata.
    """
    emiso2 = {'cmor_long_name': 'total emission rate of so2',
              'cesm_long_name': 'surface flux of so2',
              'mip': 'AERmon',
              'ndim': 3}
    emiso4 = {'cmor_long_name': 'total emission rate of so4',
              'cesm_long_name': 'surface flux of so4',
              'mip': 'AERmon',
              'ndim': 3}
    mmrso4 = {'cmor_long_name': 'mass mixing ratio of aerosol so4',
              'cesm_long_name': 'concentration of so4',
              'mip': 'AERmon',
              'ndim': 4}
    emiso2 = {'cmor_long_name': 'total emission rate of so2',
              'cesm_long_name': 'surface flux of so2',
              'mip': 'AERmon',
              'ndim': 3}
    so2 =    {'cmor_long_name': 'so2 volume mixing ratio',
              'cesm_long_name': 'so2 concentration',
              'mip': 'AERmon',
              'ndim': 4}
    rlut =   {'cmor_long_name': 'TOA outgoing longwave radiation',
              'cesm_long_name': 'upwelling longwave flux at TOA',
              'mip': 'Amon',
              'ndim': 3}
    rsut =   {'cmor_long_name': 'TOA outgoing shortwave radiation',
              'cesm_long_name': 'upwelling solar flux at TOA',
              'mip': 'Amon',
              'ndim': 3}


def group_meta_by_var(meta_dict):
    """
    Group a dictionary of variable metadata keyed on the variable's dataset into
    a dictionary keyed on the name of the variable.
    
    Parameters
    ----------
    meta_dict : Dictionary
        Dictionary returned by the ESMValTool preprocessor.
        Key: str 
            Dataset name.
        Val: list of dict
            List of variable metadata dictionaries belonging to the dataset.
            Each dataset variable gets its own dictionary.
            
    Returns
    -------
    Dictionary
        Key: str
            Name of the variable
        Val: list of dict
            Variable metadata from different model runs/configurations contained
            in the original prepreocessor metadata dictionary. 
    """
    # Get list of every value dictionary
    meta_list = list(chain.from_iterable(list(meta_dict.values())))

    # Get dict from list keyed on variable. List of dictionaries must be sorted
    # by the 'group-by' value in order to work properly. 
    meta_list.sort(key=lambda x: x['short_name'])
    var_groups = {k: list(v) for k, v in groupby(meta_list, lambda d: d['short_name'])}
    return var_groups
    
    
def group_vars_diff(var_list):
    """
    Group a list of ESMVariable objects for a given variable into base & reference
    pairs for each parent dataset.
    
    Parameters
    ----------
    var_list : list of ESMVariable objects
        List of ESMVariable objects representing the same variable from different
        model configurations/models. 
        
    Return
    ------
    dictionary
        Key : dataset
        Val : dict
            Keys: 'ref' or 'pert'
            Vals: dataset's reference or purturbation ESMVariable objects.
            
        Ex: {GISS-base : {'ref' : ESMVariable obj, 'pert' : ESMVariable obj}}
    """
    def _add_obj_to_dict(group_dict, var_obj):
        if var_obj.exp == 'reference':
            group_dict[var_obj.dataset]['ref'] = var_obj
        else: 
            group_dict[var_obj.dataset]['pert'] = var_obj
        return group_dict
    groups = {}
    for obj in var_list:
        if obj.dataset in groups:
            _add_obj_to_dict(groups, obj)
        else:
            groups[obj.dataset] = {}
            _add_obj_to_dict(groups, obj)
    return groups
    

def get_diff(var_1, var_2):
    """
    Take the difference of the Iris cubes in two ESMVariable instances.
    Computed as var_1 - var_2.
    
    Parameters
    ----------
    var_1 : ESMVariable object.
    var_2 : ESMVariable object.
    
    Returns
    -------
    Iris cube.
    """
    diff_cube = var_1.cube - var_2.cube
    return diff_cube


def get_cube_diff(cube_1, cube_2):
    """
    Take the difference of two Iris data cubes. 
    Computed as cube_1 - cube_2.
    
    Parameters
    ----------
    cube_1 : Iris cube.
    cube_2 : Iris cube.
    
    Return
    ------
    Iris cube containing the difference of cube_1 - cube_2
    """
    diff_cube = cube_1 - cube_2
    return diff_cube


# === I/O Functions ============================================================

def save_cube(cube, out_file):
    """
    Write an Iris cube to file. 
    
    Valid file formats: 
        * CF netCDF (1.5)
        * GRIB2
        * Met Office PP
        * CSV
    
    Parameters
    ----------
    cube : Iris cube
        Iris cube to write to file.
    out_file : str
        Name and path of the output file.
        
    Returns
    -------
    None.
    """
    if out_file.endswith('.nc') or out_file.endswith('.grib2') or out_file.endswith('.pp'):
        iris.save(cube, out_file)
    elif out_file.endswith('.csv'):
        # Iris does not natively support writing to .csv, so conversion to a Pandas
        # Dataframe is needed. Cube must be 2-D or conversion to DF will fail.
        import iris.pandas
        try:
            df = iris.pandas.as_data_frame(cube, copy=True)
        except ValueError as err:
            raise ValueError("Cube to DataFrame requires 2-D cube, got cube with {} dims".format(cube.ndims))
        else:
            df.to_csv(out_file, sep=',', header=True, index=False)


def save_plot_data(var_name, years, var_data, plt_config, plt_type=None):
    """
    Write processed variable data to CSV. 
    
    Parameters
    ----------
    var_name : str
        Variable short name.
    years : numpy array of int
        Array of years corresponding to the variable data.
    var_data : numpy array of float
        Variable data array contained within an Iris cube returned by the ESMValTool preprocessor.
    plt_config : Dictionary
        Dictionary containing plot metadata and configuration information.
    plt_type: str, optional
        Type of plot. If 'diff', model configuration differences (perturbation - reference)
        will be plotted. Otherwise a normal variable timeseries plot will be created.
        Default is 'None'.
        
    Returns
    -------
    str : Path of the CSV file.
    """
    import pandas as pd
    # Combine the years & variable arrays into a Pandas DF to use Pandas csv writing funcs.
    var_dict = {'year': years, 'value': var_date}
    df = pd.DataFrame(var_dict, columns=['year', 'value'])
    f_name = get_default_plot_name(var_name, plt_config, plt_type=plt_type, strp_ext=True)
    # Append model config & file extension to the filename
    f_name = '{}-{}.csv'.format(f_name, plt_config['config_alias'])
    f_out = os.path.join(plt_config['out_dir'], f_name)
    df.to_csv(f_out, sep=',', header=True, index=False)
    return f_out

  
# === Plotting Functions =======================================================
"""
The plotting functions take a dictionary, "plt_config", as an argument. This
dictionary contains metadata and configuration information for the plotting function.

Key-Value Pairs
---------------
* Key: 'ggplot', Val: bool
    Determines whether or not to use the ggplot stylesheet (grey background and 
    white grid lines, among other things).
* Key: 'out_dir', Val: str
    Plot output directory. This is where the plot will be saved. If not given,
    the plot will not be saved.
* Key: 'plt_name', Val: str
    Name of the output plot file. Include file extension.
* Key: 'time_interval', Val: str
    Time interval of the timeseries (i.e., 'monthly', 'annual', 'decadal').
* Key: 'title', Val: str
    Plot title.
* Key: 'write_data', Val : bool
    Determines whether to write the data being plotted to CSV file.
"""

class PlotStyle:
    """
    Simple class to hold pyplot line styles and colors.
    """
    styles = ['dotted', 'dashed', 'dashdot'] * 2  # Line styles (6)
    colors = ['b', 'g', 'r', 'c', 'm', 'k']       # Line colors (6)
    
    
def plot_timeseries_diff(vars_to_plot, plt_config):
    """
    Wrapper function for plot_timeseries(). Removes the need for the user to 
    remember to enter the plt_type keywarg.
    
    Parameters
    ----------
    vars_to_plot: list ESMVariable objects
        List of ESMVariable objects to plot.
    plt_config : Dictionary
        Dictionary containing plot metadata and configuration information.
        
    Returns
    -------
    None.
    """
    plot_timeseries(vars_to_plot, plt_config, plt_type='diff')
    

def plot_timeseries(vars_to_plot, plt_config, plt_type=None):
    """
    Plot a simple timeseries for one or more variables.

    Parameters
    ----------
    vars_to_plot: list ESMVariable objects
        List of ESMVariable objects to plot.
    plt_config : Dictionary
        Dictionary containing plot metadata and configuration information.
    plt_type: str, optional
        Type of plot. If 'diff', model configuration differences (perturbation - reference)
        will be plotted. Otherwise a normal variable timeseries plot will be created.
        Default is 'None'. 

    Returns
    -------
    None.
    """
    if plt_config['ggplot']:
        # Use ggplot style (grey background, white grid lines)
        plt.style.use('ggplot')
    # Use the first object in the list to parse common attributes.
    years = calc_year_span(vars_to_plot[0].start_year, vars_to_plot[0].end_year)
    units = vars_to_plot[0].units
    var_short = vars_to_plot[0].short_name
    var_long = getattr(Variables, var_short)['cmor_long_name']
    # Iterate over the variable objects & plot.
    if plt_type == 'diff':
        # Model config difference plot.
        diff_groups = group_vars_diff(vars_to_plot)
        for idx, (dataset, var_dict) in enumerate(diff_groups.items()):
            # Diff = perturbation - reference
            diff_cube = get_diff(var_dict['pert'], var_dict['ref'])
            plt.plot(years, diff_cube.data, linestyle=PlotStyle.styles[idx],
                     color=PlotStyle.colors[idx], label=dataset)
            if plt_config['write_data']:
                # Write var arrays to csv
                plt_config['config_alias'] = dataset
                save_plot_data(var_short, years, diff_cube.data, plt_config, plt_type='diff')
        default_plt_name = get_default_plot_name(var_short, plt_config, plt_type='diff')
    else:
        # Variable timeseries plot.
        for idx, var_obj in enumerate(vars_to_plot):
            plt.plot(years, var_obj.cube.data, linestyle=PlotStyle.styles[idx],
                     color=PlotStyle.colors[idx], label=var_obj.alias)
            if plt_config['write_data']:
                # Write var arrays to csv
                plt_config['config_alias'] = var_obj.alias
                save_plot_data(var_short, years, var_obj.cube.data, plt_config)
        default_plt_name = get_default_plot_name(var_short, plt_config)
    plt.xlabel('Year')
    plt.ylabel('{} ({})'.format(var_short, units))
    plt.title(plt_config['title'].format(var_long))
    plt.tight_layout()
    if 'ggplot' in plt_config and not plt_config['ggplot']:
        # Only call when not using ggplot style, otherwise no grid lines will be visible.
        plt.grid()
    plt.legend()
    # Lazy Hack: adjust figure size
    fig = plt.gcf()
    fig.set_size_inches(12, 8)
    if 'out_dir' in plt_config and plt_config['out_dir'] != None:
        # Only save the plot if 'out_dir' is defined.
        try:
            f_name = plt_config['plt_name'].format(var_short)
            plt.savefig(os.path.join(plt_config['out_dir'], f_name))
        except:
            # If a filename for the plot is not given in the plt_config dict, use the default.
            plt.savefig(os.path.join(plt_config['out_dir'], default_plt_name))
    plt.close()
    
    
def get_default_plot_name(var_name, plt_config, plt_type=None, strp_ext=False):
    """
    Construct a default plot filename.
    
    Parameters
    ----------
    var_name : str
        Name of the variable being plotted.
    plt_config : Dictionary
        Dictionary containing plot metadata and configuration information.
    plt_type: str, optional
        Type of plot. If 'diff', model configuration differences (perturbation - reference)
        will be plotted. Otherwise a normal variable timeseries plot will be created.
        Default is 'None'.
    strp_ext : bool, optional.
        If True, the '.pdf' file extension will be removed from the plot name before
        returning. Default is False.
    """
    if plt_type == 'diff':
        plt_name = 'time_series-diff-{}-{}.pdf'.format(plt_config['time_interval'].capitalize(), var_name)
    else:
        plt_name = 'time_series-{}-{}.pdf'.format(plt_config['time_interval'].capitalize(), var_name)
    return plt_name


# === Logger Functions =========================================================

def nuke_logs(log_dir, target=None):
    """
    Remove any existing logs from the logs/ subdirectory
    
    Parameters
    -----------
    log_dir : str
        Path to the log directory
    target : str, optional
        Target log file to delete. If not given, all log files in the directory 
        are deleted. Default is 'None'. 
    """
    if target:
        if not target.endswith('.log'):
            target = target + '.log'
        files = [target]
    else:
        files = [f for f in os.listdir(log_dir) if f.endswith(".log")]
    for f in files:
        try:
            os.remove(os.path.join(log_dir, f))
        except:
            pass


def init_logger(log_name, log_dir, level='debug'):
    """
    Initialize a new logger.
    
    Parameters
    ----------
    log_name : str
        Name of the log.
    log_dir : str
        Directory to write the log file to.
    level : str
        String representing the logging log level.
    
    Return
    -------
    logger : logging.Logger object
    """
    log_levels = {'debug': logging.DEBUG,
                  'info' : logging.INFO,
                  'warn' : logging.WARNING,
                  'error': logging.ERROR,
                  'critical': logging.CRITICAL
                  }
                  
    nuke_logs(log_dir, target=log_name)
    
    if not os.path.isdir(log_dir):
        os.mkdir(log_dir)
    
    log_path = os.path.join(log_dir, log_name + '.log')
    log_format = logging.Formatter("%(asctime)s %(levelname)6s: %(message)s", "%Y-%m-%d %H:%M:%S")
    handler = logging.FileHandler(log_path)
    handler.setFormatter(log_format)
    
    logger = logging.getLogger(log_name)
    logger.setLevel(log_levels[level])
    logger.addHandler(handler)
    logger.info("Log created!\n")
    return logger
    

def log_meta_dict(meta_dict, logger):
    """
    Write the metadata dictionary returned by the preprocessor to the 
    diagnostic main log file.
    
    Parameters
    ----------
    meta_dict : dictionary of {str: [dict]}.
        Dictionary keyed on dataset name. Value is a list of dataset variable
        metadata.
    logger : logging.Logger object
        Logger object representing the log file to write to.
        
    Returns
    -------
    None.
    """
    for key, val in meta_dict.items():
        logger.debug('Metadict Key: {}'.format(key))
        for sub_val in val:
            logger.debug('    val: {}'.format(sub_val))


def log_esmvariable(esm_var, logger):
    """
    Write information about an ESMVariable object to ESMVariable log file.
    
    Parameters
    ----------
    esm_var : ESMVariable object
    logger : logging.Logger object
        Logger object representing the log file to write to.
        
    Returns
    -------
    None.
    """
    attrs = [a for a in dir(esm_var) if not a.startswith('__') and not callable(getattr(obj, a))]
    attrs.remove('cube')  # We only want to log the cube's shape, not all it's attributes
    logger.debug('New ESMVariable instance created.')
    for attr in attrs:
        obj_log.debug('    {} : {}'.format(attr, getattr(self, attr)))
    obj_log.debug('    Cube shape : {}'.format(cube.data.shape))
    

# === Util Functions ===========================================================  

def calc_year_span(year_start, year_end):
    """
    Calculate a span of years (inclusive) given a start and end year.
    
    Parameters
    ----------
    year_start: int
        First year.
    year_end: int
        Last year.
    
    Returns
    -------
    List of int
        List of years between and including the start and end years.
    """
    try:
        years = [yr for yr in range(year_start, year_end + 1)]
    except:
        years = [yr for yr in range(int(year_start), int(year_end) + 1)]
    return np.asarray(years)