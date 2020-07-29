# -*- coding: utf-8 -*-
"""
Created on Wed Feb  5 11:28:04 2020

@author: admin
"""

import tdt
import xlrd
import csv
import numpy as np

import dill

from fx4assembly import *

def metafilemaker(xlfile, metafilename, sheetname='metafile', fileformat='csv'):
    with xlrd.open_workbook(xlfile) as wb:
        sh = wb.sheet_by_name(sheetname)  # or wb.sheet_by_name('name_of_the_sheet_here')
        
        if fileformat == 'csv':
            with open(metafilename+'.csv', 'w', newline="") as f:
                c = csv.writer(f)
                for r in range(sh.nrows):
                    c.writerow(sh.row_values(r))
        if fileformat == 'txt':
            with open(metafilename+'.txt', 'w', newline="") as f:
                c = csv.writer(f, delimiter="\t")
                for r in range(sh.nrows):
                    c.writerow(sh.row_values(r))
    
def metafilereader(filename):
    
    f = open(filename, 'r')
    f.seek(0)
    header = f.readlines()[0]
    f.seek(0)
    filerows = f.readlines()[1:]
    
    tablerows = []
    
    for i in filerows:
        tablerows.append(i.split('\t'))
        
    header = header.split('\t')
    # need to find a way to strip end of line \n from last column - work-around is to add extra dummy column at end of metafile
    return tablerows, header

def loaddata(tdtfile, SigBlue, SigUV):
    
    tdtfile=raw_datafolder+tdtfile
    
    try:
        tmp = tdt.read_block(tdtfile, evtype=['streams'], store=[SigBlue])
        data = getattr(tmp.streams, SigBlue)['data']
        fs = getattr(tmp.streams, SigBlue)['fs']

        tmp = tdt.read_block(tdtfile, evtype=['streams'], store=[SigUV])
        dataUV = getattr(tmp.streams, SigUV)['data']

        ttls = tdt.read_block(tdtfile, evtype=['epocs']).epocs
    except:
        print('Unable to load data properly.')
        data=[]
        dataUV=[]
        ttls=[]
        fs=[]
        
    return data, dataUV, fs, ttls

def process_rat(row_data, sessiontype='dis'):
    print('yo there', row_data[2])
    ratdata={}
    ratdata['rat'] = row_data[2]
    
    # gets photometry signals from TDT file and performs correction
    blue, uv, fs, ttls = loaddata(row_data[0], row_data[12], row_data[13])   
    
    # first line uses Vaibhav correction, second uses Lerner correction
    # filt = correctforbaseline(blue, uv)
    filt, filt_sd = lerner_correction(blue, uv)
    
    # assigns photometry data to output dictionary
    ratdata['blue'] = blue
    ratdata['uv'] = uv
    ratdata['fs'] = fs
    ratdata['filt'] = filt
    ratdata['tick'] = ttls.Tick.onset
    
    try:
        ratdata['filt_sd'] = filt_sd
    except: pass
    
    # gets licks from ttls
    lick = getattr(ttls, row_data[15])    
    ratdata['licks'] = lick.onset
    ratdata['licks_off'] = lick.offset
    
    # Calculates distractors and whether distracted or not
    ratdata['distractors'] = distractionCalc2(ratdata['licks']) 
    [ratdata['distracted'], ratdata['notdistracted']], ratdata['d_bool_array'], ratdata['pdp'], ratdata['pre_dp']  = distracted_or_not(ratdata['distractors'], ratdata['licks'])
    
    return ratdata

# declares locations for data and required files
raw_datafolder = 'D:\\DA_and_Reward\\kp259\\THPH1AND2\\tdtfiles\\'
folder = "C:\\Github\\Distraction-Paper\\"
datafolder = folder+"data\\"
xlfile = datafolder+"distraction_photo_metafile.xlsx"
metafile = datafolder+"metafile"
sheetname="THPH1&2Metafile"

# extracts data from metafile
metafilemaker(xlfile, metafile, sheetname=sheetname, fileformat='txt')
rows, header = metafilereader(metafile + '.txt')

# creates lists that include row indexes for last lick,  distraction, and hab days
rows_mod = []
rows_dis = []
rows_hab = []

for idx, row in enumerate(rows):
    if row[5] == 'D0':
        rows_mod.append(idx)
    elif row[5] == 'D1':
        rows_dis.append(idx)
    elif row[5] == 'D2':
        rows_hab.append(idx)

# makes dictionaries that include data for individual rats for each day (e.g.
# modelled day, distraction day, and habituation day)
disDict = {}
modDict = {}
habDict = {}

for idx in rows_mod:       
    ratdata = process_rat(rows[idx])
    modDict[ratdata['rat']] = ratdata

for idx in rows_dis:       
    ratdata = process_rat(rows[idx])
    disDict[ratdata['rat']] = ratdata
    
for idx in rows_hab:       
    ratdata = process_rat(rows[idx])
    habDict[ratdata['rat']] = ratdata
    
# Saves pickle file with three dictionaries that can be used by Kate's old script
# or new scripts for further analysis
    
savefile=True
outputfile=datafolder+'distraction_data.pickle'

if savefile == True:
    pickle_out = open(outputfile, 'wb')
    dill.dump([modDict, disDict, habDict], pickle_out)
    pickle_out.close()





        