# to do
# share of GDP for banking sector, ms, budget, trade variables
# add new variables, debt
# FX and BOP, Trade and Gov
# Credit growth, MS, inflation, FX, GDP, Interest rate

name_date = '2024M10'

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
import pickle

import pandas as pd
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


import sys
sys.path.insert(0,'codes')
sys.path.insert(0,'data')

#sugar = r"C:\\Users\sugar\Documents\econ\chartreport"
# sugar = r"D:\\Xac\econ\chartreport"
# direc = r"E:\Git\macro\chartreport"
# direc = r"D:\economics\GIT\monmacro\code"

# os.chdir(direc.replace('\\', '/'))

fig_dir = 'figures/'

import sys
sys.path.append('S:\docs\repo\monmacro\code')

from plotting import *
from montools import *

db_d    = './data/data_daily.xlsx'
db_m    = './data/data_monthly.xlsx'
db_q    = './data/data_quarterly.xlsx'
db_y    = './data/data_yearly.xlsx'

dd = pd.read_excel(db_d, sheet_name = "data",index_col=0)
dm = pd.read_excel(db_m, sheet_name = "data",index_col=0)
dq = pd.read_excel(db_q, sheet_name = "data", index_col=0)
dy = pd.read_excel(db_y, sheet_name = "data", index_col=0)

# dm.index = dm.index.str.replace("^[0-9]{2}","")
dm = dm.dropna(how = 'all')
# dq.index = dq.index.str.replace("^[0-9]{2}","")
# dq.index = dq.index.str.replace("Q0","Q")
dq = dq.dropna(how = 'all')
# dy.index = dy.index.str.replace("^[0-9]{2}","")
dy.index = dy.index.str.replace("Y01","Y")
dy = dy.dropna(how = 'all')

dm.index.name = None
dq.index.name = None
dy.index.name = None

my_colors = ['#58A618','#B7C82E','#BDD39D',
             '#80A9BF','#356581','#394A58','#8B92A1','#DCDCE6',
             '#FF8400','#8B4513','#9370DB','#FF1493','#C800C8',
             '#D2691E','#FFD700','#DAA520','#CD5C5C','#8470FF']


# p_list = ['food', 'alco','clot','elec','furn','heal','tran','comm',
#           'recr','educ','hote','insu','oth']
# exp_list = ['ex_gold','ex_copper','ex_fluoride','ex_iron','ex_zinc', 	 
#        'ex_cashmere_raw','ex_cashmere_comb','ex_coal','ex_oil']
# im_list = ['im_fuel','im_veh','im_truck','im_elec','im_comm']
# budget_list = ['gov_rev','gov_rev_cur','gov_rev_cur_tax','gov_rev_cur_nontax','gov_rev_cap',
#                'gov_rev_grant','gov_rev_fut','gov_rev_stab','gov_exp','gov_exp_cur','gov_exp_cap','gov_exp_netloan']
# budget_list2 = ['gov_rev_nso','gov_rev_fut_nso','gov_rev_stab_nso','gov_rev_net_nso','gov_rev_tax_nso',	
#                 'gov_rev_corp_nso','gov_rev_ind_nso','gov_rev_ssc_nso','gov_rev_vat_nso','gov_rev_spectax_nso',	
#                 'gov_rev_nontax_nso','gov_exp_nso','gov_exp_cur_nso',	'gov_exp_cur_sal_nso','gov_exp_cur_goods_nso',	
#                 'gov_exp_cur_int_nso','gov_exp_cur_sub_nso','gov_exp_cur_transfer_gov_nso',	
#                 'gov_exp_cur_transfer_oth_nso','gov_exp_cap_nso','gov_exp_netloan_nso']

# trade_list = ['ex','im']

# # decumulate 
# for elem in exp_list:
#     dm[elem] = dm[elem + "_cum"].diff()/1e3
#     dm[elem+ "_vol"] = dm[elem + "_vol" + "_cum"].diff()/1e3
#     dm[elem][dm[elem]<0] = dm[elem + "_cum"][dm[elem]<0]/1e3  
# for elem in im_list:
#     dm[elem] = dm[elem + "_cum"].diff()/1e3
#     dm[elem + "_vol"] = dm[elem + "_vol" + "_cum"].diff()/1e3
#     dm[elem][dm[elem]<0] = dm[elem + "_cum"][dm[elem]<0]/1e3  
# for elem in budget_list:
#     dm[elem] = dm[elem + "_cum"].diff()/1e3
#     dm[elem][dm[elem]<0] = dm[elem + "_cum"][dm[elem]<0]/1e3
# for elem in trade_list:
#     dm[elem] = dm[elem + "_cum"].diff()/1e3
#     dm[elem][dm[elem]<0] = dm[elem + "_cum"][dm[elem]<0]/1e3 


# # inflation
 
# # build CPI level from cpi_mom
# # 15
# for ind in p_list:
#     dm['cpi_' + ind + '_15'] = dm['cpi_' + ind + '_15_mom'].dropna().copy()
#     first = dm['cpi_' + ind + '_15_mom'].dropna().index[0]
#     dm['cpi_' + ind + '_15'][first] = 100
#     ind_first = dm.index.get_loc(first)
#     for i in range(ind_first+1,ind_first+len(dm['cpi_' + ind + '_15_mom'].dropna())):
#             dm['cpi_' + ind + '_15'][i] = dm['cpi_' + ind + '_15'][i-1]*(1+dm['cpi_' + ind + '_15_mom'][i]/100)
# # 20
# for ind in p_list:
#     dm['cpi_' + ind] = dm['cpi_' + ind + '_20_mom'].dropna().copy()
#     first = dm['cpi_' + ind + '_20_mom'].dropna().index[0]
#     dm['cpi_' + ind][first] = 100
#     ind_first = dm.index.get_loc(first)
#     for i in range(ind_first+1,ind_first+len(dm['cpi_' + ind + '_20_mom'].dropna())):
#             dm['cpi_' + ind][i] = dm['cpi_' + ind][i-1]*(1+dm['cpi_' + ind + '_20_mom'][i]/100)

# for ind in p_list:
#     dm['cpi_' + ind] = bmerge(dm['cpi_' + ind + '_15'],dm['cpi_' + ind])

# # yoy from CPI level # yoy cpi by weighted components
# cpi_yoy_tot_comp = pd.DataFrame()
# for ind in p_list:
#     dm['cpi' + ind + '_yoy'] = pct(dm['cpi_' + ind],-12)
#     elem = (dm["cpi_w_" + ind]/100*dm["cpi" + ind + "_yoy"]).dropna()
#     cpi_yoy_tot_comp[ind] = elem

# # mom cpi by weighted components
# cpi_mom_tot_comp=pd.DataFrame()
# for ind in p_list:
#     elem = (dm["cpi_w_" + ind]/100*pct(dm["cpi_" + ind],-1)).dropna()
#     cpi_mom_tot_comp[ind] = elem

# dm["cpi_nonfood_yoy"] = (pct(dm.cpi,-12)-dm.cpi_w_food.shift(12)*pct(dm.cpi_food,-12)/100)/(1-dm.cpi_w_food.shift(12)/100)   
# dm["cpi_nonfood_mom"] = (pct(dm.cpi,-1)-dm.cpi_w_food.shift()*pct(dm.cpi_food,-1)/100)/(1-dm.cpi_w_food.shift()/100)      

# for ind in ['nonfood']:
#     dm['cpi_' + ind] = dm['cpi_' + ind + '_mom'].dropna().copy()
#     first = dm['cpi_' + ind + '_mom'].dropna().index[0]
#     dm['cpi_' + ind][first] = 100
#     ind_first = dm.index.get_loc(first)
#     for i in range(ind_first+1,ind_first+len(dm['cpi_' + ind + '_mom'].dropna())):
#             dm['cpi_' + ind][i] = dm['cpi_' + ind][i-1]*(1+dm['cpi_' + ind + '_mom'][i]/100)

# # Seasonal adjustment
# for ind in p_list:
#     dm['cpi_' + ind + '_sa'] = sa(dm['cpi_' + ind])
#     dm['cpi_' + ind + '_mom_sa'] = pct(dm['cpi_' + ind + '_sa'],-1)

# for ind in ['cpi','cpi_nonfood']:
#        dm[ind + '_sa'] = sa(dm[ind])       
#        dm[ind + '_mom_sa'] = pct(dm[ind + '_sa'],-1)

# cpi_mom_tot_comp_sa=pd.DataFrame()
# for ind in p_list:
#     elem = (dm["cpi_w_" + ind]/100*pct(dm["cpi_" + ind + '_sa'],-1)).dropna()
#     cpi_mom_tot_comp_sa[ind] = elem

# dy['gdp_nom'] = convert(dq['gdp_nom'],'y')

dq['gdp'] = bmerge(bmerge(dq['gdp_05'],dq['gdp_10']), dq['gdp_15'])
dy['gdp'] = convert(dq['gdp'],'y')


gdp_list = ['agr', 'mine', 'manu', 'elec', 'cons', 'trad', 'tran', 'comm', 'serv_oth', 'tax']

for sector in gdp_list:
       dq['gdp_' + sector] = bmerge(bmerge(dq['gdp_' + sector + '_05'],dq['gdp_' + sector + '_10']), dq['gdp_' + sector + '_15'])
       dy['gdp_' + sector] = convert(dq['gdp_' + sector],'y')

### Real GDP growth
    
# gdp_comp_all = dq[['gdp_agr','gdp_mine','gdp_manu','gdp_elec',
#                    'gdp_cons','gdp_trad','gdp_tran','gdp_comm',
#                    'gdp_serv_oth','gdp_tax','gdp']]
# # last one is total, others are components
# gdp_comp_diff_rel_all = gdp_comp_all.diff(periods=4).div(dq.gdp.shift(4), axis=0)*100
# gdp_comp_diff_rel     = gdp_comp_diff_rel_all.iloc[:,:-1]
# gdp_comp_diff_rel_tot = gdp_comp_diff_rel_all.iloc[:,-1]

# gdp_comp_all_y = dy[['gdp_agr','gdp_mine','gdp_manu','gdp_elec',
#                    'gdp_cons','gdp_trad','gdp_tran','gdp_comm',
#                    'gdp_serv_oth','gdp_tax','gdp']]


# # last one is total, others are components
# gdp_comp_diff_rel_all_y = gdp_comp_all_y.diff(periods=1).div(dy.gdp.shift(1), axis=0)*100
# gdp_comp_diff_rel_y     = gdp_comp_diff_rel_all_y.iloc[:,:-1]
# gdp_comp_diff_rel_tot_y = gdp_comp_diff_rel_all_y.iloc[:,-1]


# dy["usd_mnt_last"] = convert(dm["usd_mnt"],'y','last')
# dy["usd_mnt_avg"] = convert(dm["usd_mnt"],'y','average')
# dy["cpi_last"] = convert(dm["cpi"],'y','last')


