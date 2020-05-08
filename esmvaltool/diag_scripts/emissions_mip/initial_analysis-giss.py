"""
initial_analysis-giss.py

Emissions-MIP GISS inititial analysis diagnostic script. Creates a plot of the annual & area average
of a variable from various GISS CESM configurations. One plot is created per variable.

Matt Nicholson
23 April 2020
"""
import os
import iris
import matplotlib.pyplot as plt

from esmvaltool.diag_scripts.shared import group_metadata, run_diagnostic
from esmvalcore.preprocessor import area_statistics


def _plot_time_series(vars_to_plot):
    """
    Example of personal diagnostic plotting function.

    Plots a monthly time series of an area-averaged variable 
    between the ground and first levels. 

    Parameters
    ----------
    vars_to_plot: list of tuples
        List containing tuples representing a variable to be plotted.
        Tuple format: (cfg, cube, dataset), where:
            * cfg : nested dictionary
                Nested dictionary of variable metadata.
            * cube : Iris cube
                Variable data to plot.
            * dataset : str
                Name of the dataset to plot.

    Returns
    -------
    None.
    """
    # Plot output directory can be created dynamically,
    # but is hard-coded for now.
    local_path = '/home/nich980/emip/output/diagnostics'
    for var in vars_to_plot:
        # cube = var[1], dataset str = var[2]
        plt.plot(var[1].data, label=var[2])
    plt.xlabel('Time (months)')
    plt.ylabel('Area average')
    plt.title('Time series at ground level')
    plt.tight_layout()
    plt.grid()
    plt.legend()
    #png_name = 'Time_series-my_little_diagnostic.png'
    png_name = 'time_series-initial_analysis-giss-all_in_one.png'
    plt.savefig(os.path.join(local_path, png_name))
    plt.close()

    
def main(cfg):
    """
    Main function. Handles data wrangling and such.

    Parameters
    ----------
    cfg - Dictionary
        Nested dictionary containing dataset names and variables.

    Returns
    -------
    None.

    Notes
    -----
    * Since the preprocessor extracts the 1000 hPa level data,
      the cube's data will have shape (36, 180, 360) corresponding
      to time (in months), latitude, longitude. 
    """
    # assemble the data dictionary keyed by dataset name
    # this makes use of the handy group_metadata function that
    # orders the data by 'dataset'; the resulting dictionary is
    # keyed on datasets e.g. dict = {'MPI-ESM-LR': [var1, var2...]}
    # where var1, var2 are dicts holding all needed information per variable
    file_dict = group_metadata(cfg['input_data'].values(), 'dataset')
    
    var_list = []
    # iterate over key(dataset) and values(list of vars)
    for key, value in file_dict.items():
        # load the cube from data files only
        # using a single variable here so just grab the first (and only)
        # list element
        cube = iris.load_cube(value[0]['filename'])
        print('KEY: {}'.format(key))
        print('Cube shape: {}'.format(cube.data.shape))
        print('Cube coords: {}'.format(cube.coords))
        # compute an area average over the cube using the preprocessor
        # The cube contains only 100000 Pa level data (see recipe).
        area_avg_cube = area_statistics(cube, 'mean') 
        # Append the cfg, area_avg_cube, and key tuple to variable list
        var_list.append((cfg, area_avg_cube, key))
    _plot_time_series(var_list)
 


if __name__ == '__main__':
    # always use run_diagnostic() to get the config (the preprocessor
    # nested dictionary holding all the needed information)
    with run_diagnostic() as config:
        main(config)
