"""Derivation of variable `cVeg_grid`."""

import logging

import iris
from iris import Constraint

from ._derived_variable_base import DerivedVariableBase

logger = logging.getLogger(__name__)


class DerivedVariable(DerivedVariableBase):
    """Derivation of variable `cVeg_grid`."""

    # Required variables
    _required_variables = {
        'vars': [{
            'short_name': 'cVeg',
            'field': 'T2{frequency}s'
        }],
        'fx_files': ['sftlf']
    }

    def calculate(self, cubes):
        """Compute carbon mass in vegetation relative to grid cell area.

        Note
        ----
        By default, `cVeg` is defined relative to land area. For easy spatial
        integration, the original quantity is multiplied by the land area
        fraction (`sftlf`), so that the resuting derived variable is defined
        relative to the grid cell area. This correction is only relevant for
        coastal regions.

        """
        cveg_cube = cubes.extract_strict(
            Constraint(name='vegetation_carbon_content'))
        try:
            sftlf_cube = cubes.extract_strict(
                Constraint(name='land_area_fraction'))
            cveg_cube.data *= sftlf_cube.data / 100.0
        except iris.exceptions.ConstraintMismatchError:
            pass
        return cveg_cube
