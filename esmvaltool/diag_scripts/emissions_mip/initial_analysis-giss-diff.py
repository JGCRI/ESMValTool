"""
initial_analysis-giss-diff.py

Creates a plot of the annual & area average difference of a variable from various
GISS CESM configurations. One plot is created per variable.

Matt Nicholson
22 May 2020
"""
import os
import iris
import matplotlib.pyplot as plt

from esmvaltool.diag_scripts.shared import group_metadata, run_diagnostic
from esmvalcore.preprocessor import area_statistics

import common_emip_funcs
from esm_variable import ESMVariable
    

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
    * Dictionary returned by preprocessor is keyed by dataset name, value is
      list of metadata dictionaries for variables belonging to that dataset.
      Ex: dict = {'MPI-ESM-LR': [var1, var2...]}, where var1, var2 are dicts
      holding all variable metadata.
    * Since the preprocessor extracts the 1000 hPa level data,
      the cube's data will have shape (36, 180, 360) corresponding
      to time (in months), latitude, longitude. 
    """
    # Plot configuration dictionary.
    plt_config = {'ggplot'  : True,
                  'out_dir' : cfg['plot_dir'],
                  'plt_name': 'timeseries-diff-{}.pdf',
                  'time_interval': 'annual',
                  'title'   : 'global average diff - {}',
                  'write_data': True
                  }
    file_dict = group_metadata(cfg['input_data'].values(), 'dataset')
    # Get a dictionary keyed on variable name where the value is a list of 
    # variable metadata dict from the various model configs.    
    var_groups = common_emip_funcs.group_meta_by_var(file_dict)
    
    # Iterate over the variable dictionary and process each varible one-by-one.
    for esm_var, dict_list in var_groups.items():
        # Get list of ESMVariable objects.
        var_list = [ESMVariable(var_dict).get_area_statistic('mean') for var_dict in dict_list]
        common_emip_funcs.plot_timeseries_diff(var_list, plt_config)
            
 
if __name__ == '__main__':
    # always use run_diagnostic() to get the config (the preprocessor
    # nested dictionary holding all the needed information)
    with run_diagnostic() as config:
        main(config)
