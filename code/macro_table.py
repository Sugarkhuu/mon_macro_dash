# to do 

# add salary and income

import pickle
import numpy as np

import sys
sys.path.append('D:\economics\GIT\monmacro\code')
from plotting import *
from montools import *


pickle_in = open("./data/macro_data.pickle","rb")
dd,dm,dq,dy = pickle.load(pickle_in)

tmp = dq.gdp_nom 
tmp.index = pd.period_range(start='2000Q1', periods=len(tmp), freq='Q')
tmp2 = tmp.resample('M').ffill()/3
dm['gdp_nom'] = np.nan
dm.loc['00M01':'25M09','gdp_nom'] = tmp2.values
dm['gdp_nom_y'] = dm['gdp_nom'].rolling(window=12, min_periods=12).sum()
# dm.loc['23M10','gdp_nom_y'] = dm.loc['23M09','gdp_nom_y']
# dm.loc['23M11','gdp_nom_y'] = dm.loc['23M09','gdp_nom_y']
# dm.loc['23M12','gdp_nom_y'] = dm.loc['23M09','gdp_nom_y']


list_m = ['cpi','usd_mnt','rate_pol','rate_loan_mnt_new','rate_timedepo_mnt_new',
        'ms_m2','bank_ass_credit_nfi','dc_loan_corp','dc_loan_ind','gov_rev_eq',
        'gov_exp','ex','im','bop']

list_q = ['gdp','gdp_nom_y','gdp_nom']

# Inflation
dm['cpi_yoy'] = pct(dm.cpi,-12)
dm['cpi_qoq'] = pct(dm.cpi,-3)*4
dm['cpi_mom'] = pct(dm.cpi,-1)

# FX
dm['usd_mnt_yoy'] = pct(dm.usd_mnt,-12)
dm['usd_mnt_qoq'] = pct(dm.usd_mnt,-3)*4
dm['usd_mnt_mom'] = pct(dm.usd_mnt,-1)
dm['cny_mnt_yoy'] = pct(dm.cny_mnt,-12)
dm['cny_mnt_qoq'] = pct(dm.cny_mnt,-3)*4
dm['cny_mnt_mom'] = pct(dm.cny_mnt,-1)

# Money supply
dm['ms_m2_yoy'] = pct(dm.ms_m2,-12)
dm['ms_m2_qoq'] = pct(dm.ms_m2,-3)*4
dm['ms_m2_mom'] = pct(dm.ms_m2,-1)
dm['m2_gdp'] = dm['ms_m2']/dm['gdp_nom_y']*100
dm['ms_m2'] = dm['ms_m2']/1e6

# Loan
dm['bank_ass_credit_nfi'] = dm.bank_ass_credit_nfi/1e6
dm['bank_ass_credit_nfi_yoy'] = pct(dm.bank_ass_credit_nfi,-12)
dm['bank_ass_credit_nfi_qoq'] = pct(dm.bank_ass_credit_nfi,-3)*4
dm['bank_ass_credit_nfi_mom'] = pct(dm.bank_ass_credit_nfi,-1)
dm['loan_gdp'] = dm['bank_ass_credit_nfi']/dm['gdp_nom_y']*100

dm['dc_loan_ind'] = dm.dc_loan_ind/1e6
dm['dc_loan_ind_yoy'] = pct(dm.dc_loan_ind,-12)
dm['dc_loan_ind_qoq'] = pct(dm.dc_loan_ind,-3)*4
dm['dc_loan_ind_mom'] = pct(dm.dc_loan_ind,-1)
dm['loan_ind_gdp'] = dm['dc_loan_ind']/dm['gdp_nom_y']*100

dm['dc_loan_corp'] = dm.dc_loan_corp/1e6
dm['dc_loan_corp_yoy'] = pct(dm.dc_loan_corp,-12)
dm['dc_loan_corp_qoq'] = pct(dm.dc_loan_corp,-3)*4
dm['dc_loan_corp_mom'] = pct(dm.dc_loan_corp,-1)
dm['loan_corp_gdp'] = dm['dc_loan_corp']/dm['gdp_nom_y']*100

# GDP
dq['gdp_q1'] = pct(dq.gdp,-4)
dq['gdp_q2'] = pct(dq['gdp'].rolling(window=2, min_periods=1).sum(),-4)
dq['gdp_q3'] = pct(dq['gdp'].rolling(window=3, min_periods=1).sum(),-4)
dq['gdp_q4'] = pct(dq['gdp'].rolling(window=4, min_periods=1).sum(),-4)

