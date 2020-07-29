# -*- coding: utf-8 -*-
"""
Created on Thu Feb  6 10:09:19 2020

@author: admin
"""

import dill

import numpy as np
import matplotlib.pyplot as plt

"""
this function makes 'snips' of a data file ('data' single scalar) aligned to an
event of interest ('event', list of times in seconds).

If a timelocked map is needed to align data precisely (e.g. with TDT equipment)
then it is necessary to pass a t2sMap to the function.

preTrial and trialLength are in seconds.

Will put data into bins if requested.

"""
def time2samples(data, tick, fs):
    maxsamples = len(tick)*int(fs)
    if (len(data) - maxsamples) > 2*int(fs):
        print('Something may be wrong with conversion from time to samples')
        print(str(len(data) - maxsamples) + ' samples left over. This is more than double fs.')
        t2sMap = np.linspace(min(tick), max(tick), maxsamples)
    else:
        t2sMap = np.linspace(min(tick), max(tick), maxsamples)
        
    return t2sMap    
    
def event2sample(EOI):
    idx = (np.abs(t2sMap - EOI)).argmin()   
    return idx

def lickCalc(licks, offset = [], burstThreshold = 0.25, runThreshold = 10, 
             binsize=60, histDensity = False, adjustforlonglicks='none'):
    # makes dictionary of data relating to licks and bursts
    if type(licks) != np.ndarray or type(offset) != np.ndarray:
        try:
            licks = np.array(licks)
            offset = np.array(offset)
        except:
            print('Licks and offsets need to be arrays and unable to easily convert.')
            return

    lickData = {}

    if len(offset) > 0:        
        lickData['licklength'] = offset - licks[:len(offset)]
        lickData['longlicks'] = [x for x in lickData['licklength'] if x > 0.3]
    else:
        lickData['licklength'] = []
        lickData['longlicks'] = []
    
    if adjustforlonglicks != 'none':
        if len(lickData['longlicks']) == 0:
            print('No long licks to adjust for.')
        else:
            lickData['median_ll'] = np.median(lickData['licklength'])
            lickData['licks_adj'] = int(np.sum(lickData['licklength'])/lickData['median_ll'])
            if adjustforlonglicks == 'interpolate':
                licks_new = []
                for l, off in zip(licks, offset):
                    x = l
                    while x < off - lickData['median_ll']:
                        licks_new.append(x)
                        x = x + lickData['median_ll']
                licks = licks_new
        
    lickData['licks'] = licks
    lickData['ilis'] = np.diff(np.concatenate([[0], licks]))
    lickData['shilis'] = [x for x in lickData['ilis'] if x < burstThreshold]
    lickData['freq'] = 1/np.mean([x for x in lickData['ilis'] if x < burstThreshold])
    lickData['total'] = len(licks)
    
    # Calculates start, end, number of licks and time for each BURST 
    lickData['bStart'] = [val for i, val in enumerate(lickData['licks']) if (val - lickData['licks'][i-1] > burstThreshold)]  
    lickData['bInd'] = [i for i, val in enumerate(lickData['licks']) if (val - lickData['licks'][i-1] > burstThreshold)]
    lickData['bEnd'] = [lickData['licks'][i-1] for i in lickData['bInd'][1:]]
    lickData['bEnd'].append(lickData['licks'][-1])

    lickData['bLicks'] = np.diff(lickData['bInd'] + [len(lickData['licks'])])    
    lickData['bTime'] = np.subtract(lickData['bEnd'], lickData['bStart'])
    lickData['bNum'] = len(lickData['bStart'])
    if lickData['bNum'] > 0:
        lickData['bMean'] = np.nanmean(lickData['bLicks'])
        lickData['bMean-first3'] = np.nanmean(lickData['bLicks'][:3])
    else:
        lickData['bMean'] = 0
        lickData['bMean-first3'] = 0
    
    lickData['bILIs'] = [x for x in lickData['ilis'] if x > burstThreshold]

    # Calculates start, end, number of licks and time for each RUN
    lickData['rStart'] = [val for i, val in enumerate(lickData['licks']) if (val - lickData['licks'][i-1] > runThreshold)]  
    lickData['rInd'] = [i for i, val in enumerate(lickData['licks']) if (val - lickData['licks'][i-1] > runThreshold)]
    lickData['rEnd'] = [lickData['licks'][i-1] for i in lickData['rInd'][1:]]
    lickData['rEnd'].append(lickData['licks'][-1])

    lickData['rLicks'] = np.diff(lickData['rInd'] + [len(lickData['licks'])])    
    lickData['rTime'] = np.subtract(lickData['rEnd'], lickData['rStart'])
    lickData['rNum'] = len(lickData['rStart'])

    lickData['rILIs'] = [x for x in lickData['ilis'] if x > runThreshold]
    try:
        lickData['hist'] = np.histogram(lickData['licks'][1:], 
                                    range=(0, 3600), bins=int((3600/binsize)),
                                          density=histDensity)[0]
    except TypeError:
        print('Problem making histograms of lick data')
        
    return lickData

