# -*- coding: utf-8 -*-
"""
Created on Thu Feb 27 10:51:40 2020

@author: admin
"""

import numpy as np
import dill


def make_lick_snips(d, pre=5, post=15):
    """ Makes snips of licks aligned to each distractor
    
    Args
    d: dictionary with lick data (key='licks') and distractor timestamps (key='distractors')
    pre: time before distractor (in s, default=5)
    post: time after each distractor (in s, default=15)
    
    Returns
    snips: list of lick snips aligned to distractor
    
    """
    snips = []
    for dis in d['distractors']:
        snips.append([lick-dis for lick in d['licks'] if (lick-dis>-pre) and (lick-dis<post) ])
        
    return snips

def flatten_list(listoflists):
    """ Flattens list of lists into a single list
    Args:
        listoflists: nested list
    Returns:
        flat_list: flattened list
    """
    try:
        flat_list = [item for sublist in listoflists for item in sublist]
        return flat_list
    except:
        print('Cannot flatten list. Maybe is in the wrong format. Returning empty list.')
        return []


def check_val_between(data, x1=0.001, x2=1.000):
    """ Checks if there is a value in a list between two numbers"""
    
    vals = [1 for d in data if d>x1 and d<x2]
    
    if sum(vals) > 0:
        return True
    else:
        return False

def resample_snips(snips, factor=0.1):
    """ Resamples snips to collapse data into larger bins (e.g. for ROC analysis)
    Args
    snips: array of snips (list of lists)
    factor: constant to decide how to bin data (default=0.1)
    
    Returns
    snips: resamples snips
    
    """
    if len(snips)>0:
        n_bins = len(snips[0])
        out_bins = int(n_bins * factor)

        snips_out = []
        for snip in snips:
            snips_out.append(np.mean(np.reshape(snip, (out_bins, -1)), axis=1))
    
        return snips_out
    else:
        return []
    
# Loads in data
datafolder = "C:\\Github\\Distraction-Paper\\data\\"
figfolder = "C:\\Github\\Distraction-Paper\\figs\\"
outputfolder = "C:\\Github\\Distraction-Paper\\output\\"

try:
    pickle_in = open(datafolder + "distraction_data_only_snips.pickle", 'rb')
except FileNotFoundError:
        print('Cannot access pickled file')

[modDict, disDict, habDict] = dill.load(pickle_in)

# removes rat 2.8 because no data on hab day
modDict.pop('thph2.8')
disDict.pop('thph2.8')

# gets list of rats
rats = disDict.keys()

# goes through dict from each test day nd makes lick snips
mod_lick_snips, dis_lick_snips, hab_lick_snips = [], [], []

for rat in rats:
    d = modDict[rat]
    mod_lick_snips.append(make_lick_snips(d))
    
    d = disDict[rat]
    dis_lick_snips.append(make_lick_snips(d))
    
    d = habDict[rat]
    hab_lick_snips.append(make_lick_snips(d))
    
pickle_out = open(outputfolder+"data4epochs_licks.pickle", 'wb')
dill.dump([mod_lick_snips, dis_lick_snips, hab_lick_snips], pickle_out)
pickle_out.close()

# flattens lists so that trials from all rats are pooled
mod_lick_snips_flat = flatten_list(mod_lick_snips)
dis_lick_snips_flat = flatten_list(dis_lick_snips)
hab_lick_snips_flat = flatten_list(hab_lick_snips)

# divides snips into distracted and non-distracted trials for each day
mod_dis_snips = [snip for snip in mod_lick_snips_flat if not check_val_between(snip)]
mod_notdis_snips = [snip for snip in mod_lick_snips_flat if check_val_between(snip)]

dis_dis_snips = [snip for snip in dis_lick_snips_flat if not check_val_between(snip)]
dis_notdis_snips = [snip for snip in dis_lick_snips_flat if check_val_between(snip)]

hab_dis_snips = [snip for snip in hab_lick_snips_flat if not check_val_between(snip)]
hab_notdis_snips = [snip for snip in hab_lick_snips_flat if check_val_between(snip)]

print("\nFor lick data - should match numbers for photometry data...")
print(f"Number of DISTRACTED trials on MODELLED day is {len(mod_dis_snips)}")
print(f"Number of NOT DISTRACTED trials on MODELLED day is {len(mod_notdis_snips)}")
print(f"Number of DISTRACTED trials on DISTRACTION day is {len(dis_dis_snips)}")
print(f"Number of NOT DISTRACTED trials on DISTRACTION day is {len(dis_notdis_snips)}")
print(f"Number of DISTRACTED trials on HABITUATION day is {len(hab_dis_snips)}")
print(f"Number of NOT DISTRACTED trials on HABITUATION day is {len(hab_notdis_snips)}")

