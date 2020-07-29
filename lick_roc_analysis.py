# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 15:50:43 2020

@author: admin
"""

import dill
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.transforms as transforms
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np

#  import JM_custom_figs.py"

def rocN(x,y,N=100):
    """ Function to calculate ROC based on MATLAB function"""
    if len(x) > 0 and len(y) >0:
        pass
    else:
        print("x and/or y are incorrect form")
        return np.NaN
    
    if len(x)<3 or len(y)<3:
        print('Too few trials for roc analysis!')
        return np.NaN
    
    zlo = min([min(x), min(y)])
    zhi = max([max(x), max(y)])
    z = np.linspace(zlo, zhi, N)

    fa, hit = [], []
    
    for i in range(N):
        fa.append(sum(y > z[i]))
        hit.append(sum(x > z[i]))
        
    fa.reverse()
    hit.reverse()
    
    fa = [f/len(y) for f in fa]
    hit = [h/len(x) for h in hit]
    
    fa[0], fa[-1] = 0, 1
    hit[0], hit[-1] = 0, 1
    
    a = np.trapz(fa, hit)
    
    return a

def logical_subset(data, logical, condition=True):
    if condition:
        return [d for d, L in zip(data, logical) if L]
    else:
        return [d for d, L in zip(data, logical) if not L]
    
def rocshuf(x,y,nsims=100):
    z = x + y
    b = [True for val in x] + [False for val in y]
    n0 = len(b)

    roc0 = rocN(logical_subset(z, b), logical_subset(z, b, condition=False))
    
    a=[]
    for sim in range(nsims):
        I = np.random.permutation(n0)
        B = [b[idx] for idx in I]
        a.append(rocN(logical_subset(z, B), logical_subset(z, B, condition=False)))
 
    absa = np.abs(roc0 -0.5)
    p1 = len([val for val in a if val > 0.5+absa])
    p2 = len([val for val in a if val < 0.5-absa])
    
    p = p1/nsims + p2/nsims
    
    return roc0, p

def nanroc(x, y, N=100, min4roc=4, n4shuf=100):
 
    # checks dimensions of matrices
    if np.shape(x)[1] != np.shape(y)[1]:
        print('nanroc: matrices must have the same number of columns')
    
    a=[]
    p=[]
    
    for idx in range(np.shape(x)[1]):
        print(f"Analysing column {idx}")
        x0 = [val[idx] for val in x]
        x1 = [val[idx] for val in y]
        
        a0, p0 = rocshuf(x0, x1)
        
        a.append(a0)
        p.append(p0)
        
    return a, p


def flatten_list(listoflists):
    try:
        flat_list = [item for sublist in listoflists for item in sublist]
        return flat_list
    except:
        print('Cannot flatten list. Maybe is in the wrong format. Returning empty list.')
        return []
    
    # Makes lick snips for all distractors and then flattens (e.g. pools snips from all rats)

def make_lick_snips(d, pre=10, post=20):
    snips = []
    for dis in d['distractors']:
        snips.append([lick-dis for lick in d['licks'] if (lick-dis>-pre) and (lick-dis<post) ])
        
    return snips


datafolder = "C:\\Github\\Distraction-Paper\\data\\"
figfolder = "C:\\Github\\Distraction-Paper\\figs\\"
outputfolder = "C:\\Github\\Distraction-Paper\\output\\"

try:
    pickle_in = open(datafolder + "distraction_data_only_snips.pickle", 'rb')
except FileNotFoundError:
        print('Cannot access pickled file')

[modDict, disDict, habDict] = dill.load(pickle_in)



rats = disDict.keys()
all_lick_snips = []
for rat in rats:
    d = disDict[rat]
    all_lick_snips.append(make_lick_snips(d))

all_lick_snips_flat = flatten_list(all_lick_snips)

# This cell uses a simple function to check whether any licks occur between 0 and 1 seconds (i.e. is it a distracted snip or not)

def check_val_between(data, x1=0.001, x2=1.000):
    """ Checks if there is a value in a list between two numbers"""
    
    vals = [1 for d in data if d>x1 and d<x2]
    
    if sum(vals) > 0:
        return True
    else:
        return False
    
dis_snips = [snip for snip in all_lick_snips_flat if not check_val_between(snip)]
notdis_snips = [snip for snip in all_lick_snips_flat if check_val_between(snip)]

# turns snips into binned data

bins = np.arange(-10, 20, 1)
dis_hist = [np.histogram(snip, bins=bins)[0] for snip in dis_snips]
notdis_hist = [np.histogram(snip, bins=bins)[0] for snip in notdis_snips]

# a, p = nanroc(dis_hist, notdis_hist)

f, ax = plt.subplots(nrows=3)

ax[0].plot(np.mean(notdis_hist, axis=0), color='grey')
ax[0].plot(np.mean(dis_hist, axis=0), color='red')

ax[0].set_ylabel('Licks (Hz)')
ax[0].set_xticks([])

ax[0].text(0.99, 0.95, 'Distracted', color='red', ha='right', va='top', transform=ax[0].transAxes)
ax[0].text(0.99, 0.80, 'Not distracted', color='grey', ha='right', va='top', transform=ax[0].transAxes)

ax[1].plot(a)
ax[1].set_ylabel('ROC value')
ax[1].set_xticks([])

threshold = 0.05/len(p)
sigpoints = np.array([pval < threshold for pval in p], dtype=bool)

xdata = [x for x, L in zip(range(len(sigpoints)), sigpoints) if L]
ydata = logical_subset(a, sigpoints)
ax[1].scatter(xdata, ydata, color='red')

ax[1]. set_ylim([-0.1, 1.1])

ax[2].plot(p)
ax[2].set_ylim([-0.1, 1.1])
ax[2].set_ylabel('p')

ax[2].set_xticks([0, 10, 20])
ax[2].set_xticklabels(['-10', '0', '10'])
ax[2].set_xlabel('Time from distractor (s)')

f.savefig(outputfolder + "licks_roc_analysis.png")




