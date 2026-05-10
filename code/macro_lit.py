import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

import sys
sys.path.append('D:\economics\GIT\monmacro\code')

from plotting import *
from montools import *

db_d    = '../data/data_daily.xlsx'
db_m    = '../data/data_monthly.xlsx'
db_q    = '../data/data_quarterly.xlsx'
db_y    = '../data/data_yearly.xlsx'
name_date = '2023M08'

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


p_list = ['food', 'alco','clot','elec','furn','heal','tran','comm',
          'recr','educ','hote','insu','oth']
exp_list = ['ex_gold','ex_copper','ex_fluoride','ex_iron','ex_zinc', 	 
       'ex_cashmere_raw','ex_cashmere_comb','ex_coal','ex_oil']
im_list = ['im_fuel','im_veh','im_truck','im_elec','im_comm']
budget_list = ['gov_rev','gov_rev_cur','gov_rev_cur_tax','gov_rev_cur_nontax','gov_rev_cap',
               'gov_rev_grant','gov_rev_fut','gov_rev_stab','gov_exp','gov_exp_cur','gov_exp_cap','gov_exp_netloan']
budget_list2 = ['gov_rev_nso','gov_rev_fut_nso','gov_rev_stab_nso','gov_rev_net_nso','gov_rev_tax_nso',	
                'gov_rev_corp_nso','gov_rev_ind_nso','gov_rev_ssc_nso','gov_rev_vat_nso','gov_rev_spectax_nso',	
                'gov_rev_nontax_nso','gov_exp_nso','gov_exp_cur_nso',	'gov_exp_cur_sal_nso','gov_exp_cur_goods_nso',	
                'gov_exp_cur_int_nso','gov_exp_cur_sub_nso','gov_exp_cur_transfer_gov_nso',	
                'gov_exp_cur_transfer_oth_nso','gov_exp_cap_nso','gov_exp_netloan_nso']

trade_list = ['ex','im']

# decumulate 
for elem in exp_list:
    dm[elem] = dm[elem + "_cum"].diff()/1e3
    dm[elem+ "_vol"] = dm[elem + "_vol" + "_cum"].diff()/1e3
    dm[elem][dm[elem]<0] = dm[elem + "_cum"][dm[elem]<0]/1e3  
for elem in im_list:
    dm[elem] = dm[elem + "_cum"].diff()/1e3
    dm[elem + "_vol"] = dm[elem + "_vol" + "_cum"].diff()/1e3
    dm[elem][dm[elem]<0] = dm[elem + "_cum"][dm[elem]<0]/1e3  
for elem in budget_list:
    dm[elem] = dm[elem + "_cum"].diff()/1e3
    dm[elem][dm[elem]<0] = dm[elem + "_cum"][dm[elem]<0]/1e3
for elem in trade_list:
    dm[elem] = dm[elem + "_cum"].diff()/1e3
    dm[elem][dm[elem]<0] = dm[elem + "_cum"][dm[elem]<0]/1e3 


# inflation
 
# build CPI level from cpi_mom
# 15
for ind in p_list:
    dm['cpi_' + ind + '_15'] = dm['cpi_' + ind + '_15_mom'].dropna().copy()
    first = dm['cpi_' + ind + '_15_mom'].dropna().index[0]
    dm['cpi_' + ind + '_15'][first] = 100
    ind_first = dm.index.get_loc(first)
    for i in range(ind_first+1,ind_first+len(dm['cpi_' + ind + '_15_mom'].dropna())):
            dm['cpi_' + ind + '_15'][i] = dm['cpi_' + ind + '_15'][i-1]*(1+dm['cpi_' + ind + '_15_mom'][i]/100)
# 20
for ind in p_list:
    dm['cpi_' + ind] = dm['cpi_' + ind + '_20_mom'].dropna().copy()
    first = dm['cpi_' + ind + '_20_mom'].dropna().index[0]
    dm['cpi_' + ind][first] = 100
    ind_first = dm.index.get_loc(first)
    for i in range(ind_first+1,ind_first+len(dm['cpi_' + ind + '_20_mom'].dropna())):
            dm['cpi_' + ind][i] = dm['cpi_' + ind][i-1]*(1+dm['cpi_' + ind + '_20_mom'][i]/100)

for ind in p_list:
    dm['cpi_' + ind] = bmerge(dm['cpi_' + ind + '_15'],dm['cpi_' + ind])