def snipper(data, timelock, fs = 1, t2sMap = [], preTrial=10, trialLength=30,
                 adjustBaseline = True,
                 bins = 0):

    if len(timelock) == 0:
        print('No events to analyse! Quitting function.')
        raise Exception('no events')

    pps = int(fs) # points per sample
    pre = int(preTrial*pps) 
#    preABS = preTrial
    length = int(trialLength*pps)
# converts events into sample numbers
    event=[]
    if len(t2sMap) > 1:
        for x in timelock:
            event.append(np.searchsorted(t2sMap, x, side="left"))
    else:
        event = [x*fs for x in timelock]

    new_events = []
    for x in event:
        if int(x-pre) > 0:
            new_events.append(x)
    event = new_events

    nSnips = len(event)
    snips = np.empty([nSnips,length])
    avgBaseline = []

    for i, x in enumerate(event):
        start = int(x) - pre
        avgBaseline.append(np.mean(data[start : start + pre]))
        try:
            snips[i] = data[start : start+length]
        except ValueError: # Deals with recording arrays that do not have a full final trial
            snips = snips[:-1]
            avgBaseline = avgBaseline[:-1]
            nSnips = nSnips-1

    if adjustBaseline == True:
        snips = np.subtract(snips.transpose(), avgBaseline).transpose()
        snips = np.divide(snips.transpose(), avgBaseline).transpose()

    if bins > 0:
        if length % bins != 0:
            snips = snips[:,:-(length % bins)]
        totaltime = snips.shape[1] / int(fs)
        snips = np.mean(snips.reshape(nSnips,bins,-1), axis=2)
        pps = bins/totaltime
              
    return snips, pps

def mastersnipper(data, dataUV, data_filt,
                  t2sMap, fs, bgMAD,
                  events,
                  bins=300,
                  baselinebins=100,
                  preTrial=10,
                  trialLength=30,    
                  threshold=8,
                  peak_between_time=[0, 1],
                  latency_events=[],
                  latency_direction='pre',
                  max_latency=30,
                  verbose=True):
    
    if len(events) < 1:
        print('Cannot find any events. All outputs will be empty.')
        blueTrials, uvTrials, filtTrials, filtTrials_z, filtTrials_z_adjBL, filt_avg, filt_avg_z, noiseindex, peak, latency = ([] for i in range(10))
    else:
        if verbose: print('{} events to analyze.'.format(len(events)))
        
        blueTrials,_ = snipper(data, events,
                                   t2sMap=t2sMap,
                                   fs=fs,
                                   bins=bins,
                                   preTrial=preTrial,
                                   trialLength=trialLength)
        uvTrials,_ = snipper(dataUV, events,
                                   t2sMap=t2sMap,
                                   fs=fs,
                                   bins=bins,
                                   preTrial=preTrial,
                                   trialLength=trialLength)
        filtTrials,_ = snipper(data_filt, events,
                                   t2sMap=t2sMap,
                                   fs=fs,
                                   bins=bins,
                                   preTrial=preTrial,
                                   trialLength=trialLength,
                                   adjustBaseline=False)
        
        filtTrials_z = zscore(filtTrials, baseline_points=baselinebins)
        filtTrials_z_adjBL = zscore(filtTrials, baseline_points=50)

        sigSum = [np.sum(abs(i)) for i in filtTrials]
        sigSD = [np.std(i) for i in filtTrials]

        noiseindex = [i > bgMAD*threshold for i in sigSum]
                        
        # do i need to remove noise trials first before averages
        filt_avg = np.mean(removenoise(filtTrials, noiseindex), axis=0)
        if verbose: print('{} noise trials removed'.format(sum(noiseindex)))
        filt_avg_z = zscore(filt_avg)

    
        bin2s = bins/trialLength
        peakbins = [int((preTrial+peak_between_time[0])*bin2s),
                    int((preTrial+peak_between_time[1])*bin2s)]
        peak = [np.mean(trial[peakbins[0]:peakbins[1]]) for trial in filtTrials_z]
        
        latency = []

        if len(latency_events) > 1: 
            for event in events:
                if latency_direction == 'pre':
                    try:
                        latency.append(np.abs([lat-event for lat in latency_events if lat-event<0]).min())
                    except ValueError:
                        latency.append(np.NaN)
                
                elif latency_direction == 'post':
                    try:
                        latency.append(np.abs([lat-event for lat in latency_events if lat-event>0]).min())
                    except ValueError:
                        latency.append(np.NaN)

            latency = [x if (x<max_latency) else np.NaN for x in latency]
            if latency_direction == 'pre':
                latency = [-x for x in latency]
        else:
            print('No latency events found')

    output = {}
    output['blue'] = blueTrials
    output['uv'] = uvTrials
    output['filt'] = filtTrials
    output['filt_z'] = filtTrials_z
    output['filt_z_adjBL'] = filtTrials_z_adjBL
    output['filt_avg'] = filt_avg
    output['filt_avg_z'] = filt_avg_z
    output['noise'] = noiseindex
    output['peak'] = peak
    output['latency'] = latency
    
    return output

