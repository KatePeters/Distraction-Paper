# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 15:50:43 2020

@author: admin
"""

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
    
    zlo = np.min([np.min(x), np.min(y)])
    zhi = np.max([np.max(x), np.max(y)])
    z = np.linspace(zlo, zhi, N)

    fa, hit = [], []
    
    for i in range(N):
        fa.append(np.count_nonzero(y > z[i])) # faster than np.sum
        hit.append(np.count_nonzero(x > z[i]))
        
    fa.reverse()
    hit.reverse()
    
    fa = np.divide(fa, len(y))
    hit = np.divide(hit, len(x))
    
    fa[0], fa[-1] = 0, 1
    hit[0], hit[-1] = 0, 1
    
    a = np.trapz(fa, hit)
    
    return a

def logical_subset(data, logical, condition=True):
    if condition:
        return [d for d, L in zip(data, logical) if L]
    else:
        return [d for d, L in zip(data, logical) if not L]
    
def rocshuf(x,y,nsims=10):
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
    p1 = len([val for val in a if val >= 0.5+absa])
    p2 = len([val for val in a if val <= 0.5-absa])
    
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
        
        a0, p0 = rocshuf(x0, x1, nsims=n4shuf)
        
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