# Budget 
dm['gov_rev_cum_yoy'] = pct(dm.gov_rev_cum,-12)
dm['gov_exp_cum_yoy'] = pct(dm.gov_exp_cum,-12)
dm['rev_gdp'] = dm['gov_rev_cum']/dm['gdp_nom_y']*100
dm['exp_gdp'] = dm['gov_exp_cum']/dm['gdp_nom_y']*100
dm['gov_rev_cum'] = dm['gov_rev_cum']/1e6
dm['gov_exp_cum'] = dm['gov_exp_cum']/1e6

# Trade
dm['ex_cum_yoy'] = pct(dm.ex_cum,-12)
dm['im_cum_yoy'] = pct(dm.im_cum,-12)
dm['ex_gdp'] = dm['ex_cum']*dm['usd_mnt']/dm['gdp_nom_y']*100
dm['im_gdp'] = dm['im_cum']*dm['usd_mnt']/dm['gdp_nom_y']*100
dm['ex_cum'] = dm['ex_cum']/1e3
dm['im_cum'] = dm['im_cum']/1e3
dm['fx_reserve'] = dm['fx_reserve']/1e3

# Household finance
dq['hh_exp_inc'] = dq.hh_inc/dq.hh_exp*100
dq['hh_inc_yoy'] = pct(dq.hh_inc,-4)
dq['hh_exp_yoy'] = pct(dq.hh_exp,-4)

dm['ex_coal_vol_cum'] = dm['ex_coal_vol_cum']/1e3
dm['ex_coal_cum'] = dm['ex_coal_cum']/1e6


var_m = ['cpi_yoy',
         'cpi_qoq',
         'cpi_mom',
         'usd_mnt',
         'usd_mnt_yoy',
         'usd_mnt_qoq',
         'usd_mnt_mom',
         'cny_mnt',
         'cny_mnt_yoy',
         'cny_mnt_qoq',
         'cny_mnt_mom',
         'rate_pol',
         'rate_loan_mnt_new',
         'rate_timedepo_mnt_new',
         'ms_m2_yoy',
         'ms_m2_qoq',
         'ms_m2_mom',
         'ms_m2',
         'm2_gdp',
         'bank_ass_credit_nfi',
         'bank_ass_credit_nfi_yoy',
         'bank_ass_credit_nfi_qoq',
         'bank_ass_credit_nfi_mom',
         'loan_gdp',
         'dc_loan_ind',
         'dc_loan_ind_yoy',
         'dc_loan_ind_qoq',
         'dc_loan_ind_mom',
         'loan_ind_gdp',
         'dc_loan_corp',
         'dc_loan_corp_yoy',
         'dc_loan_corp_qoq',
         'dc_loan_corp_mom',
         'loan_corp_gdp',
         'gov_rev_cum_yoy',
         'gov_rev_cum',
         'rev_gdp',
         'gov_exp_cum_yoy',
         'gov_exp_cum',
         'exp_gdp',
         'ex_cum_yoy',
         'ex_cum',
         'ex_gdp',
         'ex_coal_vol_cum',
         'ex_coal_cum', 
         'ex_coal_p',
         'im_cum_yoy',
         'im_cum',
         'im_gdp',
         'fx_reserve']
var_q = ['gdp_q1',
         'gdp_q2',
         'gdp_q3',
         'gdp_q4',
         'hh_inc',
         'hh_exp_inc',
         'hh_inc_yoy',
         'hh_exp_yoy']


# # real and fiscal
# var_m.extend(['gov_rev_eq','gov_exp'])
# var_q = ['gdp_q1','gdp_q2']
# var_m.extend(['usd_mnt','fx_reserve','cpi_yoy','cpi_mom'])
# # rates and money
# dm['m2_yoy'] = pct(dm.ms_m2,-12)
# dm['loan_yoy'] = pct(dm.bank_ass_credit_nfi,-12)
# dm['npl_ratio'] = dm.bank_ass_credit_npl/dm.bank_ass_credit_nfi*100
# var_m.extend(['rate_pol','rate_depo_mnt_new','rate_loan_mnt_new', 
#               'm2_yoy','loan_yoy','npl_ratio'])
# # external
# var_m.extend(['bop_ca_gs','ex','im','bop'])

dmt = dm[var_m]
dmt = dmt.iloc[-50:]
dmt = dmt.transpose()

dqt = dq[var_q]
dqt = dqt.iloc[-18:]
dqt = dqt.transpose()

with pd.ExcelWriter('main_indicators.xlsx', engine='xlsxwriter') as writer:
    dmt.to_excel(writer, sheet_name='m')
    dqt.to_excel(writer, sheet_name='q')
writer.close()


# dmt.to_csv('main_indicators_m.csv')
# dqt.to_csv('main_indicators_q.csv')