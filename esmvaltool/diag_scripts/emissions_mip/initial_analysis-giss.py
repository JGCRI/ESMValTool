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


class MetaObj:
    """
    Simple class to hold key metadata for a model output file.

    Instance Attributes
    -------------------
    * dataset: str
        Dataset (or model) that produced the data file.
    * ensemble: str
        'Ensemble' (variant label) of the data file. Used as unique identifier.
    * level: str
        Pressure level, if variable is 3-D. 'None' if variable is 2-D.
    * long_name: str
        Variable long name.
    * short_name: str
        Variable short name.
    * start_year: int
        First year of data.
    * end_year: int
        Last year of data.
    * units: str
        Variable units.
    """

    def __init__(self, meta_dict):
        """
        Class instance constructor.

        Parameters
        ----------
        meta_dict: ESMValTool data dictionary.

        Returns
        -------
        MetaObj instance.
        """
        self.dataset    = meta_dict['dataset']
        self.end_year   = meta_dict['end_year']
        self.ensemble   = meta_dict['ensemble']
        self.level      = None
        self.long_name  = meta_dict['long_name']
        self.short_name = meta_dict['short_name']
        self.start_year = meta_dict['start_year']
        self.units      = meta_dict['units']
        self.emip_experiment = None
        self.emip_model      = None
        self._parse_emip_meta()

    def _parse_emip_meta(self):
        """
        Parse the EMIP model name and experiment from an output file's 
        ensemble string.

        Parameters
        ----------
        self

        Returns
        -------
        None
        """
        configs = {'r1i1p5f101': {'emip_model': 'GISS-E2-1-G', 'emip_exp': 'season-so2'},
                   'r1i1p5f102': {'emip_model': 'GISS-E2-1-G', 'emip_exp': 'reference'},
                   'r1i1p5f103': {'emip_model': 'GISS-E2-1-G-nudge', 'emip_exp': 'reference'},
                   'r1i1p5f104': {'emip_model': 'GISS-E2-1-G-nudge', 'emip_exp': 'season-so2'}
                  }
        self.emip_experiment = configs[self.ensemble]['emip_exp']
        self.emip_model      = configs[self.ensemble]['emip_model']


def _plot_time_series(vars_to_plot):
    """
    Example of personal diagnostic plotting function.

    Plots a monthly time series of an area-averaged variable 
    between the ground and first levels. 

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

    Returns
    -------
    None.
    """
    plt.style.use('ggplot')   # Use ggplot style (grey background)
    # Plot output directory can be created dynamically,
    # but is hard-coded for now.
    local_path = '/home/nich980/emip/output/diagnostics'
    styles = ['dotted', 'dashed', 'dashdot'] * 2  # Line styles
    colors = ['b', 'g', 'r', 'c', 'm', 'k']       # Line colors
    for idx, var in enumerate(vars_to_plot):
        curr_cube = var[1]
        cube_meta = var[2]
        curr_label = '{}_{}'.format(cube_meta.emip_model, cube_meta.emip_experiment)
        plt.plot(curr_cube.data, linestyle=styles[idx], color=colors[idx], label=curr_label)
    units = vars_to_plot[0][2].units
    var_short = vars_to_plot[0][2].short_name
    plt.xlabel('Years Since 2000')
    plt.ylabel('Area average ({})'.format(units))
    plt.title('Annual Area Average at Surface - {}'.format(var_short))
    plt.tight_layout()
    #plt.grid()  # MUST comment-out when using ggplot style sheet
    plt.legend()
    #png_name = 'Time_series-my_little_diagnostic.png'
    plt_name = 'time_series-initial_analysis-giss-all_in_one.pdf'
    plt.savefig(os.path.join(local_path, plt_name))
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
    with open("/home/nich980/emip/output/logs/intial_analysis-giss.log", "w") as my_log:
        for key, value in file_dict.items():
            # load the cube from data files only
            # using a single variable here so just grab the first (and only)
            # list element
            my_log.write('KEY: {}\n'.format(key))
            for ensemble in value:
                my_log.write('SUB-VAL: {}'.format(ensemble))
                cube = iris.load_cube(ensemble['filename'])
                cube_meta = MetaObj(ensemble)
                my_log.write('Cube shape: {}\n'.format(cube.data.shape))
                my_log.write('Cube coords: {}\n'.format(cube.coords))
                my_log.write('{}\n'.format('-' * 30))
                # compute an area average over the cube using the preprocessor
                # The cube contains only 100000 Pa level data (see recipe).
                area_avg_cube = area_statistics(cube, 'mean') 
                # Append the cfg, area_avg_cube, and MetaObj tuple to variable list
                var_list.append((cfg, area_avg_cube, cube_meta))
            #print('{}\n'.format('*' * 30))
    _plot_time_series(var_list)
 


if __name__ == '__main__':
    # always use run_diagnostic() to get the config (the preprocessor
    # nested dictionary holding all the needed information)
    with run_diagnostic() as config:
        main(config)
