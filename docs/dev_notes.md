Dev Notes for the Emissions-MIP project and [ESMValTool](https://github.com/ESMValGroup/ESMValTool) software package.

Last updated 20 May 2020.

Matt Nicholson

# Emissions-MIP

## Phase 1 Model Configurations

|   Run   |   Archive  |  Base/Perturb. | Wind Nudging | Seasonality | Modified Model Name | Experiment Name |
| :------ |:---------- | :------------- |:------------ | :---------- | :-------------------| :-------------- |
| BNW1999 | r1i1p5f101 | base           | no           | yes         | GISS-base           | season-so2      |
| PWN1999 | r1i1p5f102 | perturbation   | no           | no          | GISS-base           | reference       |
| PW1999  | r1i1p5f103 | perturbation   | yes          | no          | GISS-nudge          | reference       |
| BW1999  | r1i1p5f104 | base           | yes          | yes         | GISS-nudge          | season-so2      |

## Win10 Linux Sub-Sys Paths
### Input
| Directory      | Path                                                                                              |
| :------------- |:------------------------------------------------------------------------------------------------- |
| root           | `/home/nich980/emip/input`                                                                        |
| GISS-Orig-root | `/home/nich980/emip/input/GISS-ORIGINAL`                                                          |
| GISS-Orig-nc   | `ROOT/AerChemMIP/NASA-GISS/GISS-E2-1-G/piClim-SO2/<archive>/AERmon/<var>/gn/v20191120/<var_nc>`   |
| GISS-EMIP-root | `/home/nich980/emip/input/GISS-EMIP`                                                              |
| GISS-EMIP-nc   | `ROOT/AerChemMIP/NASA-GISS/GISS-E2-1-G/<experiment>/<archive>/AERmon/<var>/gn/v20191120/<var_nc>` |
| Sample Input   | `/home/nich980/emip/input/input4mips`                                                             |

### Output
| Directory         | Path                                                                         |
| :---------------- |:---------------------------------------------------------------------------- |
| root              | `/home/nich980/emip/output`                                                  |
| Recipes           | `/home/nich980/esmvaltool/jgcri-fork/ESMValTool/recipes/emissions_mip`       |
| Diagnostics       | `/home/nich980/esmvaltool/jgcri-fork/ESMValTool/diag_scripts/emissions_mip`  |
| Output - Plots    | `/home/nich980/emip/output/diagnostics`                                      |
| Output - EVT Logs | `/home/nich980/emip/output<recipe_name>/run/<diagnostic_name>/<script_name>` |


### JGCRI ESMValTool Fork
| Directory   | Path                                                                        |
| :---------- |:--------------------------------------------------------------------------- |
| root        | `/home/nich980/esmvaltool/jgcri-fork/ESMValTool/esmvaltool`                 |
| Usr config  | `/home/nich980/esmvaltool/jgcri-fork/ESMValTool/config-user`                |
| Recipes     | `/home/nich980/esmvaltool/jgcri-fork/ESMValTool/recipes/emissions_mip`      |
| Diagnostics | `/home/nich980/esmvaltool/jgcri-fork/ESMValTool/diag_scripts/emissions_mip` |

### Windows Partition
| Directory | Path                             |
| :-------- |:-------------------------------- |
| root      | `/mnt/c/users/nich980/`          |
| EMIP repo | `/mnt/c/users/nich980/code/emip` |
| Output    | `/mnt/c/users/nich980/data/emip` |

---

# ESMValTool
## CMOR Data Reference Syntax & Data Finder
The [Data Finder](https://esmvaltool.readthedocs.io/projects/ESMValCore/en/latest/quickstart/find_data.html) is how ESMValTool finds datasets specified in recipes.

### Standard CMIP Filename Formats
* CMIP6: `[var_short_name]_[mip]_[dataset_name]_[experiment]_[ensemble]_[grid]_[start-date]-[end_date].nc`
* CMIP5: `[var_short_name]_[mip]_[dateset_name]_[experiment]_[ensemble]_[start_date]-[end_date].nc`
* Obs: `[project]_[dataset_name]_[type]_[version]_[mip]_[short_name]_[start_date]-[end_date].nc`

### Standard CMIP ESGF Input Directory Paths
* CMIP6-BADC:
  ```
  INPUT_ROOT/[activity]/[institute]/[dataset_name]/[experiment]/[ensemble]/[mip]/[var_short_name]/[grid]/[current_version]
  ```
* CMIP6-ETHZ:
  ```
  INPUT_ROOT/[experiment]/[mip]/[var_short_name]/[dataset_name]/[ensemble]/[grid]/[current_version]
  ```

* **Notes**
  * The [JGCRI ESMValTool fork](https://github.com/JGCRI/ESMValTool) is currently configured to use the CMIP6-BADC directory structure.
  * ESMValTool's Data Finder will automatically select the most-current variable version.
      
### GISS Output Breakdown
The table below illustrates ESMValTool dataset components and their corresponding unmodified GISS CMIP/CMOR values.

| Component       | GISS Value     |
| :-------------- | :------------- |
| activity        | `AerChemMIP`   |
| institute       | `NASA-GISS`    |
| dataset         | `GISS-E2-1-G1` |
| experiment      | `piClim-SO2`   |
| ensemble        | `r1i1p5f101`   |
| grid            | `gn`           |
| current_version | `v20191120`    |
| start_date      | `200001`       |
| end_date        | `201412`       |


### ESMValTool Documentation Syntax
It has been noted that some words and phrases used in the ESMValTool documentation differ slightly from how we're used to using them.
| Term & Realm                          | ESMValTool Definition/Example | CMOR/CMIP Definition/Example                   |
| :------------------------------------ | :---------------------------- | :--------------------------------------------- |
| `mip` - filename; directory path      | `AERmon`                      | CMOR table entry; `table_id` (netcdf metadata) |
| `ensemble` - filename; directory path | `r1i1p5f101` | Combination of realization, initialization, physics, & forcing indices; `variant_label` (netcdf metadata) |

## Running Diagnostic Scripts
As an example, here is how to run the recipe `recipe-initial_analysis-giss.yml` and its associated diagnostic script, `initial_analysis-giss.py`, using `config_user-initial_analysis-giss.yml` as the user configuration file:

1. `cd` to `~/esmvaltool/jgcri-fork/ESMValTool/esmvaltool`
2. Activate a `conda` environment that has ESMValTool installed (here it could be `emip` or `esm-dev`): `conda activate esm-dev`
3. Execute the diagnostic using the following command:
   ```
   esmvaltool -c /home/nich980/esmvaltool/jgcri-fork/ESMValTool/config-user/config_user-initial_analysis-giss.yml recipes/emissions_mip/recipe-initial_analysis-giss.yml 
   ```
   
## ESMValTool Functionality
### Metadata Dictionaries
* Returned by the preprocessor?
* Keyed on dataset name
* Value is a dictionary containing dataset's metadata

Ex: 
```
Key: CanESM2
Val: [{'alias': 'CanESM2', 'dataset': 'CanESM2', 'diagnostic': 'diagnostic1', 'end_year': 2002, 'ensemble': 'r1i1p1', 'exp': 'historical', 'filename': '/home/nich980/emip/output/recipe_python/recipe_my_personal_diagnostic_20200505_172626/preproc/diagnostic1/ta/CMIP5_CanESM2_Amon_historical_r1i1p1_ta_2000-2002.nc', 'frequency': 'mon', 'institute': ['CCCma'], 'long_name': 'Air Temperature', 'mip': 'Amon', 'modeling_realm': ['atmos'], 'preprocessor': 'preprocessor1', 'project': 'CMIP5', 'recipe_dataset_index': 0, 'short_name': 'ta', 'standard_name': 'air_temperature', 'start_year': 2000, 'units': 'K', 'variable_group': 'ta'}]

Key: MPI-ESM-LR
Val: [{'alias': 'MPI-ESM-LR', 'dataset': 'MPI-ESM-LR', 'diagnostic': 'diagnostic1', 'end_year': 2002, 'ensemble': 'r1i1p1', 'exp': 'historical', 'filename': '/home/nich980/emip/output/recipe_python/recipe_my_personal_diagnostic_20200505_172911/preproc/diagnostic1/ta/CMIP5_MPI-ESM-LR_Amon_historical_r1i1p1_ta_2000-2002.nc', 'frequency': 'mon', 'institute': ['MPI-M'], 'long_name': 'Air Temperature', 'mip': 'Amon', 'modeling_realm': ['atmos'], 'preprocessor': 'preprocessor1', 'project': 'CMIP5', 'recipe_dataset_index': 1, 'short_name': 'ta', 'standard_name': 'air_temperature', 'start_year': 2000, 'units': 'K', 'variable_group': 'ta'}]

Key: MultiModelMean
Val: [{'alias': 'MultiModelMean', 'dataset': 'MultiModelMean', 'diagnostic': 'diagnostic1', 'end_year': 2002, 'ensemble': 'r1i1p1', 'exp': 'historical', 'filename': '/home/nich980/emip/output/recipe_python/recipe_my_personal_diagnostic_20200505_172911/preproc/diagnostic1/ta/MultiModelMean_Amon_ta_2000-2002.nc', 'frequency': 'mon', 'long_name': 'Air Temperature', 'mip': 'Amon', 'modeling_realm': ['atmos'], 'preprocessor': 'preprocessor1', 'project': 'CMIP5', 'short_name': 'ta', 'standard_name': 'air_temperature', 'start_year': 2000, 'units': 'K', 'variable_group': 'ta'}]
```

If multiple variations of the same dataset are defined in a recipe, but have the same dataset name, the dictionary will have only key, but the value will contain multiple dictionaries, one for each dataset variation.

For example, we have these datasets defined in the recipe:
```
datasets:
        - {dataset: GISS-E2-1-G, project: CMIP6, mip: AERmon, exp: piClim-SO2, ensemble: r1i1p5f101, grid: gn}
        - {dataset: GISS-E2-1-G, project: CMIP6, mip: AERmon, exp: piClim-SO2, ensemble: r1i1p5f102, grid: gn}
        - {dataset: GISS-E2-1-G, project: CMIP6, mip: AERmon, exp: piClim-SO2, ensemble: r1i1p5f103, grid: gn}
        - {dataset: GISS-E2-1-G, project: CMIP6, mip: AERmon, exp: piClim-SO2, ensemble: r1i1p5f104, grid: gn}
```
Since each entry has `GISS-E2-1-G` as the dataset attribute, the metadata dictionary returned by the preprocessor will only have one key: `GISS-E2-1-G`.

However, the key's value will be a list of four dictionaries, one for each ensemble defined in the recipe:
```
Key: GISS-E2-1-G
Val: [
{'activity': 'AerChemMIP', 'alias': 'r1i1p5f101', 'dataset': 'GISS-E2-1-G', 'diagnostic': 'diagnostic1', 'end_year': 2014, 'ensemble': 'r1i1p5f101', 'exp': 'piClim-SO2', 'filename': '/home/nich980/emip/output/recipe-intial_analysis-giss/recipe-initial_analysis-giss_20200519_200056/preproc/diagnostic1/emiso2/CMIP6_GISS-E2-1-G_AERmon_piClim-SO2_r1i1p5f101_emiso2_2000-2014.nc', 'frequency': 'mon', 'grid': 'gn', 'institute': ['NASA-GISS'], 'long_name': 'Total Emission Rate of SO2', 'mip': 'AERmon', 'modeling_realm': ['aerosol'], 'preprocessor': 'preproc_nolev', 'project': 'CMIP6', 'recipe_dataset_index': 0, 'short_name': 'emiso2', 'standard_name': 'tendency_of_atmosphere_mass_content_of_sulfur_dioxide_due_to_emission', 'start_year': 2000, 'units': 'kg m-2 s-1', 'variable_group': 'emiso2'}, 
{'activity': 'AerChemMIP', 'alias': 'r1i1p5f102', 'dataset': 'GISS-E2-1-G', 'diagnostic': 'diagnostic1', 'end_year': 2014, 'ensemble': 'r1i1p5f102', 'exp': 'piClim-SO2', 'filename': '/home/nich980/emip/output/recipe-intial_analysis-giss/recipe-initial_analysis-giss_20200519_200056/preproc/diagnostic1/emiso2/CMIP6_GISS-E2-1-G_AERmon_piClim-SO2_r1i1p5f102_emiso2_2000-2014.nc', 'frequency': 'mon', 'grid': 'gn', 'institute': ['NASA-GISS'], 'long_name': 'Total Emission Rate of SO2', 'mip': 'AERmon', 'modeling_realm': ['aerosol'], 'preprocessor': 'preproc_nolev', 'project': 'CMIP6', 'recipe_dataset_index': 1, 'short_name': 'emiso2', 'standard_name': 'tendency_of_atmosphere_mass_content_of_sulfur_dioxide_due_to_emission', 'start_year': 2000, 'units': 'kg m-2 s-1', 'variable_group': 'emiso2'},
{'activity': 'AerChemMIP', 'alias': 'r1i1p5f103', 'dataset': 'GISS-E2-1-G', 'diagnostic': 'diagnostic1', 'end_year': 2014, 'ensemble': 'r1i1p5f103', 'exp': 'piClim-SO2', 'filename': '/home/nich980/emip/output/recipe-intial_analysis-giss/recipe-initial_analysis-giss_20200519_200056/preproc/diagnostic1/emiso2/CMIP6_GISS-E2-1-G_AERmon_piClim-SO2_r1i1p5f103_emiso2_2000-2014.nc', 'frequency': 'mon', 'grid': 'gn', 'institute': ['NASA-GISS'], 'long_name': 'Total Emission Rate of SO2', 'mip': 'AERmon', 'modeling_realm': ['aerosol'], 'preprocessor': 'preproc_nolev', 'project': 'CMIP6', 'recipe_dataset_index': 2, 'short_name': 'emiso2', 'standard_name': 'tendency_of_atmosphere_mass_content_of_sulfur_dioxide_due_to_emission', 'start_year': 2000, 'units': 'kg m-2 s-1', 'variable_group': 'emiso2'},
{'activity': 'AerChemMIP', 'alias': 'r1i1p5f104', 'dataset': 'GISS-E2-1-G', 'diagnostic': 'diagnostic1', 'end_year': 2014, 'ensemble': 'r1i1p5f104', 'exp': 'piClim-SO2', 'filename': '/home/nich980/emip/output/recipe-intial_analysis-giss/recipe-initial_analysis-giss_20200519_200056/preproc/diagnostic1/emiso2/CMIP6_GISS-E2-1-G_AERmon_piClim-SO2_r1i1p5f104_emiso2_2000-2014.nc', 'frequency': 'mon', 'grid': 'gn', 'institute': ['NASA-GISS'], 'long_name': 'Total Emission Rate of SO2', 'mip': 'AERmon', 'modeling_realm': ['aerosol'], 'preprocessor': 'preproc_nolev', 'project': 'CMIP6', 'recipe_dataset_index': 3, 'short_name': 'emiso2', 'standard_name': 'tendency_of_atmosphere_mass_content_of_sulfur_dioxide_due_to_emission', 'start_year': 2000, 'units': 'kg m-2 s-1', 'variable_group': 'emiso2'}
]
```

## Troubleshooting
### Exec Format Error
Due to how Python handles and executes sub-processes, `ESMValTool` can raise an `OSError: [Errno 8] Exec format error` error if your diagnostic script has *too many* permissions. 

For example, `initial_analysis-giss-diff.py` was raising an `OSError: [Errno 8] Exec format` when it had the following permissions:
```
-rwxrwxrwx 1 nich980 nich980  2780 May 26 17:59 initial_analysis-giss-diff.py
```

**Solution** 
Remove the execution permissions with the command `chmod -x initial_analysis-giss-diff.py`. This will yield
```
-rw-rw-rw- 1 nich980 nich980  2780 May 26 17:59 initial_analysis-giss-diff.py
```
and `ESMValTool` will run the diagnostic without error.
