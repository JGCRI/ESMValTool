"""
Class to represent a variable returned by the ESMValTool preprocessor.

Matt Nicholson
22 May 2020
"""
import iris
import logging

from esmvalcore.preprocessor import area_statistics

class ESMVariable:
    
    def __init__(self, var_dict):
        """
        ESMVariable instance constructor.
        
        Parameters
        ----------
        var_dict : dictionary
            Dictionary containing variable metadata returned by the ESMValTool
            preprocessor.
            
        Returns
        -------
        ESMVariable object.
        """
        self.activity       = var_dict['activity']
        self.alias          = var_dict['alias']
        self.dataset        = var_dict['dataset']
        self.diagnostic     = var_dict['diagnostic']
        self.end_year       = var_dict['end_year']
        self.ensemble       = var_dict['ensemble']
        self.exp            = var_dict['exp']
        self.filename       = var_dict['filename']
        self.frequency      = var_dict['frequency']
        self.grid           = var_dict['grid']
        self.institute      = var_dict['institute']
        self.long_name      = var_dict['long_name']
        self.mip            = var_dict['mip']
        self.modeling_realm = var_dict['modeling_realm']
        self.preprocessor   = var_dict['preprocessor']
        self.project        = var_dict['project']
        self.recipe_dataset_index = var_dict['recipe_dataset_index']
        self.short_name     = var_dict['short_name']
        self.standard_name  = var_dict['standard_name']
        self.start_year     = var_dict['start_year']
        self.units          = var_dict['units']
        self.variable_group = var_dict['variable_group']
        self.level          = self._parse_var_level()
        self.cube           = self._parse_cube()
        self._log_obj()
    
    def update_cube(self, new_cube):
        """
        Update the value of an ESMVariable instance's cube attribute.
        
        Parameters
        ----------
        var_cube : Iris cube
            Iris cube containing the data of the variable represented in the 
            ESMVariable instance.
            
        Returns
        -------
        None.
        """
        self.cube = new_cube
    
    def get_area_statistic(self, stat):
        """
        Get the area statistic of an ESMVariable instance's Iris cube.
        
        Parameters
        ----------
        stat : str
            Area statistic. Passed to ESMValCore area statistics function.
            
        Returns
        -------
        ESMVariable instance
            ESMVariable with area statistic cube.
        """
        area_stat_cube = area_statistics(self.cube, stat)
        self.update_cube(area_stat_cube)
        return self
    
    def _parse_cube(self):
        """
        Read a model output variable into an Iris cube and add it to it's respective
        ESMVariable instance.
        
        Parameters
        ----------
        None.
        
        Returns
        -------
        None.
        """
        cube = iris.load_cube(self.filename)
        return cube
    
    def _parse_var_level(self):
        """
        Parse the level extracted from the variable by the preprocessor, 
        if applicable.
        
        Parameters
        ----------
        self

        Returns
        -------
        None
        """
        vars_3d = ['mmrbc', 'mmrdust', 'mmrso4', 'mmrss', 'so2']
        if self.short_name in vars_3d:
            self.level = '100 hPa'
    
    def _log_obj(self):
        """
        Write information about an ESMVariable object instance to the ESMVariable
        log file. Logger object MUST already be initialized.
        
        Parameters
        ----------
        None - HOWEVER a logger object named 'ESMVariable' must be already initialized.
        """
        obj_log = logging.getLogger('ESMVariable')
        attrs = [a for a in dir(self) if not a.startswith('__') and not callable(getattr(self, a))]
        attrs.remove('cube')  # We only want to log the cube's shape, not all it's attributes
        obj_log.debug('New ESMVariable instance created.')
        for attr in attrs:
            obj_log.debug('    {} : {}'.format(attr, getattr(self, attr)))
        obj_log.debug('    Cube shape : {}'.format(self.cube.data.shape))
    
    def __repr__(self):
        return "<ESMVariable object - {} {} {} {}".format(self.dataset, self.ensemble,
                                                          self.exp, self.short_name)
        