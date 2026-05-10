import os
import pandas as pd
import re
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import numpy as np
import matplotlib
from matplotlib import rc
matplotlib.rcParams['font.sans-serif'] = "Arial"
matplotlib.rcParams['font.family'] = "sans-serif"
import matplotlib.gridspec as gridspec

import pdb


def doPlot(line1=None,line2=None,line3=None,line4=None,line5=None,
           line6=None,line7=None,line8=None,line9=None,line10=None,
           bar=None,title=None,leg=None,
           rng=None):
    """
    Plot a basic chart with currency decomposition for a dataframe
    
        df    - dataframe
        title - title for the chart
    """
    
    #bar_colors = ['#135C2A','#249245','#58A618','#B7C82E','#BDD39D',
#             '#80A9BF','#356581','#394A58','#8B92A1','#DCDCE6',
#             '#FF8400','#8B4513','#9370DB','#FF1493','#C800C8',
#             '#D2691E','#FFD700','#DAA520','#CD5C5C','#8470FF']

    bar_colors =  [
    "#8C564B",  # Dark Brown
    "#FF7F0E",  # Dark Orange
    "#2CA02C",  # Forest Green
    "#D62728",  # Red
    "#9467BD",  # Purple
    "#E377C2",  # Pink
    "#7F7F7F",  # Gray
    "#BCBD22",  # Olive
    "#17BECF",  # Cyan
    "#1F77B4",  # Steel Blue
    "#9EDAE5",  # Light Blue
    "#FDCB58",  # Gold
    "#4C78A8",  # Cobalt
    "#FFD700",  # Yellow
    "#6A4C93",  # Plum
]
                 
    bar_colors = ['#1e19bf','#B7C82E','#728764',
                 '#80A9BF','#356581','#394A58','#8B92A1','#DCDCE6',
                 '#FF8400','#8B4513','#9370DB','#FF1493','#C800C8',
                 '#D2691E','#FFD700','#DAA520','#CD5C5C','#8470FF']

    line_colors = ['#58A618', '#356581', '#FF8400', '#8B4513', '#E52B50', '#8B92A1', '#FFD900',
                   '#FF8400','#8B4513','#9370DB']
                  
    ax=plt.gca()
    
    if bar is not None:
        first = rng[0] if rng !=None and len(rng)>0 else bar.index[0]
        last  = rng[1] if rng !=None and len(rng)>1 else bar.index[-1]
    elif line1 is not None:
        first = rng[0] if rng !=None and len(rng)>0 else line1.index[0]
        last  = rng[1] if rng !=None and len(rng)>1 else line1.index[-1]
    
    if bar is not None:
        total = bar.loc[first:last]
        total.plot(ax=ax,kind='bar', rot=0, 
                                         fontsize=5, stacked=True, color=bar_colors,
                                         width = 0.5)

    if line1 is not None:
#        line1[first:last].plot(ax=ax,color = 'white',linewidth=2.5,label='Inline label')
        line1[first:last].plot(ax=ax,color = line_colors[0],linewidth=1.25)
        total = line1[first:last]
    if line2 is not None:
#        line2[first:last].plot(ax=ax,color = 'white',linewidth=2.5)
        line2[first:last].plot(ax=ax,color = line_colors[1],linewidth=1.25)
    if line3 is not None:
#        line3[first:last].plot(ax=ax,color = 'white',linewidth=2.5)
        line3[first:last].plot(ax=ax,color = line_colors[2],linewidth=1.25)
    if line4 is not None:
#        line4[first:last].plot(ax=ax,color = 'white',linewidth=2.5)
        line4[first:last].plot(ax=ax,color = line_colors[3],linewidth=1.25)
    if line5 is not None:
#        line5[first:last].plot(ax=ax,color = 'white',linewidth=2.5)
        line5[first:last].plot(ax=ax,color = line_colors[4],linewidth=1.25)
    if line6 is not None:
#        line6[first:last].plot(ax=ax,color = 'white',linewidth=2.5)
        line6[first:last].plot(ax=ax,color = line_colors[5],linewidth=1.25)
    if line7 is not None:
#        line7[first:last].plot(ax=ax,color = 'white',linewidth=2.5)
        line7[first:last].plot(ax=ax,color = line_colors[6],linewidth=1.25)
    if line8 is not None:
#        line8[first:last].plot(ax=ax,color = 'white',linewidth=2.5)
        line8[first:last].plot(ax=ax,color = line_colors[7],linewidth=1.25)
    if line9 is not None:
#        line9[first:last].plot(ax=ax,color = 'white',linewidth=2.5)
        line9[first:last].plot(ax=ax,color = line_colors[8],linewidth=1.25)
    if line10 is not None:
#        line10[first:last].plot(ax=ax,color = 'white',linewidth=2.5)
        line10[first:last].plot(ax=ax,color = line_colors[9],linewidth=1.25)

    ax=plt.gca()
    ax.grid(which = 'major', axis='y',linestyle='-.', color='#c5d7ed',linewidth=0.1)
    ax.grid(which = 'major', axis='x',linestyle='-.', color='#c5d7ed',linewidth=0.1)

    if leg is not None:
        if len(leg) <5:
            ax.legend(leg,loc='upper center', bbox_to_anchor=(0.5, -0.10),
                    frameon=False, ncol = 4,fontsize=5)
        else:
            ax.legend(leg,loc='upper center', bbox_to_anchor=(0.5, -0.10),
                    frameon=False, ncol = 6,fontsize=5)

    width=0.5
    plt.xlim([-width, len(total.loc[first:last])-width])

    length = total.shape[0]
    n_xticks = []
    n_xticklabels = []
    for i in range(0,length):
            if re.search('M01',total.index[i]) != None \
                or re.search('Q1',total.index[i]) != None \
                or re.search('Y',total.index[i]) != None:
                n_xticks.append(i)
                n_xticklabels.append(total.index[i])

    if len(n_xticks) > 10:
        takeOneFrom = int(np.ceil(len(n_xticks)/10))
        n_xticks = n_xticks[::takeOneFrom]
        n_xticklabels = n_xticklabels[::takeOneFrom]
            
            
            
    ax.set_xticks(n_xticks)
    ax.set_xticklabels(n_xticklabels, fontsize=5,rotation=0)
    
    ax.locator_params(axis='y', nbins=8)
    ax.yaxis.set_tick_params(labelsize=7,rotation=0) 
    
    ax.set_title(title,pad=5)
    ax.title.set_size(5)
    
    
def plot_section(name=None):
    Page = plt.figure(figsize=(11.69,8.27))
    Page.clf()
    if name is None:
        name = 'Section'
    Page.text(0.5,0.5,name, transform=Page.transFigure, size=24, ha="center", fontweight="bold")
    