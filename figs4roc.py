# -*- coding: utf-8 -*-
"""
Created on Wed Feb 26 13:44:02 2020

@author: admin
"""

import numpy as np

import matplotlib.gridspec as gridspec
from matplotlib.colors import LinearSegmentedColormap

from fx4roc import logical_subset
from JM_custom_figs import shadedError


def plot_ROC_and_line(f, a, p, snips1, snips2,
                      cdict=['grey', 'white', 'red'],
                      colors=['grey', 'red'],
                      labels=["", ""],
                      labeloffset=0,
                      ylabel=''
                      ):
    
    ax=[]
    
    gs=gridspec.GridSpec(2,2, figure=f, height_ratios=[0.25, 1], width_ratios=[1, 0.05], wspace=0.05,
                        bottom=0.2, right=0.75, left=0.15)
    
    ax.append(f.add_subplot(gs[0, 0]))
    
    # Creates colormap for ROC

    heatmap_color_scheme = LinearSegmentedColormap.from_list('rocmap', cdict)
    
    roc_for_plot = a + [0]
    xlen=len(snips1[0])
    xvals=np.arange(-0.5,xlen+0.5)
    yvals=[1, 2]
    xx, yy = np.meshgrid(xvals, yvals)
        
    mesh = ax[0].pcolormesh(xx, yy, [roc_for_plot, roc_for_plot], cmap=heatmap_color_scheme, shading = 'flat')
    mesh.set_clim([0, 1])
    
    threshold = 0.05/len(p)
    sigpoints = np.array([pval < threshold for pval in p], dtype=bool)
    
    if sum(sigpoints) > 0:
        xdata = [x for x, L in zip(range(len(sigpoints)), sigpoints) if L]
        ydata = logical_subset(a, sigpoints)
        ax[0].scatter(xdata, [2.5]*len(xdata), color='k', marker='.', clip_on=False)
    else:
        ax[0].scatter(2, 2.5, color='white', marker='.', clip_on=False)
    
    ax[0].text(-1, 2.5, 'p<0.05', va='center', ha='right')
    
    ax[0].spines['top'].set_visible(False)
    ax[0].spines['right'].set_visible(False)
    ax[0].spines['bottom'].set_visible(False)
    ax[0].spines['left'].set_visible(False)
    ax[0].set_xticks([])
    ax[0].set_yticks([])
     
    cbar_ax = f.add_subplot(gs[0,1])   
    cbar = f.colorbar(mesh, cax=cbar_ax, ticks=[0, 1], label='ROC')
    
    ax.append(f.add_subplot(gs[1, 0]))
    
    shadedError(ax[1], snips1, linecolor=colors[0])
    shadedError(ax[1], snips2, linecolor=colors[1])
    
    ax[1].set_ylabel(ylabel)
    ax[1].spines['top'].set_visible(False)
    ax[1].spines['right'].set_visible(False)
    
    ax[1].set_xticks([0, 5, 10, 15])
    ax[1].set_xticklabels(['-5', '0', '5', '10'])
    ax[1].set_xlabel('Time from distractor (s)')
    
    ax[1].text(20, np.mean(snips1, axis=0)[-1]-labeloffset, labels[0], color=colors[0], ha='left', va='center')
    ax[1].text(20, np.mean(snips2, axis=0)[-1]+labeloffset, labels[1], color=colors[1], ha='left', va='center')
    
    ax[0].set_xlim(ax[1].get_xlim())
    
    return f, ax