# dm["l_mnt_usd"] = 100*np.log(dm["usd_mnt"])
# dm["l_mnt_cny"] = dm["l_mnt_usd"] - 100*np.log(dm["usd_mnt"]/dm["cny_mnt"])
# dm["l_mnt_rub"] = dm["l_mnt_usd"] - 100*np.log(dm["usd_mnt"]/dm["rub_mnt"])
# dm["l_mnt_eur"] = dm["l_mnt_usd"] - 100*np.log(dm["usd_mnt"]/dm["eur_mnt"])


# # Money bank

# dm["bs_tot_ass"] = dm[['dc_res','dc_cbb','dc_fa','dc_gov','dc_fi',
#         'dc_pub','dc_corp','dc_ind','dc_oth']].dropna().sum(axis=1)
# dm["bs_tot_liab"] = dm[['dc_ca_mnt','dc_quasimoney','dc_fl','dc_fl_long','dc_gov_depo',
#         'dc_cbloan','dc_ca','dc_oth_net']].dropna().sum(axis=1)  

# # dm["bs_ma_nfa"] = dm.dc_fa-dm.dc_fl-dm.dc_fl_long
# dm["cb_nda"] = dm.cb_mbase-(dm.cb_nfa+dm.cb_ca+dm.cb_oth_net)
# dm["ms_m2_dep_ca_dc"] = dm.ms_m1-dm.ms_cashout

# m_list = ['ms_cic','ms_cashvault','ms_cashout','ms_m1','ms_ca_mnt','ms_dep_oth','ms_dep_mnt',
# 'ms_dep_mnt_ind','ms_dep_mnt_corp','ms_dep_fx','ms_ca_fx','ms_m2','dc_nfa','dc_ndc','dc_ndc_gov',
# 'dc_ndc_gov_cen','dc_ndc_gov_loc','dc_ndc_gov_oth','dc_ndc_oth','dc_ndc_oth_fi','dc_ndc_oth_pub',
# 'dc_ndc_oth_corp','dc_ndc_oth_ind','dc_ndc_oth_oth','dc_ms','dc_quasimoney','dc_imfloan','dc_oth_net_tot',
# 'cb_nfa','cb_fa','cb_dc','cb_gov_net','cb_gov','cb_oth','cb_oth_pub','cb_oth_priv','cb_oth_fi','cb_mbase',
# 'cb_mbase_cashout','cb_mbase_cashvault','cb_mbase_bankdepo','cbb','cb_fl','cb_fl_long','cb_gov_depo','cb_ca',
# 'cb_oth_net','dc_res','dc_cbb','dc_fa','dc_gov','dc_fi','dc_pub','dc_corp','dc_ind','dc_oth','dc_ca_mnt',
# 'dc_qm','dc_fl','dc_fl_long','dc_gov_depo','dc_cbloan','dc_ca','dc_oth_net'] + \
# ['bs_tot_ass','bs_tot_liab','cb_nda','ms_m2_dep_ca_dc']



# for ind in m_list:
#      dq[ind] = convert(dm[ind].copy(),'q',method='average')


# dm['dc_loan_corp'] = dm.dc_loan_norm_corp + dm.dc_loan_overdue_corp + dm.dc_loan_npl_corp
# dm['dc_loan_ind'] = dm.dc_loan_norm_ind + dm.dc_loan_overdue_ind + dm.dc_loan_npl_ind

# bank_list = ['bank_ass_tot','bank_ass_res','bank_ass_res_cash','bank_ass_res_cbdepo_mnt','bank_ass_res_cbdepo_fx',
# 'bank_ass_res_cbdepo_oth','bank_ass_cbb','bank_ass_fa','bank_ass_fa_cash','bank_ass_fa_cur','bank_ass_fa_depo',
# 'bank_ass_fa_forbill','bank_ass_fa_forloan','bank_ass_gov_rec','bank_ass_bill','bank_ass_credit_net',
# 'bank_ass_credit_dom','bank_ass_credit_nfi','bank_ass_credit_norm','bank_ass_credit_norm_mnt',
# 'bank_ass_credit_norm_mnt_pub','bank_ass_credit_norm_mnt_corp','bank_ass_credit_norm_mnt_ind',
# 'bank_ass_credit_norm_mnt_oth','bank_ass_credit_norm_fx','bank_ass_credit_norm_fx_pub',
# 'bank_ass_credit_norm_fx_corp','bank_ass_credit_norm_fx_ind','bank_ass_credit_norm_fx_oth',
# 'bank_ass_credit_ovrd','bank_ass_credit_ovrd_mnt','bank_ass_credit_ovrd_mnt_pub',
# 'bank_ass_credit_ovrd_mnt_corp','bank_ass_credit_ovrd_mnt_ind','bank_ass_credit_ovrd_mnt_oth',
# 'bank_ass_credit_ovrd_fx','bank_ass_credit_ovrd_fx_pub','bank_ass_credit_ovrd_fx_corp',
# 'bank_ass_credit_ovrd_fx_ind','bank_ass_credit_ovrd_fx_oth','bank_ass_credit_npl','bank_ass_credit_npl_mnt',
# 'bank_ass_credit_npl_mnt_pub','bank_ass_credit_npl_mnt_corp','bank_ass_credit_npl_mnt_ind',
# 'bank_ass_credit_npl_mnt_oth','bank_ass_credit_npl_fx','bank_ass_credit_npl_fx_pub',
# 'bank_ass_credit_npl_fx_corp','bank_ass_credit_npl_fx_ind','bank_ass_credit_npl_fx_oth',
# 'bank_ass_credit_fi','bank_ass_credit_norm_fi','bank_ass_credit_norm_mnt_fi',
# 'bank_ass_credit_norm_fx_fi','bank_ass_credit_ovrd_fi','bank_ass_credit_ovrd_mnt_fi',
# 'bank_ass_credit_ovrd_fx_fi','bank_ass_credit_npl_fi','bank_ass_credit_npl_mnt_fi',
# 'bank_ass_credit_npl_fx_fi','bank_ass_credit_prov','bank_ass_oth_fi',
# 'bank_ass_oth_bank','bank_ass_der','bank_ass_estates','bank_ass_properties','bank_liab_tot','bank_liab_cur',
# 'bank_liab_cur_mnt','bank_liab_cur_fx','bank_liab_depo','bank_liab_depo_dem','bank_liab_depo_dem_mnt',
# 'bank_liab_depo_dem_fx','bank_liab_depo_time','bank_liab_depo_time_mnt','bank_liab_depo_time_fx','bank_liab_fi',
# 'bank_liab_oth_curdepo','bank_liab_mmarket','bank_liab_spec_depo','bank_liab_bank','bank_liab_cbank','bank_liab_fl',
# 'bank_liab_gov','bank_liab_der','bank_liab_oth_liab','bank_cap']

# list_type = ['norm','ovrd','npl']
# list_sector = ['ind','corp','pub','fi','oth']

# for type in list_type:
#      for sector in list_sector:
#        dm['bank_ass_credit_' + type + '_' + sector] = dm['bank_ass_credit_' + type + '_mnt_' + sector] + dm['bank_ass_credit_' + type + '_fx_' + sector]
#        bank_list = bank_list + ['bank_ass_credit_' + type + '_' + sector]

# for sector in list_sector:
#        dm['bank_ass_credit_' + sector] = dm['bank_ass_credit_norm_' + sector] + \
#               dm['bank_ass_credit_ovrd_' + sector] + dm['bank_ass_credit_npl_' + sector]
#        bank_list = bank_list + ['bank_ass_credit_' + sector]

# for type in list_type:
#        dm['bank_ass_credit_' + type] = dm['bank_ass_credit_' + type + '_pub'] + \
#               dm['bank_ass_credit_' + type + '_corp'] + dm['bank_ass_credit_' + type + '_ind'] + dm['bank_ass_credit_' + type + '_oth']
#        bank_list = bank_list + ['bank_ass_credit_' + type]

# for currency in ['mnt','fx']:
#        dm['bank_ass_credit_' + currency] = dm['bank_ass_credit_norm_' + currency] + \
#              dm['bank_ass_credit_ovrd_' + currency] + dm['bank_ass_credit_npl_' + currency] 
#        dm['bank_ass_credit_' + currency + '_corp'] = dm['bank_ass_credit_norm_' + currency  + '_corp'] + \
#              dm['bank_ass_credit_ovrd_' + currency  + '_corp'] + dm['bank_ass_credit_npl_' + currency  + '_corp'] 
#        dm['bank_ass_credit_' + currency + '_ind'] = dm['bank_ass_credit_norm_' + currency  + '_ind'] + \
#              dm['bank_ass_credit_ovrd_' + currency  + '_ind'] + dm['bank_ass_credit_npl_' + currency  + '_ind'] 
#        bank_list = bank_list + ['bank_ass_credit_' + currency]


# for ind in bank_list:
#      dq[ind] = convert(dm[ind].copy(),'q',method='average')


# dm['gov_rev_eq'] = dm['gov_rev'] - dm['gov_rev_fut']- dm['gov_rev_stab']
# dm['gov_exp_cur_subtran_nso'] = dm['gov_exp_cur_sub_nso']+dm['gov_exp_cur_transfer_gov_nso']+dm['gov_exp_cur_transfer_oth_nso']

# budget_list = budget_list + ['gov_rev_eq','gov_exp_cur_subtran_nso']

# for ind in budget_list + budget_list2:
#      dq[ind] = convert(dm[ind].copy(),'q')
#      dy[ind] = convert(dq[ind].copy(),'y')

# dq['gdp_nom_y'] = dq['gdp_nom'].rolling(window=4, min_periods=1).sum()


# bop_list = ['bop_ca','bop_ca_gs','bop_ca_gs_cre','bop_ca_gs_deb','bop_ca_goods','bop_ca_goods_ex',
# 'bop_ca_goods_im','bop_ca_serv','bop_ca_serv_cre','bop_ca_serv_deb','bop_ca_prim','bop_ca_prim_cre',
# 'bop_ca_prim_deb','bop_ca_sec','bop_ca_sec_cre','bop_ca_sec_deb','bop_capa','bop_fa','bop_fa_di',
# 'bop_fa_pi','bop_fa_der','bop_fa_oth','bop_eo','bop']

# for ind in bop_list:
#        dq[ind] = convert(dm[ind],'q') 


# dq['bop_fa_di'].loc[dq['bop_fa_di']>2000] = 1500
# dq['bop_fa_oth'].loc[dq['bop_fa_oth']<-2000] = -1500


# # trade to quarterly
# for ind in exp_list + im_list:
#      dq[ind] = convert(dm[ind],'q')
#      dq[ind + '_vol'] = convert(dm[ind + '_vol'],'q')

# for ind in trade_list:
#      dq[ind] = convert(dm[ind].copy(),'q')

## 
tmp = dm.usd_mnt.copy()
dq['d_usd_mnt'] = pct(convert(tmp,'q'),-4)
tmp = dm.fx_reserve.copy()
dq['fx_reserve'] = convert(tmp,'q')

# Save the data file
macro_data = [dd,dm,dq,dy]
pickle.dump(macro_data, file = open("./data/macro_data.pickle", "wb"))


