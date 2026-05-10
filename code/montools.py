import re
from statsmodels.tsa.seasonal import seasonal_decompose
import pandas as pd
import numpy as np

def pct(ts, lag=-1):
    
    res = 100*ts.diff(-lag)/ts.shift(-lag)
    
    return res

def sa(ts):
    
    ts = ts.dropna()
    
    if re.search('M',ts.index[0]) is not None:
        my_freq=12
    elif re.search('Q',ts.index[0]) is not None:
        my_freq=4
    else:
        raise Exception("Only monthly or quarterly data can be seasonally adjusted!")

    res = seasonal_decompose(ts, model='additive', period=12) #, extrapolate_trend='freq',two_sided = True
    # breakpoint()
    ts = ts-res.seasonal    
    return ts


def date_dec(ts):
    # decompose date
    ts = ts.reset_index()
    pattern = r'(\d{1,2})([M|Q|Y])(\d{1,2})'
    matches = ts[ts.columns[0]].str.extract(pattern)
    ts[['year', 'freq', 'period']] = matches
    return ts

def convert(ts,freq,method='sum'):
    if method == 'sum':
        if 'Q' in ts.index[-1] and freq == 'y':
            ts  = date_dec(ts)
            tsn = ts.groupby('year')[ts.columns[1]].sum()
            tsn = tsn.reset_index()
            tsn['year']=tsn['year']+'Y'
            tsn = tsn.set_index('year')
        elif 'M' in ts.index[-1] and freq == 'y':
            ts  = date_dec(ts)
            tsn = ts.groupby('year')[ts.columns[1]].sum()
            tsn = tsn.reset_index()
            tsn['year']=tsn['year']+'Y'
            tsn = tsn.set_index('year')
        elif 'M' in ts.index[-1] and freq == 'q':
            ts.index = pd.to_datetime(ts.index, format='%yM%m')
            tsn = ts.resample('Q').sum()
            tsn.index = tsn.index.year.astype(str).str[-2:] + 'Q' + tsn.index.quarter.astype(str)
    elif method == 'last':
        if 'Q' in ts.index[-1] and freq == 'y':
            ts  = date_dec(ts)
            tsn = ts.groupby('year')[ts.columns[1]].last()
            tsn = tsn.reset_index()
            tsn['year']=tsn['year']+'Y'
            tsn = tsn.set_index('year')
        elif 'M' in ts.index[-1] and freq == 'y':
            ts  = date_dec(ts)
            tsn = ts.groupby('year')[ts.columns[1]].last()
            tsn = tsn.reset_index()
            tsn['year']=tsn['year']+'Y'
            tsn = tsn.set_index('year')
    elif method == 'average':
        if 'Q' in ts.index[-1] and freq == 'y':
            ts  = date_dec(ts)
            tsn = ts.groupby('year')[ts.columns[1]].mean()
            tsn = tsn.reset_index()
            tsn['year']=tsn['year']+'Y'
            tsn = tsn.set_index('year')
        elif 'M' in ts.index[-1] and freq == 'y':
            ts  = date_dec(ts)
            tsn = ts.groupby('year')[ts.columns[1]].mean()
            tsn = tsn.reset_index()
            tsn['year']=tsn['year']+'Y'
            tsn = tsn.set_index('year')
        elif 'M' in ts.index[-1] and freq == 'q':
            ts.index = pd.to_datetime(ts.index, format='%yM%m')
            tsn = ts.resample('Q').mean()
            tsn.index = tsn.index.year.astype(str).str[-2:] + 'Q' + tsn.index.quarter.astype(str)

    return tsn


def bmerge(ts1, ts2):
    # base merge
    tmp = ts2/ts1
    ts1  = ts1 * tmp.loc[tmp.dropna().index[0]]
    ts1 = dmerge(ts1, ts2)
    return ts1

def dmerge(ts1, ts2):
    # direct merge
    for ind in ts2.index:
        if not np.isnan(ts2[ind]):
            ts1[ind] = ts2[ind]
       
    return ts1

def get(ts, what):
    
    if what == 'first':
        that = ts.dropna().index[0]
    if what == 'last':
        that = ts.dropna().index[-1]
    
    return that

def uncumul(ts): 
    ts_new = ts.diff()
    if isinstance(ts, pd.DataFrame):
        ts_new[ts_new.iloc[:,0]<0] = ts[ts_new.iloc[:,0]<0]
    elif isinstance(ts, pd.Series):
        ts_new[ts_new.iloc[:,]<0] = ts[ts_new.iloc[:,]<0]
    return ts_new
#def convert(ts, freq2):
    
#    if re.search('M',ts.index[0]):
#        freq1 = 12
#    elif re.search('Q',ts.index[0]):
#        freq1 = 4
#    elif re.search('Y',ts.index[0]):
#        freq1 = 1
#        
#    if freq2 == 'm':
#        freq2 = 12
#    elif freq2 == 'q':
#        freq2 = 4
#    elif freq2 == 'y':
#        freq2 = 1
#        
#    if freq1==freq2:
#        ts = ts
#    if freq1>freq2:
#        
#    
#    if freq1 == 12:
#        if freq2 == 4:
#            q1
#        if freq2 == 1:
#            
#    if freq1 == 4:
#        if freq2 == 1:
#        
#    pd.to_datetime(df.index)        
    
    
        