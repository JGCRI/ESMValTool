"""
Python 3.6
meta_obj.py

Class to hold key model output file metadata.

Matt Nicholson
19 May 2020
"""

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
        self.level      = None
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
        configs = {'r1i1p5f101': {'emip_model': 'GISS-base', 'emip_exp': 'season-so2'},
                   'r1i1p5f102': {'emip_model': 'GISS-base', 'emip_exp': 'reference'},
                   'r1i1p5f103': {'emip_model': 'GISS-nudge', 'emip_exp': 'reference'},
                   'r1i1p5f104': {'emip_model': 'GISS-nudge', 'emip_exp': 'season-so2'}
                  }
        self.emip_experiment = configs[self.ensemble]['emip_exp']
        self.emip_model      = configs[self.ensemble]['emip_model']

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