# Create 2x2 sub plots
gs21 = gridspec.GridSpec(2, 1)
gs22 = gridspec.GridSpec(2, 2)
gs33 = gridspec.GridSpec(3, 3)
gs43 = gridspec.GridSpec(4, 3)
gs44 = gridspec.GridSpec(4, 4)


firstM = "05M01"
firstM_bop = "09M01"
firstQ = "05Q1"
firstQ_bop = "09Q1"
firstY = "05Y"
lastY = "22Y"

### Reporting section

plot_section("Macroeconomic Data Report")





# plt.figure()
# plt.subplot(gs21[0])
# doPlot(line1 = dq.bop_ca/100,
#        line2=-dq.bop_fa/100,
#        line3=dq.bop/100,
#        line4=dq['d_usd_mnt'],
#        title = 'BoP (100m USD) and USDMNT rate, last: ' + get(dq.bop_ca,'last'),
#        leg   = ['CA','FA','BoP','FX 1Y %'],
#        rng   = [firstQ])
# plt.subplot(gs21[1])
# doPlot(line1=dq.bop_ca/100,
#        line2=dq['d_usd_mnt'],
#        title = 'Current account (100m USD) and USDMNT rate, last: ' + get(dq.ex,'last'),
#        leg   = ['CA','FX 1Y %'],
#        rng   = [firstQ])
# plt.subplots_adjust(hspace=0.5)
# plt.savefig(fig_dir + 'gdp1.png')

# plt.figure()
# plt.subplot(gs21[0])
# doPlot(line1=dq.bop/100,
#        line2=dq['fx_reserve'].diff(1)/100,
#        line3=dq['d_usd_mnt'],
#        title = 'BoP (100m USD) and USDMNT rate, last: ' + get(dq.bop_ca,'last'),
#        leg   = ['BoP','BoM reserve changes','FX 1Y %'],
#        rng   = [firstQ])
# plt.subplot(gs21[1])
# doPlot(line1 = 10*dq.ex,
#        line2=10*dq.im,
#        line3=dq.bop_ca/100,
#        line4=dq['d_usd_mnt'],
#        title = 'Foreign trade (100m USD) and USDMNT rate, last: ' + get(dq.ex,'last'),
#        leg   = ['Ex','Im','CA','FX 1Y %'],
#        rng   = [firstQ])
# plt.subplots_adjust(hspace=0.5)
# plt.savefig(fig_dir + 'gdp1.png')



# ### Overview
# plot_section("Short Overview")
# plt.figure()
# plt.subplot(gs22[0,0])
# doPlot(line1 = pct(dq.gdp,-4),
#        title = 'Real GDP growth (%, YoY), last: ' + get(dq.gdp,'last'),
#        rng = [firstQ])
# plt.subplot(gs22[0,1])
# doPlot(line1 = pct(dq.gdp_nom,-4),
#        title = 'Nominal GDP growth (%, YoY), last: ' + get(dq.gdp_nom,'last'),
#        rng = [firstQ])
# plt.subplot(gs22[1,0])
# doPlot(line1 = dm["usd_mnt"],
#        title = 'MNT/USD Exchange rate, last: ' + get(dm["usd_mnt"],'last'),
#        rng   = [firstM])
# plt.xticks(fontsize=5)
# plt.subplot(gs22[1,1])
# doPlot(line1 = pct(dm["cpi"],-12),
#        title = 'Inflation (%, YoY), last: ' + get(dm["cpi"],'last'),
#        rng   = [firstM])
# plt.xticks(fontsize=5)
# plt.subplots_adjust(hspace=0.5)
# plt.savefig(fig_dir + 'short1.png')

# plt.figure()
# plt.subplot(gs22[0,0])
# doPlot(line1 = pct(dy.gdp,-1),
#        title = 'Real GDP growth (%, yearly), last: ' + lastY,
#        rng = [firstY,lastY])
# plt.subplot(gs22[0,1])
# doPlot(line1 = pct(dy.gdp_nom,-1),
#        title = 'Nominal GDP growth (%, yearly), last: ' + lastY,
#        rng = [firstY,lastY])
# plt.subplot(gs22[1,0])
# doPlot(line1 = dy["usd_mnt_avg"] ,
#        line2 = dy["usd_mnt_last"] ,
#        leg   = ['Mean','Last'],
#        title = 'MNT/USD Exchange rate, last: ' + lastY,
#        rng   = [firstY,lastY])
# plt.xticks(fontsize=5)
# plt.subplot(gs22[1,1])
# doPlot(line1 = pct(dy["cpi_last"],-1),
#        title = 'Inflation (%, yearly), last: ' + lastY,
#        rng   = [firstY,lastY])
# plt.xticks(fontsize=5)
# plt.subplots_adjust(hspace=0.5)
# plt.savefig(fig_dir + 'short2.png')

# tmp = dm['cpi'].copy()
# plt.figure()
# plt.subplot(gs22[0,0])
# doPlot(line1 = pct(dm['bank_ass_credit_nfi'],-12),
#        line2 = pct(dm['ms_m2'],-12),
#        title = 'Credit and money supply (% YoY), last: ' + get(dm['ms_m2'],'last'),
#        leg   = ['Banking sector credit','M2'],
#        rng   = [firstM])
# plt.subplot(gs22[0,1])
# doPlot(line1 = pct(dm['cpi'],-12),
#        line2 = pct(dm['ms_m2'],-12),
#        title = 'Inflation and money supply (% YoY), last: ' + get(dm['ms_m2'],'last'),
#        leg   = ['Inflation','M2'],
#        rng   = [firstM])
# plt.subplot(gs22[1,0])
# doPlot(line1 = pct(dm['usd_mnt'],-12),
#        line2 = pct(dm['cpi'],-12),
#        title = 'FX rates and inflation (% YoY), last: ' + get(dm['ms_m2'],'last'),
#        leg   = ['USD/MNT','Inflation'],
#        rng   = [firstM])
# plt.subplot(gs22[1,1])
# doPlot(line1 = pct(convert(tmp,'q'),-4),
#        line2 = (dq['gov_rev_eq'] - dq['gov_exp'])/1e2,
#        line3 = (- dq['gov_exp'])/1e2,
#        title = 'Inflation (%, yearly) and Budget, last: ' + get(dq['ex'],'last'),
#        leg   = ['Inflation','Budget balance (100 bn MNT)', 'Budget expenditure (100 bn MNT)'],
#        rng   = [firstQ])

# # doPlot(line1 = pct(dm['cpi'],-12),
# #        line2 = dm['rate_pol'],
# #        title = 'Inflation (%, yearly) and interest rates, last: ' + get(dm['ms_m2'],'last'),
# #        leg   = ['Inflation','BoM policy rate'],
# #        rng   = [firstM])
# plt.subplots_adjust(hspace=0.5)
# plt.savefig(fig_dir + 'short3.png')

# ### Real economy
# plot_section("Real economy")


# plt.figure()
# plt.subplot(gs21[0])
# doPlot(line1 = gdp_comp_diff_rel_tot,
#        bar   = gdp_comp_diff_rel,
#        title = 'Real GDP growth (%, YoY), last: ' + get(gdp_comp_diff_rel,'last'),
#        leg   = ['_nolegend_','Agr','Min','Manu','Elec','Cons','Trad','Trans','Comm','Oth. Serv.','Net Tax'],
#        rng   = [firstQ])
# plt.subplot(gs21[1])
# doPlot(line1 = gdp_comp_diff_rel_tot_y,
#        bar   = gdp_comp_diff_rel_y,
#        title = 'Real GDP growth (%, YoY), last: ' + lastY,
#        leg   = ['_nolegend_','Agr','Min','Manu','Elec','Cons','Trad','Trans','Comm','Oth. Serv.','Net Tax'],
#        rng   = [firstY,lastY])
# plt.subplots_adjust(hspace=0.5)
# plt.savefig(fig_dir + 'gdp1.png')

# #### Real GDP decomposition
# plt.figure()
# plt.subplot(gs21[1])
# doPlot(bar   = dy[['gdp_agr', 'gdp_mine', 'gdp_manu', 'gdp_elec', 
#                     'gdp_cons', 'gdp_trad', 'gdp_tran', 'gdp_comm', 
#                     'gdp_serv_oth', 'gdp_tax']].div(dy['gdp'],axis=0),
#        title = 'Real GDP decomposition (shares, production approach), last: ' + get(dy['gdp'],'last'),
#        leg   = ['Agr','Min','Manu','Elec','Cons','Trad','Trans','Comm','Oth. Serv.','Net Tax'],
#        rng   = [firstY])
# plt.subplot(gs21[0])
# ax=plt.gca()
# first = '05Y'
# color = 'tab:red'
# ax.set_ylabel('Nominal GDP (tn MNT)', color=color,fontsize=7)
# ax.plot(dy.gdp_nom[firstY:lastY]/1e6,color=color)
# ax.tick_params(axis='y', labelcolor=color, labelsize=7)
# #ax = plt.sca(ax1)
# #ax=plt.gca()
# ax.grid(which = 'major', axis='y',linestyle='-.', color='#c5d7ed',linewidth=0.1)
# ax.grid(which = 'major', axis='x',linestyle='-.', color='#c5d7ed',linewidth=0.1)
# title = 'Nominal GDP, last: ' + lastY
# ax.set_title(title,pad=5,size=5)
# ax2 = ax.twinx()  # instantiate a second axes that shares the same x-axis
# color = 'tab:blue'
# ax2.set_ylabel('Nominal GDP (bn USD)', color=color,rotation=90,fontsize=7)
# ax2.plot(dy.gdp_nom_usd[firstY:lastY],color=color)
# ax2.tick_params(axis='y', labelcolor=color, labelsize=5)
# ax = plt.sca(ax)
# ax=plt.gca()
# start, end = ax.get_xlim()
# length = dy.gdp_nom[firstY:lastY].shape[0]
# n_xticks = []
# n_xticklabels = []
# for i in range(length):
#     if np.mod(i+1,2)==0:
#         n_xticks.append(i)
#         n_xticklabels.append(dy.gdp_nom[firstY:lastY].index[i])
# ax.set_xticks(n_xticks)
# ax.set_xticklabels(n_xticklabels, fontsize=7,rotation=0)
# ax.yaxis.set_tick_params(labelsize=7,rotation=0) 
# width=.5
# plt.xlim([-width, len(dy.gdp_nom[firstY:lastY])-width])
# plt.subplots_adjust(hspace=0.5)
# plt.savefig(fig_dir + 'gdp2.png')



plt.figure()
plt.subplot(gs22[0,0])
doPlot(line1 = pct(dq['gdp_agr'],-4),
       line2 = pct(dq['gdp'],-4),
       title = 'Real GDP growth (%, YoY), last: ' + get(dq['gdp_agr'],'last'),
       leg   = ['Agr','Total GDP'],
       rng   = [firstQ])
