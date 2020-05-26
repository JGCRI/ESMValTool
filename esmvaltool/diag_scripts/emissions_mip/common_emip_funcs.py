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
from itertools import groupby, chain

from esmvaltool.diag_scripts.shared import group_metadata, run_diagnostic
from esmvalcore.preprocessor import area_statistics


# === Variable Processing Functions ============================================

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
"""

class PlotStyle:
    """
    Simple class to hold pyplot line styles and colors.
    """
    styles = ['dotted', 'dashed', 'dashdot'] * 2  # Line styles (6)
    colors = ['b', 'g', 'r', 'c', 'm', 'k']       # Line colors (6)
    

def plot_timeseries(vars_to_plot, plt_config):
    """
    Plot a simple timeseries for one or more variables.

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
    if plt_config['ggplot']:
        # Use ggplot style (grey background, white grid lines)
        plt.style.use('ggplot')
    # Use the first object in the list to parse common attributes.
    years = calc_year_span(vars_to_plot[0].start_year, vars_to_plot[0].end_year)
    units = vars_to_plot[0].units
    var_short = vars_to_plot[0].short_name
    # Iterate over the variable objects & plot.
    for idx, var_obj in enumerate(vars_to_plot):
        plt.plot(years, var_obj.cube.data, linestyle=PlotStyle.styles[idx],
                 color=PlotStyle.colors[idx], label=var_obj.alias)
    plt.xlabel('Year')
    plt.ylabel('Area average ({})'.format(units))
    plt.title(plt_config['title'].format(var_short))
    plt.tight_layout()
    if 'ggplot' in plt_config and not plt_config['ggplot']:
        # Only call when not using ggplot style, otherwise no grid lines will be visible.
        plt.grid()
    plt.legend()
    if 'out_dir' in plt_config and plt_config['out_dir'] != None:
        # Only save the plot if 'out_dir' is defined.
        try:
            f_name = plt_config['plt_name'].format(var_short)
            plt.savefig(os.path.join(plt_config['out_dir'], f_name))
        except:
            # If a filename for the plot is not given in the plt_config dict, use the default.
            plt_name = 'time_series-{}-{}.pdf'.format(plt_config['time_interval'].capitalize(), var_short)
            plt.savefig(os.path.join(plt_config['out_dir'], plt_name))
    plt.close()
    
    
def plot_timeseries_diff(vars_to_plot, plt_config):
    """
    Plot a timeseries of the differences between model configurations for one
    or more variables.
    
    Parameters
    ----------
    vars_to_plot: list of tuples
        List containing tuples representing a variable to be plotted.
        Tuple format: (cfg, cube, cube_meta), where:
            * cfg : nested dictionary
                Nested dictionary of variable metadata.
            * cube : Iris cube
                Variable data to plot.
            * cube_meta: MetaObj object
                MetaObj instance containing key Iris cube metadata.
    plt_config : Dictionary
        Dictionary containing plot metadata and configuration information.

    Returns
    -------
    None.
    """
    if plt_config['ggplot']:
        # Use ggplot style (grey background, white grid lines)
        plt.style.use('ggplot')
    years = calc_year_span(vars_to_plot[0][2].start_year, vars_to_plot[0][2].end_year)
    for idx, var in enumerate(vars_to_plot):
        curr_cube = var[1]
        cube_meta = var[2]
        curr_label = '{}_{}'.format(cube_meta.emip_model, cube_meta.emip_experiment)
        plt.plot(years, curr_cube.data, linestyle=PlotStyle.styles[idx],
                 color=PlotStyle.colors[idx], label=curr_label)
    units = vars_to_plot[0][2].units
    var_short = vars_to_plot[0][2].short_name
    plt.xlabel('Year')
    plt.ylabel('Area average ({})'.format(units))
    plt.title('Annual Area Average Difference - {}'.format(var_short))
    plt.tight_layout()
    if not plt_config['ggplot']:
        # Only call when not using ggplot style, otherwise no grid lines will be visible.
        plt.grid()
    plt.legend()
    try:
        plt.savefig(os.path.join(plt_config['out_dir'], plt_config['plt_name']))
    except:
        plt_name = 'time_series-initial_analysis-giss-all_in_one.pdf'
        plt.savefig(os.path.join(plt_config['out_dir'], plt_name))
    plt.close()
    

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
    

# === Helper Functions =========================================================  

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
    return years