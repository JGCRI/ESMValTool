"""
test_diag.py

A simple test diagnostic script for R&D.

Matt Nicholson
6 May 2020
"""
import os
import iris

from esmvaltool.diag_scripts.shared import group_metadata, run_diagnostic
from esmvalcore.preprocessor import area_statistics, annual_statistics


def print_cube_metadata(filename, cube):
    """
    Print some metadata from a given cube.

    Parameters
    ----------
    filename : str
        Name of the file corresponding to the Iris cube.
    cube : iris.cube.Cube
        Cube to query.
    
    Returns
    -------
    None.
    """
    print('*' * 60)
    print('Cube parent file: {}'.format(filename))
    print('Cube name: {}'.format(cube.name()))
    print('Cube shape: {}'.format(cube.shape))
    print('Cube coordinates:')
    for coord in cube.coords():
        print('    {} - {}'.format(coord.standard_name, coord.shape))


def run_test_diagnostic(cfg):
    """
    Put stuff to be run in here.

    Parameters
    ----------
    cfg : Nested dictionary
        Nested dictionary of metadata.

    Returns
    -------
    Maybe
    """
    # Construct the data dictionary, where:
    #    key: str, dataset name
    #    val: list, each element is a dictionary containing variable
    #         information.
    # Ex: file_dict = {'CanESM2': [var_1_dict, var_2_dict, ...]}
    file_dict = group_metadata(cfg['input_data'].values(), 'dataset')
    
    for key, value in file_dict.items():
        curr_fname = value[0]['filename']
        cube = iris.load_cube(curr_fname)
        print_cube_metadata(curr_fname, cube)

        # Take the annual average of the cube data
        annual_avg_cube = annual_statistics(cube, 'mean')
        print_cube_metadata(curr_fname + 'annual_avg', annual_avg_cube)



if __name__ == '__main__':
    with run_diagnostic() as config:
        run_test_diagnostic(config)