plt.subplot(gs22[0,1])
doPlot(line1 = pct(dq['gdp_trad'],-4),
       line2 = pct(dq['gdp_serv_oth'],-4),
       line3 = pct(dq['gdp'],-4),
       title = 'Real GDP growth (%, YoY), last: ' + get(dq['gdp_agr'],'last'),
       leg   = ['Trad','Oth','Total GDP'],
       rng   = [firstQ])
plt.subplot(gs22[1,0])
doPlot(line1 = pct(dq['gdp_manu'],-4),
       line2 = pct(dq['gdp_cons'],-4),
       line3 = pct(dq['gdp_elec'],-4),
       line4 = pct(dq['gdp_comm'],-4),
       line5 = pct(dq['gdp'],-4),
       title = 'Real GDP growth (%, YoY), last: ' + get(dq['gdp_agr'],'last'),
       leg   = ['Manu','Cons','Elec','Comm','Total GDP'],
       rng   = [firstQ])
plt.subplot(gs22[1,1])
doPlot(line1 = pct(dq['gdp_mine'],-4),
       line2 = pct(dq['gdp_tran'],-4),
       line3 = pct(dq['gdp_tax'],-4),
       line4 = pct(dq['gdp'],-4),
       title = 'Real GDP growth (%, YoY), last: ' + get(dq['gdp_agr'],'last'),
       leg   = ['Mine','Tran','Tax','Total GDP'],
       rng   = [firstQ])
plt.subplots_adjust(hspace=0.5)

plt.figure()
plt.subplot(gs43[0,0])
doPlot(line1 = pct(dq['gdp_agr'],-4),
       line2 = pct(dq['gdp'],-4),
       title = 'Real GDP growth (%, YoY), last: ' + get(dq['gdp_agr'],'last'),
       leg   = ['Agr','Total GDP'],
       rng   = [firstQ])
plt.subplot(gs43[0,1])
doPlot(line1 = pct(dq['gdp_mine'],-4),
       line2 = pct(dq['gdp'],-4),
       title = 'Real GDP growth (%, YoY), last: ' + get(dq['gdp_agr'],'last'),
       leg   = ['Mine','Total GDP'],
       rng   = [firstQ])
plt.subplot(gs43[0,2])
doPlot(line1 = pct(dq['gdp_manu'],-4),
       line2 = pct(dq['gdp'],-4),
       title = 'Real GDP growth (%, YoY), last: ' + get(dq['gdp_agr'],'last'),
       leg   = ['Manu','Total GDP'],
       rng   = [firstQ])
plt.subplot(gs43[1,0])
doPlot(line1 = pct(dq['gdp_elec'],-4),
       line2 = pct(dq['gdp'],-4),
       title = 'Real GDP growth (%, YoY), last: ' + get(dq['gdp_agr'],'last'),
       leg   = ['Elec','Total GDP'],
       rng   = [firstQ])
plt.subplot(gs43[1,1])
doPlot(line1 = pct(dq['gdp_cons'],-4),
       line2 = pct(dq['gdp'],-4),
       title = 'Real GDP growth (%, YoY), last: ' + get(dq['gdp_agr'],'last'),
       leg   = ['Cons','Total GDP'],
       rng   = [firstQ])
plt.subplot(gs43[1,2])
doPlot(line1 = pct(dq['gdp_trad'],-4),
       line2 = pct(dq['gdp'],-4),
       title = 'Real GDP growth (%, YoY), last: ' + get(dq['gdp_agr'],'last'),
       leg   = ['Trad','Total GDP'],
       rng   = [firstQ])
plt.subplot(gs43[2,0])
doPlot(line1 = pct(dq['gdp_tran'],-4),
       line2 = pct(dq['gdp'],-4),
       title = 'Real GDP growth (%, YoY), last: ' + get(dq['gdp_agr'],'last'),
       leg   = ['Tran','Total GDP'],
       rng   = [firstQ])
plt.subplot(gs43[2,1])
doPlot(line1 = pct(dq['gdp_comm'],-4),
       line2 = pct(dq['gdp'],-4),
       title = 'Real GDP growth (%, YoY), last: ' + get(dq['gdp_agr'],'last'),
       leg   = ['Comm','Total GDP'],
       rng   = [firstQ])
plt.subplot(gs43[2,2])
doPlot(line1 = pct(dq['gdp_serv_oth'],-4),
       line2 = pct(dq['gdp'],-4),
       title = 'Real GDP growth (%, YoY), last: ' + get(dq['gdp_agr'],'last'),
       leg   = ['Oth serv','Total GDP'],
       rng   = [firstQ])
plt.subplot(gs43[3,0])
doPlot(line1 = pct(dq['gdp_tax'],-4),
       line2 = pct(dq['gdp'],-4),
       title = 'Real GDP growth (%, YoY), last: ' + get(dq['gdp_agr'],'last'),
       leg   = ['Net tax','Total GDP'],
       rng   = [firstQ])
plt.subplots_adjust(hspace=0.8)




# ['gdp_agr', 'gdp_mine', 'gdp_manu', 'gdp_elec', 
#                     'gdp_cons', 'gdp_trad', 'gdp_tran', 'gdp_comm', 
#                     'gdp_serv_oth', 'gdp_tax']

# plot_section("Inflation and Prices")

# ### Inflation
  
# plt.figure()
# plt.subplot(gs21[0])
# doPlot(line1 = pct(dm.cpi,-12),
#        bar   = cpi_yoy_tot_comp,
#        title = 'Inflation (%, YoY), last: ' + get(dm["cpi"],'last'),
#        leg   = ['_nolegend_','Food','Alc','Cloth','Fuel','Furn','Heal','Trans','Comm','Recre.','Edu','Restau','Misc'],
#        rng   = ['11M01',get(dm["cpi"],'last')])
# plt.subplot(gs21[1])
# doPlot(line1 = pct(dm.cpi,-1),
#        bar   = cpi_mom_tot_comp,
#        title = 'Inflation (%, MoM), last: ' + get(dm["cpi"],'last'),
#        leg   = ['_nolegend_','Food','Alc','Cloth','Fuel','Furn','Heal','Trans','Comm','Recre.','Edu','Restau','Misc'],
#        rng   = ['11M01',get(dm["cpi"],'last')])
# # doPlot(bar   = cpi_mom_tot_comp,
# #        title = 'Inflation (%, MoM), last: ' + get(dm["cpi"],'last'),
# #        leg   = ['Food','Alc','Cloth','Fuel','Furn','Heal','Trans','Comm','Recre.','Edu','Restau','Misc'],
# #        rng   = ['11M01',get(dm["cpi"],'last')])
# plt.subplots_adjust(hspace=0.5)
# plt.savefig(fig_dir + 'inf1.png')

# plt.figure()
# plt.subplot(gs21[0])
# doPlot(line1 = pct(dm.cpi,-12),
#        line2 = pct(dm.cpi_food,-12),
#        line3 = dm["cpi_nonfood_yoy"],
#        title = 'Inflation (%, YoY), last: ' + get(dm.cpi,'last'),
#        leg   = ['Total','Food','Non-food'],
#        rng   = ['11M01'])
# plt.subplot(gs21[1])
# doPlot(line1 = pct(dm.cpi,-1),
#        line2 = pct(dm.cpi_food,-1),
#        line3 = pct(dm["cpi_nonfood"],-1),
#        title = 'Inflation (%, MoM, su), last: ' + get(dm.cpi,'last'),
#        leg   = ['Total','Food','Non-food'],
#        rng   = ['11M01'])
# plt.subplots_adjust(hspace=0.5)
# plt.savefig(fig_dir + 'inf2.png')

# plt.figure()
# plt.subplot(gs21[0])
# doPlot(line1 = pct(dm.cpi_sa,-1),
#        bar   = cpi_mom_tot_comp_sa,
#        title = 'Inflation (%, MoM, sa), last: ' + get(dm["cpi"],'last'),
#        leg   = ['_nolegend_','Food','Alc','Cloth','Fuel','Furn','Heal','Trans','Comm','Recre.','Edu','Restau','Misc'],
#        rng   = ['11M01',get(dm["cpi"],'last')])
# plt.subplot(gs21[1])
# doPlot(line1 = pct(dm.cpi_sa,-1),
#        line2 = pct(dm.cpi_food_sa,-1),
#        line3 = pct(dm["cpi_nonfood_sa"],-1),
#        title = 'Inflation (%, MoM, sa), last: ' + get(dm.cpi,'last'),
#        leg   = ['Total','Food','Non-food'],
#        rng   = ['11M01'])
# plt.subplots_adjust(hspace=0.5)
# plt.savefig(fig_dir + 'inf3.png')

# dm['l_rp_nff'] = 100*np.log(dm['cpi_nonfood']/dm['cpi_food'])
# dm['l_rp_nf']  = 100*np.log(dm['cpi_nonfood']/dm['cpi'])
# dm['l_rp_f']   = 100*np.log(dm['cpi_food']/dm['cpi'])
# dm['l_rp_nff'] = dm['l_rp_nff'] - dm['l_rp_nff']['11M01']
# dm['l_rp_nf'] = dm['l_rp_nf'] - dm['l_rp_nf']['11M01']
# dm['l_rp_f'] = dm['l_rp_f'] - dm['l_rp_f']['11M01']

# dm['l_cpi_nf'] = 100*np.log(dm['cpi_nonfood'])
# dm['l_cpi_f']  = 100*np.log(dm['cpi_food'])
# dm['l_cpi']   = 100*np.log(dm['cpi'])
# dm['l_cpi_nf'] = dm['l_cpi_nf'] - dm['l_cpi_nf']['11M01']
# dm['l_cpi_f'] = dm['l_cpi_f'] - dm['l_cpi_f']['11M01']
# dm['l_cpi'] = dm['l_cpi'] - dm['l_cpi']['11M01']


# plt.figure()
# plt.subplot(gs21[0])
# doPlot(line1 = dm['l_rp_nff'],
#        line2 = dm['l_rp_nf'],
#        line3 = dm['l_rp_f'],
#        title = 'Relative prices (100*log, 11M01=0), last: ' + get(dm["cpi"],'last'),
#        leg   = ['Nonfood/Food','Food/CPI','Nonfood/CPI'],
#        rng   = [firstM])
# plt.subplot(gs21[1])
# doPlot(line1 = dm['l_cpi_nf'],
#        line2 = dm['l_cpi_f'],
#        line3 = dm['l_cpi'],
#        title = 'CPI (100*log, 11M01=0), last: ' + get(dm["cpi"],'last'),
#        leg   = ['Nonfood','Food','CPI'],
#        rng   = [firstM])
# plt.subplots_adjust(hspace=0.5)
# plt.savefig(fig_dir + 'inf4.png')