# yoy from CPI level # yoy cpi by weighted components
cpi_yoy_tot_comp = pd.DataFrame()
for ind in p_list:
    dm['cpi' + ind + '_yoy'] = pct(dm['cpi_' + ind],-12)
    elem = (dm["cpi_w_" + ind]/100*dm["cpi" + ind + "_yoy"]).dropna()
    cpi_yoy_tot_comp[ind] = elem

# mom cpi by weighted components
cpi_mom_tot_comp=pd.DataFrame()
for ind in p_list:
    elem = (dm["cpi_w_" + ind]/100*pct(dm["cpi_" + ind],-1)).dropna()
    cpi_mom_tot_comp[ind] = elem

dm["cpi_nonfood_yoy"] = (pct(dm.cpi,-12)-dm.cpi_w_food.shift(12)*pct(dm.cpi_food,-12)/100)/(1-dm.cpi_w_food.shift(12)/100)   
dm["cpi_nonfood_mom"] = (pct(dm.cpi,-1)-dm.cpi_w_food.shift()*pct(dm.cpi_food,-1)/100)/(1-dm.cpi_w_food.shift()/100)      

for ind in ['nonfood']:
    dm['cpi_' + ind] = dm['cpi_' + ind + '_mom'].dropna().copy()
    first = dm['cpi_' + ind + '_mom'].dropna().index[0]
    dm['cpi_' + ind][first] = 100
    ind_first = dm.index.get_loc(first)
    for i in range(ind_first+1,ind_first+len(dm['cpi_' + ind + '_mom'].dropna())):
            dm['cpi_' + ind][i] = dm['cpi_' + ind][i-1]*(1+dm['cpi_' + ind + '_mom'][i]/100)

# Seasonal adjustment
for ind in p_list:
    dm['cpi_' + ind + '_sa'] = sa(dm['cpi_' + ind])
    dm['cpi_' + ind + '_mom_sa'] = pct(dm['cpi_' + ind + '_sa'],-1)

for ind in ['cpi','cpi_nonfood']:
       dm[ind + '_sa'] = sa(dm[ind])       
       dm[ind + '_mom_sa'] = pct(dm[ind + '_sa'],-1)

cpi_mom_tot_comp_sa=pd.DataFrame()
for ind in p_list:
    elem = (dm["cpi_w_" + ind]/100*pct(dm["cpi_" + ind + '_sa'],-1)).dropna()
    cpi_mom_tot_comp_sa[ind] = elem

dy['gdp_nom'] = convert(dq['gdp_nom'],'y')

dq['gdp'] = bmerge(bmerge(dq['gdp_05'],dq['gdp_10']), dq['gdp_15'])
dy['gdp'] = convert(dq['gdp'],'y')


gdp_list = ['agr', 'mine', 'manu', 'elec', 'cons', 'trad', 'tran', 'comm', 'serv_oth', 'tax']

for sector in gdp_list:
       dq['gdp_' + sector] = bmerge(bmerge(dq['gdp_' + sector + '_05'],dq['gdp_' + sector + '_10']), dq['gdp_' + sector + '_15'])
       dy['gdp_' + sector] = convert(dq['gdp_' + sector],'y')

### Real GDP growth
    
gdp_comp_all = dq[['gdp_agr','gdp_mine','gdp_manu','gdp_elec',
                   'gdp_cons','gdp_trad','gdp_tran','gdp_comm',
                   'gdp_serv_oth','gdp_tax','gdp']]
# last one is total, others are components
gdp_comp_diff_rel_all = gdp_comp_all.diff(periods=4).div(dq.gdp.shift(4), axis=0)*100
gdp_comp_diff_rel     = gdp_comp_diff_rel_all.iloc[:,:-1]
gdp_comp_diff_rel_tot = gdp_comp_diff_rel_all.iloc[:,-1]

gdp_comp_all_y = dy[['gdp_agr','gdp_mine','gdp_manu','gdp_elec',
                   'gdp_cons','gdp_trad','gdp_tran','gdp_comm',
                   'gdp_serv_oth','gdp_tax','gdp']]


# last one is total, others are components
gdp_comp_diff_rel_all_y = gdp_comp_all_y.diff(periods=1).div(dy.gdp.shift(1), axis=0)*100
gdp_comp_diff_rel_y     = gdp_comp_diff_rel_all_y.iloc[:,:-1]
gdp_comp_diff_rel_tot_y = gdp_comp_diff_rel_all_y.iloc[:,-1]


