# -*- coding: utf-8 -*-
"""
Created on Wed Feb 19 11:55:06 2020

@author: admin
"""

import time
start_time = time.time()

from fx4roc import *
import numpy as np
import sys
import dill

# args = sys.argv

args = [ [], "C:\\Github\\Distraction-Paper\\notebooks\\hist_licks", "dis_hist", "notdis_hist", 5, "roc_results_licks"]

print("Loading data")

try:
    pickle_in = open(args[1], 'rb')
except FileNotFoundError:
        print('Cannot access pickled file')

# [args[2], args[3]] = dill.load(pickle_in)
[dis_hist, notdis_hist] = dill.load(pickle_in)

print("Running ROC analysis")

# a, p = nanroc(args[2], args[3], n4shuf=args[4])

a, p = nanroc(dis_hist, notdis_hist, n4shuf=args[4])


pickle_out = open(args[5], 'wb')
dill.dump([a, p], pickle_out)
pickle_out.close()

print(f"--- Total ROC analysis took {(time.time() - start_time)} seconds ---")