# # plt.figure()
# # plt.subplot(gs22[0,0])
# # doPlot(line1 = dm.coal_csx,
# #        title = 'Coal price (USD per metric ton, futures generic), last: ' + get(dm.coal_csx,'last'),
# #        rng   = ['05M01'])
# # plt.xticks(fontsize=5)
# # plt.subplot(gs22[0,1])
# # doPlot(line1 = dm.copper_lon,
# #        title = 'Copper price (USD per metric ton, spot), last: ' + get(dm.copper_lon,'last'),
# #        rng   = ['05M01'])
# # plt.xticks(fontsize=5)
# # plt.subplot(gs22[1,0])
# # doPlot(line1 = dm.gold,
# #        title = 'Gold price (USD per troy ounce, spot), last: ' + get(dm.gold,'last'),
# #        rng   = ['05M01'])
# # plt.xticks(fontsize=5)
# # plt.subplot(gs22[1,1])
# # doPlot(line1 = dm.iron,
# #        title = 'Iron ore price (USD per tonne), last: ' + get(dm.iron,'last'),
# #        rng   = ['05M01'])
# # plt.xticks(fontsize=5)
# # plt.subplots_adjust(hspace=0.5)

# # dm["l_cpi_food_usd"] = 100*np.log(dm["cpi_food_su"]/dm["mnt_usd"])
# # dm["l_food"] = 100*np.log(dm["food"])

# # plt.figure()
# # plt.subplot(gs22[0,0])
# # doPlot(line1 = dm.oil,
# #        title = 'Oil price (USD per barrel, Brent), last: ' + get(dm.oil,'last'),
# #        rng   = ['05M01'])
# # plt.xticks(fontsize=5)
# # plt.subplot(gs22[0,1])
# # doPlot(line1 = dm["l_food"]-dm["l_food"].loc["10M01"]+100,
# #        line2 = dm["l_cpi_food_usd"]-dm["l_cpi_food_usd"].loc["10M01"]+100,
# #        title = 'Food price index (100*log, 10M01=100), last: ' + get(dm.food,'last'),
# #        leg   = ['FAO','FOOD CPI (in USD)'],
# #        rng   = ['05M01'])
# # plt.xticks(fontsize=5)
# # plt.subplot(gs22[1,0])
# # doPlot(line1 = dm.meat,
# #        title = 'FAO meat price index, last: ' + get(dm.meat,'last'),
# #        rng   = ['05M01'])
# # plt.xticks(fontsize=5)
# # plt.subplot(gs22[1,1])
# # doPlot(line1 = dm.cereals,
# #        title = 'FAO cereals price index, last: ' + get(dm.cereals,'last'),
# #        rng   = ['05M01'])
# # plt.xticks(fontsize=5)
# # plt.subplots_adjust(hspace=0.5)

# plot_section("Exchange rate")

# ### Exchange rates

# plt.figure()
# plt.subplot(gs22[0,0])
# doPlot(line1 = dm["usd_mnt"],
#        title = 'MNT per USD, last: ' + get(dm["usd_mnt"],'last'),
#        rng   = [firstM])
# plt.subplot(gs22[0,1])
# doPlot(line1 = dm["cny_mnt"],
#        title = 'MNT per CNY, last: ' + get(dm["cny_mnt"],'last'),
#        rng   = [firstM])
# plt.subplot(gs22[1,0])
# doPlot(line1 = dm["rub_mnt"],
#        title = 'MNT per RUB, last: ' + get(dm["rub_mnt"],'last'),
#        rng   = [firstM])
# plt.subplot(gs22[1,1])
# doPlot(line1 = dm["eur_mnt"],
#        title = 'MNT per EUR, last: ' + get(dm["eur_mnt"],'last'),
#        rng   = [firstM])
# plt.subplots_adjust(hspace=0.5)
# plt.savefig(fig_dir + 'fx1.png')

# plt.figure()
# plt.subplot(gs21[0])
# doPlot(line1 = dm["reer"],
#        title = 'Real Effective Exchange Rate (depreciation down, 10M01=100, Source: BoM), last: ' + get(dm["reer"],'last'),
#        #leg   = ['_nolegend_','Food','Alc','Cloth','Fuel','Furn','Heal','Trans','Comm','Recre.','Edu','Restau','Misc'],
#        rng   = [firstM])
# plt.subplot(gs21[1])
# doPlot(line1 = (dm["l_mnt_usd"] - dm["l_mnt_usd"].loc[firstM] + 100),
#        line2 = (dm["l_mnt_cny"] - dm["l_mnt_cny"].loc[firstM] + 100),
#        line3 = (dm["l_mnt_rub"] - dm["l_mnt_rub"].loc[firstM] + 100),
#        line4 = (dm["l_mnt_eur"] - dm["l_mnt_eur"].loc[firstM] + 100),
#        title = 'Nominal Exchange Rates (' + firstM + '=100, 100*log), last: ' + get(dm["l_mnt_usd"],'last'),
#        leg   = ['MNT per USD', 'MNT per CNY', 'MNT per RUB', 'MNT per EUR'],
#        rng   = [firstM])
# plt.subplots_adjust(hspace=0.5)
# plt.savefig(fig_dir + 'fx2.png')

# plot_section("Balance of Payments")
# # Balance of Payment

# ###BOP

# plt.figure()
# plt.subplot(gs21[0])
# doPlot(bar   = dq[['bop_ca','bop_capa','bop_fa','bop_eo','bop']]*[1,1,-1,1,-1],
#        title = 'Balance of Payments (mln USD), last: ' + get(dq['bop_ca'],'last'),
#        leg   = ['Current','Capital','Financial','Errors & Omissions','Reserves'],
#        rng   = [firstQ_bop])
# plt.subplots_adjust(hspace=0.5)
# plt.savefig(fig_dir + 'bop1.png')

# # CA

# plt.figure()
# plt.subplot(gs21[0])
# doPlot(line1 = dq['bop_ca'],
#        bar   = dq[['bop_ca_gs','bop_ca_prim','bop_ca_sec']],
#        title = 'Current account (mln USD), last: ' + get(dq['bop_ca_gs'],'last'),
#        leg   = ['_nolegend_','Goods and Services','Primary Income','Secondary Income'],
#        rng   = [firstQ_bop])
# plt.subplot(gs21[1])
# doPlot(line1 = dq['bop_fa']*-1,
#        bar   = dq[['bop_fa_di','bop_fa_pi','bop_fa_der','bop_fa_oth']]*[-1,-1,-1,-1],
#        title = 'Financial account (mln USD), last: ' + get(dq['bop_fa'],'last'),
#        leg   = ['_nolegend_','Direct','Portfolio','Derivative','Other'],
#        rng   = [firstQ_bop])
# plt.subplots_adjust(hspace=0.5)
# plt.savefig(fig_dir + 'bop2.png')

# # CA details from BoP

# plt.figure()
# plt.subplot(gs22[0,0])
# doPlot(line1 = dq['bop_ca_gs'],
#        bar   = dq[['bop_ca_gs_cre','bop_ca_gs_deb']]*[1,-1],
#        title = 'Trade balance (mln USD), last: ' + get(dq['bop_ca_gs'],'last'),
#        leg   = ['_nolegend_','Export','Import'],
#        rng   = [firstQ_bop])
# plt.subplot(gs22[0,1])
# doPlot(line1 = dq['bop_ca_prim'],
#        bar   = dq[['bop_ca_prim_cre','bop_ca_prim_deb']]*[1,-1],
#        title = 'Primary Income Balance (mln USD), last: ' + get(dq['bop_ca_prim'],'last'),
#        leg   = ['_nolegend_','Credit','Debit'],
#        rng   = [firstQ_bop])
# plt.subplot(gs22[1,0])
# doPlot(line1 = dq['bop_ca_sec'],
#        bar   = dq[['bop_ca_sec_cre','bop_ca_sec_deb']]*[1,-1],
#        title = 'Secondary Income Balance (mln USD), last: ' + get(dq['bop_ca_sec'],'last'),
#        leg   = ['_nolegend_','Credit','Debit'],
#        rng   = [firstQ_bop])
# plt.subplots_adjust(hspace=0.5)
# plt.savefig(fig_dir + 'bop3.png')

# # Foreign trade

# dq["ex_rest"] = dq.ex*1e3-(dq.ex_gold+dq.ex_copper+
#                       dq.ex_cashmere_raw+dq.ex_cashmere_comb+dq.ex_coal+dq.ex_oil)
# dq['ex_cashmere'] = dq.ex_cashmere_raw+dq.ex_cashmere_comb
# dq['ex_cashmere_vol'] = dq.ex_cashmere_raw_vol+dq.ex_cashmere_comb_vol
# dq["im_rest"] = dq.im*1e3-(dq.im_fuel+dq.im_veh+dq.im_truck+
#                   dq.im_elec+dq.im_comm)

# plt.figure()
# plt.subplot(gs21[0])
# doPlot(line1 = dq['ex'],
#        bar   = dq[['ex_coal','ex_copper','ex_gold','ex_oil','ex_cashmere','ex_rest']]/1e3,
#        title = 'Exports (bn USD), last: ' + get(dq['ex'],'last'),
#        leg   = ['_nolegend_','Coal','Copper','Gold','Oil','Cashmere','Rest'],
#        rng   = [firstQ])
# plt.subplot(gs21[1])
# doPlot(line1 = dq['im'],
#        bar   = dq[['im_fuel','im_veh','im_truck','im_elec','im_comm','im_rest']]/1e3,
#        title = 'Imports (bn USD), last: ' + get(dq['im'],'last'),
#        leg   = ['_nolegend_','Fuel','Vehicle','Truck','Elec.','Comm.','Rest'],
#        rng   = [firstQ])
# plt.subplots_adjust(hspace=0.5)
# plt.savefig(fig_dir + 'trade1.png')

# # plt.figure()
# # plt.subplot(gs21[0])
# # doPlot(line1 = pct(dq['ex'],-12),
# #        line2 = pct(dq['ex_coal'],-12),
# #        line3 = pct(dq['ex_copper'],-12),
# #        line4 = pct(dq['ex_gold'],-12),
# #        line5 = pct(dq['ex_oil'],-12),
# #        line6 = pct(dq['ex_cashmere'],-12),
# #        title = 'Growth of value of main exports (%, YoY), last: ' + get(dq['ex'],'last'),
# #        leg   = ['Total','Coal','Copper','Gold','Oil','Cashmere'],
# #        rng   = [firstQ_bop])
# # plt.subplot(gs21[1])
# # doPlot(line1 = pct(dq['ex_coal_vol'],-12),
# #        line2 = pct(dq['ex_copper_vol'],-12),
# #        line3 = pct(dq['ex_gold_vol'],-12),
# #        line4 = pct(dq['ex_oil_vol'],-12),
# #        line5 = pct(dq['ex_cashmere_vol'],-12),
# #        title = 'Growth of volume main exports (%, YoY), last: ' + get(dq['ex'],'last'),
# #        leg   = ['Coal','Copper','Gold','Oil','Cashmere'],
# #        rng   = [firstQ_bop])
# # plt.subplots_adjust(hspace=0.5)