dy["usd_mnt_last"] = convert(dm["usd_mnt"],'y','last')
dy["usd_mnt_avg"] = convert(dm["usd_mnt"],'y','average')
dy["cpi_last"] = convert(dm["cpi"],'y','last')


dm["l_mnt_usd"] = 100*np.log(dm["usd_mnt"])
dm["l_mnt_cny"] = dm["l_mnt_usd"] - 100*np.log(dm["usd_mnt"]/dm["cny_mnt"])
dm["l_mnt_rub"] = dm["l_mnt_usd"] - 100*np.log(dm["usd_mnt"]/dm["rub_mnt"])
dm["l_mnt_eur"] = dm["l_mnt_usd"] - 100*np.log(dm["usd_mnt"]/dm["eur_mnt"])


# Money bank

dm["bs_tot_ass"] = dm[['dc_res','dc_cbb','dc_fa','dc_gov','dc_fi',
        'dc_pub','dc_corp','dc_ind','dc_oth']].dropna().sum(axis=1)
dm["bs_tot_liab"] = dm[['dc_ca_mnt','dc_quasimoney','dc_fl','dc_fl_long','dc_gov_depo',
        'dc_cbloan','dc_ca','dc_oth_net']].dropna().sum(axis=1)  

# dm["bs_ma_nfa"] = dm.dc_fa-dm.dc_fl-dm.dc_fl_long
dm["cb_nda"] = dm.cb_mbase-(dm.cb_nfa+dm.cb_ca+dm.cb_oth_net)
dm["ms_m2_dep_ca_dc"] = dm.ms_m1-dm.ms_cashout

m_list = ['ms_cic','ms_cashvault','ms_cashout','ms_m1','ms_ca_mnt','ms_dep_oth','ms_dep_mnt',
'ms_dep_mnt_ind','ms_dep_mnt_corp','ms_dep_fx','ms_ca_fx','ms_m2','dc_nfa','dc_ndc','dc_ndc_gov',
'dc_ndc_gov_cen','dc_ndc_gov_loc','dc_ndc_gov_oth','dc_ndc_oth','dc_ndc_oth_fi','dc_ndc_oth_pub',
'dc_ndc_oth_corp','dc_ndc_oth_ind','dc_ndc_oth_oth','dc_ms','dc_quasimoney','dc_imfloan','dc_oth_net_tot',
'cb_nfa','cb_fa','cb_dc','cb_gov_net','cb_gov','cb_oth','cb_oth_pub','cb_oth_priv','cb_oth_fi','cb_mbase',
'cb_mbase_cashout','cb_mbase_cashvault','cb_mbase_bankdepo','cbb','cb_fl','cb_fl_long','cb_gov_depo','cb_ca',
'cb_oth_net','dc_res','dc_cbb','dc_fa','dc_gov','dc_fi','dc_pub','dc_corp','dc_ind','dc_oth','dc_ca_mnt',
'dc_qm','dc_fl','dc_fl_long','dc_gov_depo','dc_cbloan','dc_ca','dc_oth_net'] + \
['bs_tot_ass','bs_tot_liab','cb_nda','ms_m2_dep_ca_dc']



for ind in m_list:
     dq[ind] = convert(dm[ind].copy(),'q',method='average')


dm['dc_loan_corp'] = dm.dc_loan_norm_corp + dm.dc_loan_overdue_corp + dm.dc_loan_npl_corp
dm['dc_loan_ind'] = dm.dc_loan_norm_ind + dm.dc_loan_overdue_ind + dm.dc_loan_npl_ind

