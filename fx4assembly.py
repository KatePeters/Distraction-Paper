# -*- coding: utf-8 -*-
"""
Created on Wed Feb  5 12:39:35 2020

@author: admin
"""
import numpy as np
import scipy.signal as sig

def correctforbaseline(blue, uv):
    pt = len(blue)
    X = np.fft.rfft(uv, pt)
    Y = np.fft.rfft(blue, pt)
    Ynet = Y-X

    datafilt = np.fft.irfft(Ynet)

    datafilt = sig.detrend(datafilt)

    b, a = sig.butter(9, 0.012, 'low', analog=True)
    datafilt = sig.filtfilt(b, a, datafilt)
    
    return datafilt

def lerner_correction(blue, uv):
    x = np.array(uv)
    y = np.array(blue)
    bls = np.polyfit(x, y, 1)
    Y_fit_all = np.multiply(bls[0], x) + bls[1]
    Y_dF_all = y - Y_fit_all
    dFF = np.multiply(100, np.divide(Y_dF_all, Y_fit_all))
    std_dFF = np.std(dFF)
    
    return [dFF, std_dFF]

def remcheck(val, range1, range2):
    # function checks whether value is within range of two decimels
    if (range1 < range2):
        if (val > range1) and (val < range2):
            return True
        else:
            return False
    else:
        if (val > range1) or (val < range2):
            return True
        else:
            return False

def distractionCalc2(licks, pre=1, post=1):
    """
    Works out from list of lick timestamps when distractors should occur
    """
    
    licks = np.insert(licks, 0, 0)
    b = 0.001
    d = []
    idx = 3
    
    while idx < len(licks):
        if licks[idx]-licks[idx-2] < 1 and remcheck(b, licks[idx-2] % 1, licks[idx] % 1) == False:
                d.append(licks[idx])
                b = licks[idx] % 1
                idx += 1
                try:
                    while licks[idx]-licks[idx-1] < 1:
                        b = licks[idx] % 1
                        idx += 1
                except IndexError:
                    pass
        else:
            idx +=1
            
    if d[-1] > 3599:
        d = d[:-1]
    
    return d

def distracted_or_not(distractors, licks, delay=1):   
    pdp = [] # post-distraction pause
    pre_dp = [] # pre-distraction pause
    distractedArray = []

    for d in distractors:               
        try:
            pdp.append([lick - d for lick in licks if (lick > d)][0])
        except IndexError:
            pdp.append(3600-d) # designates end of session as max pdp
            
        distractor_index = [idx for idx, lick in enumerate(licks) if lick == d][0]
        try:
            pre_dp.append(-[ili for ili in np.diff(licks[distractor_index::-1]) if ili < -1][0])
        except IndexError:
            pre_dp.append(licks[0]) # if it is at the start of session then uses time from start 

    distracted_boolean_array = np.array([i>delay for i in pdp], dtype=bool)
    
    distracted = [d for d,l in zip(distractors, distracted_boolean_array) if l]
    notdistracted = [d for d,l in zip(distractors, distracted_boolean_array) if not l] 
    
    if np.isnan(pdp)[-1] == 1: 
        distracted_boolean_array[-1] = True
        
    if len(pre_dp) == len(pdp) == len(distracted_boolean_array):
        pass
    else:
        print('Numbers of pdps, pre-dps and distractors do not match. Something might be wrong')
    
    return [distracted, notdistracted], distracted_boolean_array, pdp, pre_dp