# ### International reserves
# dm['im_ma'] = dm['im'].rolling(window=12, min_periods=1).mean()
# color = 'tab:red'
# first = firstM #'17M01'
# total = dm.fx_reserve.loc[first:]/1e3
# title = 'BoM FX Reserves, last: ' + get(total,'last')
# fig, ax1 = plt.subplots()
# ax1.set_ylabel('bn USD', color=color)
# ax1.plot(total,color=color)
# ax1.tick_params(axis='y', labelcolor=color)
# ax = plt.sca(ax1)
# ax=plt.gca()
# ax.grid(which = 'major', axis='y',linestyle='-.', color='#c5d7ed',linewidth=0.1)
# ax.grid(which = 'major', axis='x',linestyle='-.', color='#c5d7ed',linewidth=0.1)
# ax.set_title(title,fontweight="bold",pad=20)
# ax.title.set_size(15)
# ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
# color = 'tab:blue'
# ax2.set_ylabel('months of imports', color=color,rotation=90)
# ax2.plot((total/dm.im_ma.loc[first:]),color=color)
# ax2.tick_params(axis='y', labelcolor=color)
# ax = plt.sca(ax1)
# ax=plt.gca()
# start, end = ax.get_xlim()
# length = total.shape[0]
# n_xticks = []
# n_xticklabels = []
# for i in range(length):
#     if np.mod(i+1,6)==0:
#         n_xticks.append(i)
#         n_xticklabels.append(total.index[i])

# if len(n_xticks) > 10:
#         takeOneFrom = int(np.ceil(len(n_xticks)/10))
#         n_xticks = n_xticks[::takeOneFrom]
#         n_xticklabels = n_xticklabels[::takeOneFrom]
        
# ax.set_xticks(n_xticks)
# ax.set_xticklabels(n_xticklabels, fontsize=7,rotation=0)
# ax.yaxis.set_tick_params(labelsize=7,rotation=0) 
# width=.5
# plt.xlim([-width, len(total)-width])
# plt.savefig(fig_dir + 'res1.png')


# plot_section("Interest rates")
# ### Interest rate

# plt.figure()
# plt.subplot(gs22[0,0])
# doPlot(line1 = dm['rate_pol'],
#        line2 = dm['rate_cbb_1w'],
#        line3 = dm['rate_cbb_4w'],
#        line4 = dm['rate_cbb_28w'],
#        line5 = dm['rate_gb_12w'],
#        line6 = dm['rate_gb_1y'],
#        line7 = dm['rate_gb_3y'],
#        title = 'Bill\Bond interest rate (%, p.a), last: ' + get(dm['rate_pol'],'last'),
#        leg   = ['Bom Pol.','CBB 1w','CBB 4w','CBB 28w','GovB 12w','GovB 1y','GovB 3y'],
#        rng   = [firstM])
# plt.subplot(gs22[0,1])
# doPlot(line1 = dm[['rate_pol']],
#        line2 = dm[['rate_ib_repo_cbb']],
#        line3 = dm[['rate_ib_on']],
#        line4 = dm[['rate_ib_war']],
#        title = 'Interbank interest rate (%, p.a), last: ' + get(dm['rate_pol'],'last'),
#        rng   = [firstM],
#        leg   = ['BoM Pol.','IB Repo CB','IB ON','IB WAR'])
# plt.subplot(gs22[1,1])
# doPlot(line1 = dm['rate_depo_fx'],
#        line2 = dm['rate_depo_fx_new'],
#        line3 = dm['rate_loan_fx'],
#        line4 = dm['rate_loan_fx_new'],
#        line5 = dm['rate_pol'],
#        title = 'Foreign Currency Interest rate (%, p.a), last: ' + get(dm['rate_depo_fx'],'last'),
#        leg   = ['Deposit','Deposit (new)','Lending','Lending (new)','BoM policy'],
#        rng   = [firstM])
# plt.subplot(gs22[1,0])
# doPlot(line1 = dm['rate_depo_mnt'],
#        line2 = dm['rate_depo_mnt_new'],
#        line3 = dm['rate_loan_mnt'],
#        line4 = dm['rate_loan_mnt_new'],
#        line5 = dm['rate_pol'],
#        title = 'Domestic Currency Interest rate (%, p.a), last: ' + get(dm['rate_depo_mnt'],'last'),
#        leg   = ['Deposit','Deposit (new)','Lending','Lending (new)','BoM policy'],
#        rng   = [firstM])
# plt.subplots_adjust(hspace=0.5)
# plt.savefig(fig_dir + 'ir1.png')
# #plt.figure()
# #plt.subplot(gs22[0,0])
# #doPlot(line1 = dm[['dep_rate_dc']],
# #       line2 = dm[['lend_rate_dc']],
# #       line3 = dm[['cb_bills_prate']],
# #       title = 'Domestic Currency Interest rate (%, p.a), last: ' + get(dm['dep_rate_dc'],'last'),
# #       leg   = ['Deposit','Lending','BoM Policy'],
# #       rng   = [firstM])
# #plt.subplot(gs22[1,0])
# #doPlot(line1 = dm[['dep_rate_fc']],
# #       line2 = dm[['lend_rate_fc']],
# #       title = 'Foreign Currency Interest rate (%, p.a), last: ' + get(dm['dep_rate_fc'],'last'),
# #       leg   = ['Deposit','Lending'],
# #       rng   = [firstM])
# #plt.subplot(gs22[0,1])
# #doPlot(line1 = dm[['cb_on_depo']],
# #       line2 = dm[['intb_rate_on_lns']],
# #       line3 = dm[['intb_rate_intb_d']],
# #       line4 = dm[['cb_bills_prate']],
# #       line5 = dm[['cb_repo']],
# #       line6 = dm[['cb_on_repo']],
# #       title = 'Interest rates (%, p.a), last: ' + get(dm['cb_on_depo'],'last'),
# #       rng   = ['15M01'])
# #plt.legend(['BoM ON Depo','Interbank ON','Interbank Depo','Policy','BoM Repo','BoM ON Repo'],loc='upper center', bbox_to_anchor=(0.5, -0.10),
# #                  frameon=False, ncol=3,fontsize=5)
# #plt.subplot(gs22[1,1])
# #doPlot(line1 = dm['cb_bills_rate_4w'],
# #       line2 = dm['cb_bills_rate_28w'],
# #       line3 = dm['tbills_rate_12w'],
# #       line4 = dm['tbills_rate_13w'],
# #       title = 'Interest rates (%, p.a), last: ' + get(dm['cb_bills_rate_4w'],'last'),
# #       leg   = ['CBB 4w','CBB 12w','T-bill 12w','T-bill 13w','T-bill 1y','T-bill 3y','T-bill 5y'],
# #       rng   = [firstM])
# #plt.subplots_adjust(hspace=0.5)

# ### Eurobond yield

# # dm['ir_bond_18'].loc['18M01'] = None

# # plt.figure()
# # plt.subplot(gs21[0])
# # doPlot(line1 = dm['ir_bond_18'],
# #        line2 = dm['ir_bond_22'],
# #        line3 = dm['ir_bond_24'],
# #        line4 = dm['ir_bond_18_cny'],
# #        title = 'Mongolian Government International Bond Yields (%, p.a, mid-YTM), last: ' + get(dm['ir_bond_22'],'last'),
# #        leg   = ['USD-2018','USD-2022','USD-2024','CNY-2018'],
# #        rng   = ['13M01'])
# # plt.subplot(gs21[1])
# # doPlot(line1 = dm['i_1w_libor_usd'],
# #        line2 = dm['i_12m_libor_usd'],
# #        line3 = dm['us10_govt'],
# #        line4 = dm['embi'],
# #        title = 'World USD Interest rates (%, p.a, mid-YTM), last: ' + get(dm['i_1w_libor_usd'],'last'),
# #        leg   = ['Libor 1w','Libor 12w','US T-bill 10Y','EMBI'],
# #        rng   = ['13M01'])
# # plt.subplots_adjust(hspace=0.5)



# plot_section("Bank and Money Supply")

# ### Money supply

# plt.figure()
# plt.subplot(gs21[0,0])
# doPlot(line1 = dm['cb_mbase']/1e6,
#        bar   = dm[['cb_nfa','cb_nda','cb_ca','cb_oth_net']]/1e6,
#        title = 'Monetary base (tn MNT), last: ' + get(dm['cb_nfa'],'last'),
#        leg   = ['_nolegend_','NFA','NDA','Capital','Other items (net)'],
#        rng   = [firstM])
# plt.subplot(gs21[1,0])
# doPlot(line1 = 100*dq['cb_mbase']/dq['gdp_nom_y'],
#        bar   = 100*dq[['cb_nfa','cb_nda','cb_ca','cb_oth_net']].div(dq['gdp_nom_y'],axis=0),
#        title = 'Monetary base (% of GDP), last: ' + get(dq['cb_nfa'],'last'),
#        leg   = ['_nolegend_','NFA','NDA','Capital','Other items (net)'],
#        rng   = [firstQ])
# plt.subplots_adjust(hspace=0.5)
# plt.savefig(fig_dir + 'ms1.png')

# plt.figure()
# plt.subplot(gs21[0,0])
# doPlot(line1 = dm['ms_m2']/1e6,
#        bar   = dm[['ms_cashout','ms_m2_dep_ca_dc','ms_dep_mnt','ms_ca_fx','ms_dep_fx']]/1e6,
#        title = 'Money supply (M2, tn MNT), last: ' + get(dm['ms_m2'],'last'),
#        leg   = ['_nolegend_','Currency outside Bank','CurrA LCY','Time depo LCY','CurrA FCY','Time depo FCY'],
#        rng   = [firstM])
# plt.subplot(gs21[1,0])
# doPlot(line1 = 100*dq['ms_m2']/dq['gdp_nom_y'],
#        bar   = 100*dq[['ms_cashout','ms_m2_dep_ca_dc','ms_dep_mnt','ms_ca_fx','ms_dep_fx']].div(dq['gdp_nom_y'],axis=0),
#        title = 'Money supply (M2, % of GDP), last: ' + get(dq['ms_m2'],'last'),
#        leg   = ['_nolegend_','Currency outside Bank','CurrA LCY','Time depo LCY','CurrA FCY','Time depo FCY'],
#        rng   = [firstQ])
# plt.subplots_adjust(hspace=0.5)
# plt.savefig(fig_dir + 'ms2.png')
# # plt.figure()
# # plt.subplot(gs21[0,0])
# # doPlot(bar   = 100*dm[['bs_ma_mb_cob','ms_m2_dep_ca_dc','ms_m2_dep_td_dc','ms_m2_dep_ca_fc','ms_m2_dep_td_fc']].div(dm['ms_m2'],axis=0),
# #        title = 'Money supply breakdown, last: ' + get(dm['ms_m2'],'last'),
# #        leg   = ['Currency outside Bank','CurrA LCY','Time depo LCY','CurrA FCY','Time depo FCY'],
# #        rng   = ["13M01"])
# # plt.subplots_adjust(hspace=0.5)

# ### Bank balance 