bank_list = ['bank_ass_tot','bank_ass_res','bank_ass_res_cash','bank_ass_res_cbdepo_mnt','bank_ass_res_cbdepo_fx',
'bank_ass_res_cbdepo_oth','bank_ass_cbb','bank_ass_fa','bank_ass_fa_cash','bank_ass_fa_cur','bank_ass_fa_depo',
'bank_ass_fa_forbill','bank_ass_fa_forloan','bank_ass_gov_rec','bank_ass_bill','bank_ass_credit_net',
'bank_ass_credit_dom','bank_ass_credit_nfi','bank_ass_credit_norm','bank_ass_credit_norm_mnt',
'bank_ass_credit_norm_mnt_pub','bank_ass_credit_norm_mnt_corp','bank_ass_credit_norm_mnt_ind',
'bank_ass_credit_norm_mnt_oth','bank_ass_credit_norm_fx','bank_ass_credit_norm_fx_pub',
'bank_ass_credit_norm_fx_corp','bank_ass_credit_norm_fx_ind','bank_ass_credit_norm_fx_oth',
'bank_ass_credit_ovrd','bank_ass_credit_ovrd_mnt','bank_ass_credit_ovrd_mnt_pub',
'bank_ass_credit_ovrd_mnt_corp','bank_ass_credit_ovrd_mnt_ind','bank_ass_credit_ovrd_mnt_oth',
'bank_ass_credit_ovrd_fx','bank_ass_credit_ovrd_fx_pub','bank_ass_credit_ovrd_fx_corp',
'bank_ass_credit_ovrd_fx_ind','bank_ass_credit_ovrd_fx_oth','bank_ass_credit_npl','bank_ass_credit_npl_mnt',
'bank_ass_credit_npl_mnt_pub','bank_ass_credit_npl_mnt_corp','bank_ass_credit_npl_mnt_ind',
'bank_ass_credit_npl_mnt_oth','bank_ass_credit_npl_fx','bank_ass_credit_npl_fx_pub',
'bank_ass_credit_npl_fx_corp','bank_ass_credit_npl_fx_ind','bank_ass_credit_npl_fx_oth',
'bank_ass_credit_fi','bank_ass_credit_norm_fi','bank_ass_credit_norm_mnt_fi',
'bank_ass_credit_norm_fx_fi','bank_ass_credit_ovrd_fi','bank_ass_credit_ovrd_mnt_fi',
'bank_ass_credit_ovrd_fx_fi','bank_ass_credit_npl_fi','bank_ass_credit_npl_mnt_fi',
'bank_ass_credit_npl_fx_fi','bank_ass_credit_prov','bank_ass_oth_fi',
'bank_ass_oth_bank','bank_ass_der','bank_ass_estates','bank_ass_properties','bank_liab_tot','bank_liab_cur',
'bank_liab_cur_mnt','bank_liab_cur_fx','bank_liab_depo','bank_liab_depo_dem','bank_liab_depo_dem_mnt',
'bank_liab_depo_dem_fx','bank_liab_depo_time','bank_liab_depo_time_mnt','bank_liab_depo_time_fx','bank_liab_fi',
'bank_liab_oth_curdepo','bank_liab_mmarket','bank_liab_spec_depo','bank_liab_bank','bank_liab_cbank','bank_liab_fl',
'bank_liab_gov','bank_liab_der','bank_liab_oth_liab','bank_cap']

list_type = ['norm','ovrd','npl']
list_sector = ['ind','corp','pub','fi','oth']

for type in list_type:
     for sector in list_sector:
       dm['bank_ass_credit_' + type + '_' + sector] = dm['bank_ass_credit_' + type + '_mnt_' + sector] + dm['bank_ass_credit_' + type + '_fx_' + sector]
       bank_list = bank_list + ['bank_ass_credit_' + type + '_' + sector]

for sector in list_sector:
       dm['bank_ass_credit_' + sector] = dm['bank_ass_credit_norm_' + sector] + \
              dm['bank_ass_credit_ovrd_' + sector] + dm['bank_ass_credit_npl_' + sector]
       bank_list = bank_list + ['bank_ass_credit_' + sector]

for type in list_type:
       dm['bank_ass_credit_' + type] = dm['bank_ass_credit_' + type + '_pub'] + \
              dm['bank_ass_credit_' + type + '_corp'] + dm['bank_ass_credit_' + type + '_ind'] + dm['bank_ass_credit_' + type + '_oth']
       bank_list = bank_list + ['bank_ass_credit_' + type]

for currency in ['mnt','fx']:
       dm['bank_ass_credit_' + currency] = dm['bank_ass_credit_norm_' + currency] + \
             dm['bank_ass_credit_ovrd_' + currency] + dm['bank_ass_credit_npl_' + currency] 
       bank_list = bank_list + ['bank_ass_credit_' + currency]


for ind in bank_list:
     dq[ind] = convert(dm[ind].copy(),'q',method='average')


dm['gov_rev_eq'] = dm['gov_rev'] - dm['gov_rev_fut']- dm['gov_rev_stab']
dm['gov_exp_cur_subtran_nso'] = dm['gov_exp_cur_sub_nso']+dm['gov_exp_cur_transfer_gov_nso']+dm['gov_exp_cur_transfer_oth_nso']

budget_list = budget_list + ['gov_rev_eq','gov_exp_cur_subtran_nso']

