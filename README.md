# Distraction-Paper

This is forked from Kate Peters' code to analyse distraction data from PhD experiments conducted c. 2017 at Uni. of Leicester. Jaime made the fork in Feb 2020 to add to analysis and prepare results and figures for publication.

## Order of analysis

Main input files are TDT fiber photometry tanks. The analysis pipeline is designed to enable relevant data to be extracted from tanks and saved in a way that individual analyses can be conducted rapidly without necessarily having access to all of the tanks and metadata (which are large). The process is as follows:

### 1. Assemble data
The script assemble_data.py is executed, which reads in data from an Excel metafile (distraction_photo_metafile.xlsx) and uses functions in fx4assembly.py to construct dictionaries for each day of analysis (3 used - Mod(elled), Dis(traction) and Hab(ituation). Each dictionary is constructed with sub-dictionaries for each rat. Each sub-dictionary includes data from the metafile and tdtfile including the full photometry signals.

This script saves resulting dictionaries in a .pickle file, which is approximately 2GB.

This script will need to be re-run if you do not have access to this 2GB file or if you want to make changes to the metadata that are captured or the processing of the signals.

### 2. Make snips
Next, the script makesnips.py is executed, in which 'snips' are made (short strectches of binned photometry data aligned to the event of interest - the distractors). This script saves .pickle files both with all data (~2GB) and with the streamed photometry data removed (<100MB).

This will need to be re-run if changes to the snip procedure occur (e.g. different trial length).

### 3. ROC analysis
ROC analysis of photometry and behavioural data is performed. First, prepare_roc_data.py is executed, which removes trials from rat dictionaries and flattens into 1-D lists which can be analysed using trial-based ROC analysis. This script saves two .pickle files - one with behavioural data, data4roc_licks.pickle, and one for photometry data, data4roc_photometry.pickle. Next, run_roc_analysis.py is executed (which relies on ROC functions in fx4roc.py). This script performs ROC analyses - which take some time, approx 5 min per comparsison - and thus has the option of commenting out. The results of ROC analyses are saved as .pickle files with appropriate names.

### 4. Plotting of figures using Jupyter Notebooks
Two main notebooks are used - 01_dis-behavior.ipynb and 02_dis-roc-all-figs.ipynb - and should be self-explanatory. Other notebooks for testing data ands for looking at data from individual rats are also included.

### Note on environment file
There is an environment.yml file which can be installed to run all code using standard Anaconda installations.

### Note on folders
Most of the scripts and notebooks will require the destination and source folders for data to be renamed to match your computer, e.g.       datafolder = "C:\\YOURNAME\\Github\\Distraction-Paper\\data\\"