# # dm[['dc_res','dc_cbb','dc_fa','dc_gov','dc_fi','dc_pub','dc_corp','dc_ind','dc_oth']]/1e6
# plt.figure()
# plt.subplot(gs21[0,0])
# doPlot(line1=dm["bs_tot_ass"].div(1e6),
#        bar   = dm[['dc_corp','dc_ind','dc_fi','dc_res','dc_cbb','dc_fa','dc_gov',
#         'dc_pub','dc_oth']]/1e6,
#        title = 'Banking sector assets (tn MNT), last: ' + get(dm['bs_tot_ass'],'last'),
#        rng   = [firstM])
# plt.legend(['_nolegend_','Claims on Corp','Claims on Ind','Claims on oth fin','Res.','CBB','FA',
#             'Claims on Govt','Claims on Public sect',
#            'Claims Oth'],
#            loc='upper center', bbox_to_anchor=(0.5, -0.10),
#                   frameon=False, ncol=5,fontsize=5)
# plt.subplot(gs21[1,0])
# doPlot(line1=100*dq["bs_tot_ass"]/dq['gdp_nom_y'],
#        bar   = 100*dq[['dc_corp','dc_ind','dc_fi','dc_res','dc_cbb','dc_fa','dc_gov',
#         'dc_pub','dc_oth']].div(dq['gdp_nom_y'],axis=0),
#        title = 'Banking sector assets (% of GDP), last: ' + get(dq['bs_tot_ass'],'last'),
#        rng   = [firstQ])
# plt.legend(['_nolegend_','Claims in Priv Sect','Claims on Ind','Claims on oth fin','Res.','CBB','FA',
#             'Claims on Govt','Claims on Public sect',
#            'Claims Oth'],
#            loc='upper center', bbox_to_anchor=(0.5, -0.10),
#                   frameon=False, ncol=5,fontsize=5)
# plt.subplots_adjust(hspace=0.5)
# plt.savefig(fig_dir + 'bank1.png')

# plt.figure()
# plt.subplot(gs21[0,0])
# doPlot(line1=dm["bs_tot_liab"].div(1e6),
#        bar   = dm[['dc_ca_mnt','dc_quasimoney','dc_fl','dc_fl_long','dc_gov_depo',
#         'dc_cbloan','dc_ca','dc_oth_net']]/1e6,
#        title = 'Banking sector liabilities (tn MNT), last: ' + get(dm['bs_tot_liab'],'last'),
#        rng   = [firstM])
# plt.legend(['_nolegend_','CA LCY','Deposits','Foreign Liab Short',
#            'Foreign Liab Long','Govt Depo','Credit from BoM',
#            'Capital','Other (net)'],
#            loc='upper center', bbox_to_anchor=(0.5, -0.10),
#                   frameon=False, ncol=5,fontsize=5)
# plt.subplot(gs21[1,0])
# doPlot(line1=100*dq["bs_tot_liab"]/dq['gdp_nom_y'],
#        bar   = 100*dq[['dc_ca_mnt','dc_quasimoney','dc_fl','dc_fl_long','dc_gov_depo',
#         'dc_cbloan','dc_ca','dc_oth_net']].div(dq['gdp_nom_y'],axis=0),
#        title = 'Banking sector liabilities (% of GDP), last: ' + get(dq['bs_tot_liab'],'last'),
#        rng   = [firstQ])
# plt.legend(['_nolegend_','CA LCY','Deposits','Foreign Liab Short',
#            'Foreign Liab Long','Govt Depo','Credit from BoM',
#            'Capital','Other (net)'],
#            loc='upper center', bbox_to_anchor=(0.5, -0.10),
#                   frameon=False, ncol=5,fontsize=5)
# plt.subplots_adjust(hspace=0.5)
# plt.savefig(fig_dir + 'bank2.png')


# ### Loan

# plt.figure()
# plt.subplot(gs22[0,0])
# doPlot(line1 = dq['bank_ass_credit_nfi']/1e6,
#        bar   = dq[['bank_ass_credit_norm','bank_ass_credit_ovrd','bank_ass_credit_npl']]/1e6,
#        title = 'Credit (tn MNT), last: ' + get(dq['bank_ass_credit_nfi'],'last'),
#        leg   = ['_nolegend_','Standard','OVRD','NPL'],
#        rng   = [firstQ])
# plt.subplot(gs22[0,1])
# doPlot(line1 = dq['bank_ass_credit_nfi']/1e6,
#        bar   = dq[['bank_ass_credit_corp','bank_ass_credit_ind','bank_ass_credit_pub','bank_ass_credit_oth']]/1e6,
#        title = 'Credit (tn MNT), last: ' + get(dq['bank_ass_credit_nfi'],'last'),
#        leg   = ['_nolegend_','Corp.','Indiv.','Public','Other'],
#        rng   = [firstQ])
# plt.subplot(gs22[1,0])
# doPlot(line1 = dq['bank_ass_credit_nfi']/1e6,
#        bar   = dq[['bank_ass_credit_mnt','bank_ass_credit_fx']]/1e6,
#        title = 'Credit (tn MNT), last: ' + get(dq['bank_ass_credit_nfi'],'last'),
#        leg   = ['_nolegend_','MNT','FX'],
#        rng   = [firstQ])
# plt.subplot(gs22[1,1])
# doPlot(line1 = 100*dq.bank_ass_credit_npl/dq.bank_ass_credit_nfi,
#        title = 'NPL (% of total), last: ' + get(dq['bank_ass_credit_nfi'],'last'),
#        rng   = [firstQ])
# plt.subplots_adjust(hspace=0.5)
# plt.savefig(fig_dir + 'bank3.png')

# plt.figure()
# plt.subplot(gs22[0,0])
# doPlot(line1 = 100*dq['bank_ass_credit_nfi']/dq['gdp_nom_y'],
#        bar   = 100*dq[['bank_ass_credit_norm','bank_ass_credit_ovrd','bank_ass_credit_npl']].div(dq['gdp_nom_y'],axis=0),
#        title = 'Credit (% of GDP), last: ' + get(dq['bank_ass_credit_nfi'],'last'),
#        leg   = ['_nolegend_','Standard','OVRD','NPL'],
#        rng   = [firstQ])
# plt.subplot(gs22[0,1])
# doPlot(line1 = 100*dq['bank_ass_credit_nfi']/dq['gdp_nom_y'],
#        bar   = 100*dq[['bank_ass_credit_corp','bank_ass_credit_ind','bank_ass_credit_pub','bank_ass_credit_oth']].div(dq['gdp_nom_y'],axis=0),
#        title = 'Credit (% of GDP), last: ' + get(dq['bank_ass_credit_nfi'],'last'),
#        leg   = ['_nolegend_','Corp.','Indiv.','Public','Other'],
#        rng   = [firstQ])
# plt.subplot(gs22[1,0])
# doPlot(line1 = 100*dq['bank_ass_credit_nfi']/dq['gdp_nom_y'],
#        bar   = 100*dq[['bank_ass_credit_mnt','bank_ass_credit_fx']].div(dq['gdp_nom_y'],axis=0),
#        title = 'Credit (% of GDP), last: ' + get(dq['bank_ass_credit_nfi'],'last'),
#        leg   = ['_nolegend_','MNT','FX'],
#        rng   = [firstQ])
# plt.subplot(gs22[1,1])
# doPlot(line1 = 100*dq.bank_ass_credit_npl/dq.bank_ass_credit_nfi,
#        title = 'NPL (% of total), last: ' + get(dq['bank_ass_credit_nfi'],'last'),
#        rng   = [firstQ])
# plt.subplots_adjust(hspace=0.5)
# plt.savefig(fig_dir + 'bank4.png')


# plt.figure()
# plt.subplot(gs22[0,0])
# doPlot(line1 = dm['bank_ass_credit_npl_corp']/dm['bank_ass_credit_corp']*100,
#        title = 'Corporate NPL ratio, last: ' + get(dm['bank_ass_credit_corp'],'last'),
#        rng   = [firstM])
# plt.subplot(gs22[0,1])
# doPlot(line1 = dm['bank_ass_credit_npl_mnt_corp']/dm['bank_ass_credit_mnt_corp']*100, 
#        title = 'Corporate FX NPL ratio, last: ' + get(dm['bank_ass_credit_corp'],'last'),
#        rng   = [firstM])
# plt.subplot(gs22[1,0])
# doPlot(line1 = dm['bank_ass_credit_npl_fx_corp']/dm['bank_ass_credit_fx_corp']*100, 
#        title = 'Corporate FX NPL ratio, last: ' + get(dm['bank_ass_credit_corp'],'last'),
#        rng   = [firstM])
# plt.subplots_adjust(hspace=0.5)
# plt.savefig(fig_dir + 'bank5.png')

# plt.figure()
# plt.subplot(gs22[0,0])
# doPlot(line1 = dm['bank_ass_credit_npl_ind']/dm['bank_ass_credit_ind']*100,
#        title = 'Individual NPL ratio, last: ' + get(dm['bank_ass_credit_corp'],'last'),
#        rng   = [firstM])
# plt.subplot(gs22[0,1])
# doPlot(line1 = dm['bank_ass_credit_npl_mnt_ind']/dm['bank_ass_credit_mnt_ind']*100, 
#        title = 'Individual FX NPL ratio, last: ' + get(dm['bank_ass_credit_corp'],'last'),
#        rng   = [firstM])
# plt.subplot(gs22[1,0])
# doPlot(line1 = dm['bank_ass_credit_npl_fx_ind']/dm['bank_ass_credit_fx_ind']*100, 
#        title = 'Individual FX NPL ratio, last: ' + get(dm['bank_ass_credit_corp'],'last'),
#        rng   = [firstM])
# plt.subplots_adjust(hspace=0.5)
# plt.savefig(fig_dir + 'bank6.png')


# ### Credit
# plt.figure()
# plt.subplot(gs21[0])
# doPlot(line1 = pct(dm['bank_ass_credit_nfi'],-12),
#        line2 = pct(dm['dc_loan_corp'],-12),
#        line3 = pct(dm['dc_loan_ind'],-12),
#        title = 'Credit Growth (%, YoY), last: ' + get(dm['bank_ass_credit_nfi'],'last'),
#        leg   = ['Total','Corporate','Individuals'],
#        rng   = [firstM])
# plt.subplot(gs21[1])
# doPlot(line1 = pct(dm['bank_ass_credit_nfi'],-1),
#        line2 = pct(dm['dc_loan_corp'],-1),
#        line3 = pct(dm['dc_loan_ind'],-1),
#        title = 'Credit Growth (%, MoM), last: ' + get(dm['bank_ass_credit_nfi'],'last'),
#        leg   = ['Total','Corporate','Individuals'],
#        rng   = [firstM])
# plt.subplots_adjust(hspace=0.5)
# plt.savefig(fig_dir + 'bank4.png')

# ### Money supply growth
# plt.figure()
# plt.subplot(gs21[0])
# doPlot(line1 = pct(dm['cb_mbase'],-12),
#        line2 = pct(dm['ms_m1'],-12),
#        line3 = pct(dm['ms_m2'],-12),
#        title = 'Money Supply Growth (%, YoY), last: ' + get(dm['cb_mbase'],'last'),
#        leg   = ['Money base','M1','M2'],
#        rng   = [firstM])
# plt.subplot(gs21[1])
# doPlot(line1 = pct(dm['cb_mbase'],-1),
#        line2 = pct(dm['ms_m1'],-1),
#        line3 = pct(dm['ms_m2'],-1),
#        title = 'Money Supply Growth (%, MoM), last: ' + get(dm['cb_mbase'],'last'),
#        leg   = ['Money base','M1','M2'],
#        rng   = [firstM])
# plt.subplots_adjust(hspace=0.5)
# plt.savefig(fig_dir + 'ms3.png')

