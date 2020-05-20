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
import matplotlib.pyplot as plt

from esmvaltool.diag_scripts.shared import group_metadata, run_diagnostic
from esmvalcore.preprocessor import area_statistics


# === Variable Processing Functions ============================================  

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
    Plot output directory. This is where the plot will be saved.
* Key: 'plt_name', Val: str
    Name of the output plot file. Include file extension.
* Key: 'time_interval', Val: str
    Time interval of the timeseries (i.e., 'monthly', 'annual', 'decadal').
* Key: 'save', Val: bool
    Whether or not to save the plot. (Not yet implemented)
* Key: 'title', Val: str
    Plot title. (Not yet implemented)
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
    plt.title('Annual Area Average - {}'.format(var_short))
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