# Puts lick data into histograms
bins = np.arange(-5, 16, 1)
mod_dis_hist = [np.histogram(snip, bins=bins)[0] for snip in mod_dis_snips]
mod_notdis_hist = [np.histogram(snip, bins=bins)[0] for snip in mod_notdis_snips]

dis_dis_hist = [np.histogram(snip, bins=bins)[0] for snip in dis_dis_snips]
dis_notdis_hist = [np.histogram(snip, bins=bins)[0] for snip in dis_notdis_snips]

hab_dis_hist = [np.histogram(snip, bins=bins)[0] for snip in hab_dis_snips]
hab_notdis_hist = [np.histogram(snip, bins=bins)[0] for snip in hab_notdis_snips]

# Saves lick histograms for each day for further ROC analysis

pickle_out = open(outputfolder+"data4roc_licks.pickle", 'wb')
dill.dump([mod_dis_hist, mod_notdis_hist, dis_dis_hist, dis_notdis_hist, hab_dis_hist, hab_notdis_hist], pickle_out)
pickle_out.close()



# resamples snips from each dictionary
mod_dis_photo_snips, mod_notdis_photo_snips, = [], []
dis_dis_photo_snips, dis_notdis_photo_snips, = [], []
hab_dis_photo_snips, hab_notdis_photo_snips, = [], []

rats=disDict.keys()

for rat in rats:
    d = disDict[rat]
    
    snips_dis = resample_snips(d['snips_distracted']['filt_z'])
    dis_dis_photo_snips.append(snips_dis)
    
    snips_notdis = resample_snips(d['snips_not-distracted']['filt_z'])
    dis_notdis_photo_snips.append(snips_notdis)
    
    d = modDict[rat]
    
    snips_dis = resample_snips(d['snips_distracted']['filt_z'])
    mod_dis_photo_snips.append(snips_dis)
    
    snips_notdis = resample_snips(d['snips_not-distracted']['filt_z'])
    mod_notdis_photo_snips.append(snips_notdis)
    
    d = habDict[rat]
    
    snips_dis = resample_snips(d['snips_distracted']['filt_z'])
    hab_dis_photo_snips.append(snips_dis)
    
    snips_notdis = resample_snips(d['snips_not-distracted']['filt_z'])
    hab_notdis_photo_snips.append(snips_notdis)
    
pickle_out = open(outputfolder+"data4epochs_photo.pickle", 'wb')
dill.dump([ mod_dis_photo_snips, mod_notdis_photo_snips, dis_dis_photo_snips, dis_notdis_photo_snips, hab_dis_photo_snips, hab_notdis_photo_snips], pickle_out)
pickle_out.close()

# flattens all lists
mod_dis_photo_snips_flat = flatten_list(mod_dis_photo_snips)
mod_notdis_photo_snips_flat = flatten_list(mod_notdis_photo_snips)

dis_dis_photo_snips_flat = flatten_list(dis_dis_photo_snips)
dis_notdis_photo_snips_flat = flatten_list(dis_notdis_photo_snips)

hab_dis_photo_snips_flat = flatten_list(hab_dis_photo_snips)
hab_notdis_photo_snips_flat = flatten_list(hab_notdis_photo_snips)

print("\nFor photometry data - should match numbers for lick data...")
print(f"Number of DISTRACTED trials on MODELLED day is {len(mod_dis_photo_snips_flat)}")
print(f"Number of NOT DISTRACTED trials on MODELLED day is {len(mod_notdis_photo_snips_flat)}")
print(f"Number of DISTRACTED trials on DISTRACTION day is {len(dis_dis_photo_snips_flat)}")
print(f"Number of NOT DISTRACTED trials on DISTRACTION day is {len(dis_notdis_photo_snips_flat)}")
print(f"Number of DISTRACTED trials on HABITUATION day is {len(hab_dis_photo_snips_flat)}")
print(f"Number of NOT DISTRACTED trials on HABITUATION day is {len(hab_notdis_photo_snips_flat)}")

# Saves resampled and flattened photo data for each day for further ROC analysis

pickle_out = open(outputfolder+"data4roc_photo.pickle", 'wb')
dill.dump([mod_dis_photo_snips_flat, mod_notdis_photo_snips_flat, dis_dis_photo_snips_flat, dis_notdis_photo_snips_flat, hab_dis_photo_snips_flat, hab_notdis_photo_snips_flat], pickle_out)
pickle_out.close()
    
    