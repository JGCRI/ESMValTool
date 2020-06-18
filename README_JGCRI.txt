
Important Directories
=====================
* EMIP root - /pic/projects/GCAM/mnichol/emip
* ESMValTool working directory - /pic/projects/GCAM/mnichol/emip/ESMValTool/esmvaltool
* ESMValTool input  - /pic/projects/GCAM/mnichol/emip/input
* ESMValTool output - /pic/projects/GCAM/mnichol/emip/output
* User config files - /pic/projects/GCAM/mnichol/emip/ESMValTool/config-user
* EMIP recipes    - /pic/projects/GCAM/mnichol/emip/ESMValTool/esmvaltool/recipes/emissions_mip
* EMIP diagostics - /pic/projects/GCAM/mnichol/emip/ESMValTool/esmvaltool/diag_scripts/emissions_mip


Running a diagnostic 
====================
1. Activate your Conda environment where ESMValTool is installed as a command line tool.
2. Change working directories to the ESMValTool working directory.
3. Execute via the command: 
    esmvaltool -c <path_to_user_config> <path_to_recipe>
    * Absolute or relative paths may be used for the user config & recipe files. 
4. Output will be written to the ESMValTool output directory.

Example
-------
    cd /pic/projects/GCAM/mnichol/emip/ESMValTool/esmvaltool
    esmvaltool -c ../config-user/config_user-initial_analysis-giss.yml recipes/emissions_mip/recipe-initial_analysis-giss.yml 

Notes
-----
* ESMValTool output will be written to "../../output" regardless of the working directory where ESMValTool was invoked. 