# ### Deposit growth

# dm['ms_m2_dc'] = dm['bank_liab_cur_mnt'] + dm['bank_liab_depo_dem_mnt'] + dm['bank_liab_depo_time_mnt']
# dm['ms_m2_fc'] = dm['bank_liab_cur_fx'] + dm['bank_liab_depo_dem_fx'] + dm['bank_liab_depo_time_fx']

# plt.figure()
# plt.subplot(gs21[0])
# doPlot(line1 = pct(dm['ms_m2_dc'],-12),
#        line2 = pct(dm['ms_m2_fc'],-12),
#        line3 = pct(dm['ms_m2'],-12),
#        title = 'Money Supply Growth (%, YoY), last: ' + get(dm['ms_m2'],'last'),
#        leg   = ['MNT deposits (including CA)','FX deposits (including CA)','M2'],
#        rng   = ['15M01'])
# plt.subplot(gs21[1])
# doPlot(line1 = pct(dm['ms_m2_dc'],-1),
#        line2 = pct(dm['ms_m2_fc'],-1),
#        line3 = pct(dm['ms_m2'],-1),
#        title = 'Money Supply Growth (%, MoM), last: ' + get(dm['ms_m2'],'last'),
#        leg   = ['MNT deposits (including CA)','FX deposits (including CA)','M2'],
#        rng   = ['15M01'])
# plt.subplots_adjust(hspace=0.5)
# plt.savefig(fig_dir + 'ms4.png')

# plot_section("Fiscal sector")
# # Budget

# plt.figure()
# plt.subplot(gs21[0])
# doPlot(line1 = (dq['gov_rev_eq'] - dq['gov_exp'])/1e3,
#        bar   = dq[['gov_rev_eq','gov_exp']]*[1,-1]/1e3,
#        title = 'Budget balance (tn MNT), last: ' + get(dq['gov_rev_eq'],'last'),
#        leg   = ['_nolegend_','Revenue','Expense'],
#        rng   = [firstQ])
# plt.subplot(gs21[1])
# doPlot(line1 = 100*1e3*(dy['gov_rev_eq'] - dy['gov_exp'])/dy['gdp_nom'],
#        bar   = 100*1e3*(dy[['gov_rev_eq','gov_exp']]*[1,-1]).div(dy['gdp_nom'],axis=0),
#        title = 'Budget balance (% of GDP), last: ' + '22Y',
#        leg   = ['_nolegend_','Revenue','Expense'],
#        rng   = [firstY,'22Y'])
# plt.subplots_adjust(hspace=0.5)
# plt.savefig(fig_dir + 'budget1.png')

# plt.figure()
# plt.subplot(gs21[0])
# doPlot(line1 = 100*1e3*dq['gov_rev_eq']/dq['gdp_nom_y'],
#        bar   = 100*1e3*dq[['gov_rev_cur_tax','gov_rev_cur_nontax','gov_rev_cap','gov_rev_grant']].div(dq['gdp_nom_y'],axis=0),
#        title = 'Total revenue (% of GDP), last: ' + get(dq['gov_rev_eq'],'last'),
#        leg   = ['_nolegend_','Tax Revenue','Non-tax Revenue','Capital','Grants&Transfer'],
#        rng   = [firstQ])
# plt.subplot(gs21[1])
# doPlot(line1 = 100*1e3*dq['gov_rev_cur_tax']/dq['gdp_nom_y'],
#        bar   = 100*dq[['gov_rev_corp_nso','gov_rev_ind_nso','gov_rev_ssc_nso','gov_rev_vat_nso','gov_rev_spectax_nso']].div(dq['gdp_nom_y'],axis=0),
#        title = 'Tax revenue (% of GDP), last: ' + get(dq['gov_rev_cur_tax'],'last'),
#        leg   = ['_nolegend_','Corporate','Individual','Social Security Contrib.','VAT','Excise'],
#        rng   = [firstQ])
# plt.subplots_adjust(hspace=0.5)
# plt.savefig(fig_dir + 'budget2.png')


# plt.figure()
# plt.subplot(gs21[0])
# doPlot(line1 = 100*1e3*dq['gov_exp']/dq['gdp_nom_y'],
#        bar   = 100*1e3*dq[['gov_exp_cur','gov_exp_cap','gov_exp_netloan']].div(dq['gdp_nom_y'],axis=0),
#        title = 'Total expenditure (% of GDP), last: ' + get(dq['gov_exp'],'last'),
#        leg   = ['_nolegend_','Current','Capital','Net lending'],
#        rng   = [firstQ])
# plt.subplot(gs21[1])
# doPlot(line1 = 100*(dq[['gov_exp_cur_sal_nso','gov_exp_cur_goods_nso','gov_exp_cur_subtran_nso','gov_exp_cur_int_nso']].sum(axis=1))/dq['gdp_nom_y'],
#        bar   = 100*dq[['gov_exp_cur_subtran_nso','gov_exp_cur_sal_nso','gov_exp_cur_goods_nso','gov_exp_cur_int_nso']].div(dq['gdp_nom_y'],axis=0),
#        title = 'Current expenditure (% of GDP), last: ' + get(dq['gov_exp_cur'],'last'),
#        leg = [],
#        rng   = ['10Q1'])
# plt.subplots_adjust(hspace=0.5)
# plt.savefig(fig_dir + 'budget3.png')

# plt.figure()
# plt.subplot(gs21[0])
# doPlot(bar   = 100*dq[['gov_exp_cur','gov_exp_cap','gov_exp_netloan']].div(dq[['gov_exp_cur','gov_exp_cap','gov_exp_netloan']].sum(axis=1),axis=0),
#        title = 'Total expenditure (composition), last: ' + get(dq['gov_exp'],'last'),
#        leg   = ['Current','Capital','Net lending'],
#        rng   = [firstQ])
# plt.subplot(gs21[1])
# doPlot(bar   = 100*dq[['gov_exp_cur_subtran_nso','gov_exp_cur_sal_nso','gov_exp_cur_goods_nso','gov_exp_cur_int_nso',]].div(dq[['gov_exp_cur_sal_nso','gov_exp_cur_goods_nso','gov_exp_cur_subtran_nso','gov_exp_cur_int_nso']].sum(axis=1),axis=0),
#        title = 'Current expenditure (composition), last: ' + get(dq['gov_exp_cur'],'last'),
#        leg   = ['Subsidies & Transfers','Salary','Goods & Services','Interest expense'],
#        rng   = ['10Q1'])
# plt.subplots_adjust(hspace=0.5)
# plt.savefig(fig_dir + 'budget4.png')

# # plt.figure()
# # doPlot(line1 = dq['debt_ext_tot']/1e3,
# #        bar   = dq[['debt_ext_gg','debt_ext_cb','debt_ext_odc','debt_ext_oth','debt_ext_di']]/1e3,
# #        title = 'Total External Debt (bn USD), last: ' + get(dq['debt_ext_tot'],'last'),
# #        leg   = ['_nolegend_','Government','Central Bank','Commercial Banks','Other Sector', "FDI"],
# #        rng   = [firstQ])

# # plot_section("Socio-economic")
# # ### Social

# # plt.figure()
# # plt.subplot(gs21[0])
# # doPlot(line1 = dq['hh_inc']/1e6,
# #        bar   = dq[['hh_inc_mon_sal','hh_inc_mon_pen','hh_inc_mon_live','hh_inc_mon_agr','hh_inc_mon_nonagr','hh_inc_mon_oth','hh_inc_gift','hh_inc_ownfood']]/1e6,
# #        title = 'Household income (mln MNT), last: ' + get(dq['hh_inc_mon_sal'],'last'),
# #        leg   = ['_nolegend_','Salary','Pension','Livestock','Agriculture','Non-Agro','Other','Gift','Own food'],
# #        rng   = [firstQ])
# # plt.subplot(gs21[1])
# # doPlot(line1 = dq['hh_exp']/1e6,
# #        bar   = dq[['hh_exp_mon_food','hh_exp_mon_nonfood','hh_exp_mon_oth','hh_exp_giftto','hh_exp_giftfrom','hh_exp_ownfood']]/1e6,
# #        title = 'Household expenses (mln MNT), last: ' + get(dq['hh_exp_mon_food'],'last'),
# #        leg   = ['_nolegend_','Food','Nonfood','Other','Gift to others','Gift from others','Own food'],
# #        rng   = [firstQ])
# # plt.subplots_adjust(hspace=0.5)
# # plt.savefig(fig_dir + 'hh1.png')

# # plt.figure()
# # doPlot(line1 = dq['wage_avg']/1e3,
# #        line2 = dq['wage_median']/1e3,
# #        title = 'Monthly salary (national, mln MNT), last: ' + get(dq['wage_avg'],'last'),
# #        leg   = ['Average','Median'],
# #        rng   = [firstQ])
# # plt.savefig(fig_dir + 'hh2.png')

# # plt.figure()
# # plt.subplot(gs21[0])
# # doPlot(line1 = dy['poverty_tot'],
# #        line2 = dy['poverty_urban'],
# #        line3 = dy['poverty_rural'],
# #        title = 'Poverty rate, last: ' + get(dy['poverty_tot'],'last'),
# #        leg   = ['Total','Urban','Rural'],
# #        rng   = [firstY])
# # plt.subplot(gs21[1])
# # doPlot(line1 = dq['hh_exp']/dq['hh_inc']*100,
# #        title = 'Household Expense to Income (times 100), last: ' + get(dq['hh_exp'],'last'),
# #        rng   = [firstQ])
# # plt.subplots_adjust(hspace=0.5)
# # plt.savefig(fig_dir + 'hh3.png')

# plot_section("Other")
# ### MSE

# plt.figure()
# plt.subplot(gs21[0])
# doPlot(line1 = dm['mse_top20_avg'],
#        title = 'MSE TOP 20 Index (average), last: ' + get(dm['mse_top20_avg'],'last'),
#        rng   = [firstM])
# plt.subplot(gs21[1])
# doPlot(line1 = pct(dm['mse_top20_avg'],-12),
#        line2 = 12*pct(dm['mse_top20_avg'],-1),
#        title = 'MSE TOP 20 index change (%), last: ' + get(dm['mse_top20_avg'],'last'),
#        leg   = ['MoM @ar','YoY'],
#        rng   = ['12M01'])
# plt.subplots_adjust(hspace=0.5)
# plt.savefig(fig_dir + 'mse1.png')

import matplotlib.backends.backend_pdf
pdf = matplotlib.backends.backend_pdf.PdfPages(r"output\data_exploration.pdf")
for fig in range(1, plt.gcf().number+1): ## will open an empty extra figure :(
    pdf.savefig( fig )
pdf.close()