def zscore(snips, baseline_points=100):
    
    BL_range = range(baseline_points)
    z_snips = []
    try:
        for i in snips:
            mean = np.mean(i[BL_range])
            sd = np.std(i[BL_range])
            z_snips.append([(x-mean)/sd for x in i])
    except IndexError:
        mean = np.mean(snips[BL_range])
        sd = np.std(snips[BL_range])
        z_snips = [(x-mean)/sd for x in snips]

    return z_snips

"""
This function will check for traces that are outliers or contain a large amount
of noise, relative to other trials (or relative to the whole data file.
"""


def findnoise(data, background, t2sMap = [], fs = 1, bins=0, method='sd'):
    
    bgSnips, _ = snipper(data, background, t2sMap=t2sMap, fs=fs, bins=bins, 
                        adjustBaseline=False)
  
    if method == 'sum':
        bgSum = [np.sum(abs(i)) for i in bgSnips]
        bgMAD = med_abs_dev(bgSum)
    elif method == 'sd':
        bgSD = [np.std(i) for i in bgSnips]
        bgMAD = med_abs_dev(bgSD)
   
    return bgMAD

def removenoise(snipsIn, noiseindex):
    snipsOut = np.array([x for (x,v) in zip(snipsIn, noiseindex) if not v])   
    return snipsOut

def findphotodiff(blue, UV, noise):
    blueNoNoise = removenoise(blue, noise)
    UVNoNoise = removenoise(UV, noise)
    diffSig = blueNoNoise-UVNoNoise
    return diffSig

def makerandomevents(minTime, maxTime, spacing = 77, n=100):
    events = []
    total = maxTime-minTime
    start = 0
    for i in np.arange(0,n):
        if start > total:
            start = start - total
        events.append(start)
        start = start + spacing
    events = [i+minTime for i in events]
    return events

def med_abs_dev(data, b=1.4826):
    median = np.median(data)
    devs = [abs(i-median) for i in data]
    mad = np.median(devs)*b
                   
    return mad

# Load assembled files from pickle file
# Gets dictionaries with ratadata for modelled, distraction and hab days

datafolder = "C:\\Github\\Distraction-Paper\\data\\"

try:
    pickle_in = open(datafolder + "distraction_data.pickle", 'rb')
except FileNotFoundError:
        print('Cannot access pickled file')

[modDict, disDict, habDict] = dill.load(pickle_in)

for d, s in zip([modDict, disDict, habDict],
                ['modelled', 'distraction', 'habituation']):
    
    for rat in d.keys():
       
        ratdata = d[rat]
        
        print('Analysing rat {} in {} session'.format(rat, s))
        
        data = ratdata['blue']
        dataUV = ratdata['uv']
        data_filt = ratdata['filt']
        fs = ratdata['fs']
        tick = ratdata['tick']
        
        ratdata['lickdata'] = lickCalc(ratdata['licks'],
                                       offset=ratdata['licks_off'])
        
        bins=200
        baselinebins=40
        preTrial=5
        trialLength=20
        
        t2sMap = time2samples(data, tick, fs)
        
        randomevents = makerandomevents(120, max(tick)-120)
        
        bgTrials, pps = snipper(data, randomevents,
                                t2sMap = t2sMap, fs=fs, bins=bins)
        
        bgMAD = findnoise(data_filt, randomevents, t2sMap=t2sMap, fs=fs,
                          bins=bins, method='sum')
        
        ratdata['snips_distractors'] = mastersnipper(data, dataUV, data_filt,
                                                     t2sMap, fs, bgMAD,
                                                     ratdata['distractors'],
                                                     bins=200,
                                                     baselinebins=40,
                                                     preTrial=5,
                                                     trialLength=20,                                                    
                                                     latency_events=ratdata['licks'],
                                                     latency_direction='post')
        
        ratdata['snips_distracted'] = mastersnipper(data, dataUV, data_filt,
                                                      t2sMap, fs, bgMAD,
                                                      ratdata['distracted'],
                                                      bins=200,
                                                      baselinebins=40,
                                                      preTrial=5,
                                                      trialLength=20)
        
        ratdata['snips_not-distracted'] = mastersnipper(data, dataUV, data_filt,
                                                      t2sMap, fs, bgMAD,
                                                      ratdata['notdistracted'],
                                                      bins=200,
                                                      baselinebins=40,
                                                      preTrial=5,
                                                      trialLength=20)


save_total_file=True
save_reduced_file=True

# saves pickled file including full dictionaries

if save_total_file == True:
    outputfile=datafolder+'distraction_data_with_snips.pickle'
    pickle_out = open(outputfile, 'wb')
    dill.dump([modDict, disDict, habDict], pickle_out)
    pickle_out.close()

# removes large, streaming variables and saves reduced file
if save_reduced_file == True:
    for d in [modDict, disDict, habDict]:
        for rat in d.keys():
            for item_to_be_removed in ['blue', 'uv', 'filt']:
                del d[rat][item_to_be_removed]

    outputfile=datafolder+'distraction_data_only_snips.pickle'

    pickle_out = open(outputfile, 'wb')
    dill.dump([modDict, disDict, habDict], pickle_out)
    pickle_out.close()
    


