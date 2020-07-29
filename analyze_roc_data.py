# -*- coding: utf-8 -*-
"""
Created on Thu Feb 27 11:45:46 2020

@author: admin
"""

from fx4roc import *
import time
import dill

def run_roc_comparison(data, n4shuf=10, timer=True, savedata=""):
    """ Function to run ROC analysis with option for timing and saving resulting data
    Args
    data: list or array with two distributions to be compared. Normally should 
          be of the shape (2,x,y) where x is number of trials and can be different
          between each array and y is bins and should be identical.
          Example, data[0] can be 300x20 list of lists or array and data[1] can
          be 360x20.
    n4shuf: number of times to repeat roc with shuffled values to calculate ps
            default=10, so that it is fast to run, but for accurate p-vals should
            run 2000 times
    timer: Boolean, prints time taken if True
    savedata: insert complete filename here to save the results
    
    Returns
    a: list of ROC values (between 0 and 1) corresponding to bins provided
       (e.g. y in description above)
    p: list of p-vals that correspond to each ROC value in a
    
    """
    
    if timer: start_time = time.time()

    a, p = nanroc(data[0], data[1], n4shuf=n4shuf)
    
    if timer: print(f"--- Total ROC analysis took {(time.time() - start_time)} seconds ---")
    
    if len(savedata)>0:
        try:       
            pickle_out = open(savedata, 'wb')
            dill.dump([a, p, data], pickle_out)
            pickle_out.close()
        except:
            print("Cannot save. Check filename.")

    return a, p


# Loads in data
datafolder = "C:\\Github\\Distraction-Paper\\data\\"
figfolder = "C:\\Github\\Distraction-Paper\\figs\\"
outputfolder = "C:\\Github\\Distraction-Paper\\output\\"

# Loads data for ROC analysis on licking
pickle_in = open(outputfolder+"data4roc_licks.pickle", 'rb')
[mod_dis_hist, mod_notdis_hist, dis_dis_hist, dis_notdis_hist, hab_dis_hist, hab_notdis_hist] = dill.load(pickle_in)

# list of comparisons

# Uncomment to run lick comparisons

# ### Comparison of lick data between distracted and non-distracted trials on distraction day 
# a, p = run_roc_comparison([dis_notdis_hist, dis_dis_hist], n4shuf=2000,
#                           savedata=outputfolder+"roc_licks_disday_disVnondis.pickle")

# # Comparison of lick data between modelled and distraction day for distracted trials 
# a, p = run_roc_comparison([mod_dis_hist, dis_dis_hist], n4shuf=2000,
#                           savedata=outputfolder+"roc_licks_distrials_modVdis.pickle")

# # Comparison of lick data between modelled and distraction day for NOT distracted trials 
# a, p = run_roc_comparison([mod_notdis_hist, dis_notdis_hist], n4shuf=2000,
#                           savedata=outputfolder+"roc_licks_notdistrials_modVdis.pickle")

# Comparison of lick data between distraction and habituation day for ALL trials 

dis_all_hist = dis_notdis_hist + dis_dis_hist
hab_all_hist = hab_notdis_hist + hab_dis_hist
# a, p = run_roc_comparison([dis_all_hist, hab_all_hist], n4shuf=2000,
#                           savedata=outputfolder+"roc_licks_alltrials_disVhab.pickle")


# Loads data for ROC analysis on photometry snips
pickle_in = open(outputfolder+"data4roc_photo.pickle", 'rb')
[mod_dis_photo_snips_flat, mod_notdis_photo_snips_flat, dis_dis_photo_snips_flat, dis_notdis_photo_snips_flat, hab_dis_photo_snips_flat, hab_notdis_photo_snips_flat] = dill.load(pickle_in)

# makes lists of all snips for each day (distracted and not distracted trials)
mod_all_photo_snips_flat = mod_dis_photo_snips_flat + mod_notdis_photo_snips_flat
dis_all_photo_snips_flat = dis_dis_photo_snips_flat + dis_notdis_photo_snips_flat
hab_all_photo_snips_flat = hab_dis_photo_snips_flat + hab_notdis_photo_snips_flat

# ### Comparison of photometry data between modelled, distraction, and hab day for ALL trials 
# a, p = run_roc_comparison([mod_all_photo_snips_flat, dis_all_photo_snips_flat], n4shuf=2000,
#                           savedata=outputfolder+"roc_photo_alltrials_modVdis.pickle")

# a, p = run_roc_comparison([mod_all_photo_snips_flat, hab_all_photo_snips_flat], n4shuf=2000,
#                           savedata=outputfolder+"roc_photo_alltrials_modVhab.pickle")

# a, p = run_roc_comparison([dis_all_photo_snips_flat, hab_all_photo_snips_flat], n4shuf=2000,
#                           savedata=outputfolder+"roc_photo_alltrials_disVhab.pickle")

# ### Comparison of photometry data between distracted and non-distracted trials for each day in turn 
# a, p = run_roc_comparison([mod_notdis_photo_snips_flat, mod_dis_photo_snips_flat], n4shuf=2000,
#                           savedata=outputfolder+"roc_photo_modday_disVnotdis.pickle")

# a, p = run_roc_comparison([dis_notdis_photo_snips_flat, dis_dis_photo_snips_flat], n4shuf=2000,
#                           savedata=outputfolder+"roc_photo_disday_disVnotdis.pickle")

# a, p = run_roc_comparison([hab_notdis_photo_snips_flat, hab_dis_photo_snips_flat], n4shuf=2000,
#                           savedata=outputfolder+"roc_photo_habday_disVnotdis.pickle")

# a, p = run_roc_comparison([dis_dis_photo_snips_flat, hab_dis_photo_snips_flat], n4shuf=2000,
#                           savedata=outputfolder+"roc_photo_distrials_disVhab.pickle")

# a, p = run_roc_comparison([dis_notdis_photo_snips_flat, hab_notdis_photo_snips_flat], n4shuf=2000,
#                           savedata=outputfolder+"roc_photo_notdistrials_disVhab.pickle")