for ind in budget_list + budget_list2:
     dq[ind] = convert(dm[ind].copy(),'q')
     dy[ind] = convert(dq[ind].copy(),'y')

dq['gdp_nom_y'] = dq['gdp_nom'].rolling(window=4, min_periods=1).sum()

# Create 2x2 sub plots
gs21 = gridspec.GridSpec(2, 1)
gs22 = gridspec.GridSpec(2, 2)


firstM = "05M01"
firstM_bop = "09M01"
firstQ = "05Q1"
firstQ_bop = "09Q1"
firstY = "05Y"
lastY = "22Y"

bop_list = ['bop_ca','bop_ca_gs','bop_ca_gs_cre','bop_ca_gs_deb','bop_ca_goods','bop_ca_goods_ex',
'bop_ca_goods_im','bop_ca_serv','bop_ca_serv_cre','bop_ca_serv_deb','bop_ca_prim','bop_ca_prim_cre',
'bop_ca_prim_deb','bop_ca_sec','bop_ca_sec_cre','bop_ca_sec_deb','bop_capa','bop_fa','bop_fa_di',
'bop_fa_pi','bop_fa_der','bop_fa_oth','bop_eo','bop']

for ind in bop_list:
       dq[ind] = convert(dm[ind],'q') 


dq['bop_fa_di'].loc[dq['bop_fa_di']>2000] = 1500
dq['bop_fa_oth'].loc[dq['bop_fa_oth']<-2000] = -1500


# trade to quarterly
for ind in exp_list + im_list:
     dq[ind] = convert(dm[ind],'q')
     dq[ind + '_vol'] = convert(dm[ind + '_vol'],'q')

for ind in trade_list:
     dq[ind] = convert(dm[ind].copy(),'q')

# Streamlit App
st.title("Macroeconomic Data Dashboard")

# Sidebar for user input
st.sidebar.header("Select Data")

# Create a list of available charts
available_charts = ["Real GDP Growth", "Nominal GDP Growth", "Exchange Rate", "Inflation"]

# Create a selectbox to choose the chart
selected_chart = st.sidebar.selectbox("Select Chart", available_charts)

# Display selected chart
if selected_chart == "Real GDP Growth":
    
    fig, ax = plt.subplots()
    plt.subplot(gs22[0,0])
    doPlot(line1 = pct(dq.gdp,-4),
        title = 'Real GDP growth (%, YoY), last: ' + get(dq.gdp,'last'),
        rng = [firstQ])
    plt.subplot(gs22[0,1])
    doPlot(line1 = pct(dq.gdp_nom,-4),
        title = 'Nominal GDP growth (%, YoY), last: ' + get(dq.gdp_nom,'last'),
        rng = [firstQ])
    plt.subplot(gs22[1,0])
    doPlot(line1 = dm["usd_mnt"],
        title = 'MNT/USD Exchange rate, last: ' + get(dm["usd_mnt"],'last'),
        rng   = [firstM])
    plt.xticks(fontsize=5)
    plt.subplot(gs22[1,1])
    doPlot(line1 = pct(dm["cpi"],-12),
        title = 'Inflation (%, YoY), last: ' + get(dm["cpi"],'last'),
        rng   = [firstM])
    plt.xticks(fontsize=5)
    plt.subplots_adjust(hspace=0.5)
    st.pyplot(fig)

elif selected_chart == "Nominal GDP Growth":
    st.subheader("Nominal GDP Growth (Quarterly)")
    fig, ax = plt.subplots()
    ax.plot(dq.index, pct(dq.gdp_nom, -4))
    ax.set_title('Nominal GDP Growth (%, YoY)')
    st.pyplot(fig)

elif selected_chart == "Exchange Rate":
    st.subheader("MNT/USD Exchange Rate (Monthly)")
    fig, ax = plt.subplots()
    ax.plot(dm.index, dm["usd_mnt"])
    ax.set_title('MNT/USD Exchange Rate')
    st.pyplot(fig)

elif selected_chart == "Inflation":
    st.subheader("Inflation (Monthly)")
    fig, ax = plt.subplots()
    ax.plot(dm.index, pct(dm["cpi"], -12))
    ax.set_title('Inflation (%, YoY)')
    st.pyplot(fig)

# You can add more charts and visualizations in a similar manner

# Data Table
st.subheader("Data Table")
st.write(dq)

# Additional features and visualizations can be added as needed

