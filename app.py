from __future__ import annotations

import hmac
import io
import pickle
import re
from pathlib import Path
from typing import Any
import os

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from auth_utils import verify_password


ROOT = Path(__file__).resolve().parent
DATA_PICKLE = ROOT / "data" / "macro_data.pickle"
FIGURE_DIR = ROOT / "figures"
REPORT_DIRS = [ROOT / "output", ROOT / "report" / "table"]
ANALYSIS_FORECAST_DIR = ROOT / "analysis_forecast"
FORECAST_REPORT_DIR = ANALYSIS_FORECAST_DIR / "reports"
HISTORICAL_FORECAST_DIR = ANALYSIS_FORECAST_DIR / "historical_forecasts"
FORECAST_DATABASE_DIR = ANALYSIS_FORECAST_DIR / "database"


MONTHLY_METRICS = [
    ("cpi_yoy", "Inflation YoY", "%", "pp"),
    ("usd_mnt", "USD/MNT", "", "MNT"),
    ("rate_pol", "Policy Rate", "%", "pp"),
    ("ms_m2_yoy", "M2 YoY", "%", "pp"),
    ("bank_ass_credit_nfi_yoy", "Credit YoY", "%", "pp"),
    ("fx_reserve", "FX Reserves", "bn USD", "bn USD"),
]

QUARTERLY_METRICS = [
    ("gdp_q4", "GDP 4Q YoY", "%", "pp"),
    ("hh_inc_yoy", "Household Income YoY", "%", "pp"),
    ("hh_exp_yoy", "Household Spending YoY", "%", "pp"),
    ("hh_exp_inc", "Income / Expense", "%", "pp"),
]

SAMPLE_ANALYSIS = {
    "2026M04": {
        "title": "April 2026 Macro Update",
        "date": "2026-05-10",
        "summary": "Inflation pressure picked up in April while external buffers remained adequate. Domestic demand indicators are still firm, but credit growth and food prices point to a less comfortable near-term inflation path.",
        "bullets": [
            "Headline CPI rose sharply in April, with food, transport, and insurance-related prices contributing to the monthly increase.",
            "The exchange rate remained broadly stable compared with the previous update, helping contain imported inflation outside volatile categories.",
            "Credit growth is still running above nominal GDP momentum, so financial conditions remain supportive for domestic demand.",
            "Fiscal execution should be watched closely as revenue growth normalizes and expenditure pressures remain visible.",
        ],
        "risks": [
            "Food price persistence could keep inflation expectations elevated.",
            "Commodity export volumes remain a key upside risk for growth and reserves.",
            "A faster credit cycle could complicate disinflation even if external conditions stay benign.",
        ],
    },
    "2026M03": {
        "title": "March 2026 Macro Update",
        "date": "2026-04-15",
        "summary": "Growth momentum stayed resilient in March, supported by trade and household income, while inflation was still above the comfort zone but less broad-based than earlier in the year.",
        "bullets": [
            "Real activity indicators were consistent with steady quarterly growth.",
            "FX reserves provided a useful buffer against external volatility.",
            "Loan growth remained concentrated in household and corporate segments sensitive to domestic demand.",
        ],
        "risks": [
            "External demand for key exports could soften.",
            "Inflation may become sticky if wage gains continue to outrun productivity.",
        ],
    },
}

SAMPLE_FORECASTS = {
    "Baseline": {
        "narrative": "The baseline assumes export volumes remain solid, policy rates decline only gradually, and inflation eases after the April food-price shock fades. Growth moderates toward potential while reserves remain broadly stable.",
        "table": [
            {"Indicator": "Real GDP growth", "2026": 5.8, "2027": 5.4, "2028": 5.2, "Unit": "%"},
            {"Indicator": "CPI inflation, eop", "2026": 7.9, "2027": 6.4, "2028": 5.8, "Unit": "%"},
            {"Indicator": "Policy rate, eop", "2026": 11.0, "2027": 9.5, "2028": 8.5, "Unit": "%"},
            {"Indicator": "Current account balance", "2026": -7.2, "2027": -6.5, "2028": -6.1, "Unit": "% GDP"},
            {"Indicator": "FX reserves", "2026": 5.9, "2027": 6.2, "2028": 6.5, "Unit": "bn USD"},
        ],
    },
    "Upside": {
        "narrative": "The upside scenario assumes stronger coal and copper exports, smoother food supply, and faster confidence recovery. Inflation falls earlier, creating room for easier financial conditions without destabilizing the currency.",
        "table": [
            {"Indicator": "Real GDP growth", "2026": 6.7, "2027": 6.1, "2028": 5.8, "Unit": "%"},
            {"Indicator": "CPI inflation, eop", "2026": 7.1, "2027": 5.6, "2028": 5.2, "Unit": "%"},
            {"Indicator": "Policy rate, eop", "2026": 10.5, "2027": 8.75, "2028": 8.0, "Unit": "%"},
            {"Indicator": "Current account balance", "2026": -5.9, "2027": -5.3, "2028": -5.0, "Unit": "% GDP"},
            {"Indicator": "FX reserves", "2026": 6.3, "2027": 6.9, "2028": 7.4, "Unit": "bn USD"},
        ],
    },
    "Downside": {
        "narrative": "The downside scenario combines weaker commodity demand, stickier food inflation, and tighter financial conditions. Growth slows, reserves are used more actively, and policy easing is delayed.",
        "table": [
            {"Indicator": "Real GDP growth", "2026": 4.6, "2027": 4.8, "2028": 5.0, "Unit": "%"},
            {"Indicator": "CPI inflation, eop", "2026": 9.4, "2027": 7.8, "2028": 6.6, "Unit": "%"},
            {"Indicator": "Policy rate, eop", "2026": 12.5, "2027": 11.0, "2028": 9.75, "Unit": "%"},
            {"Indicator": "Current account balance", "2026": -8.8, "2027": -8.0, "2028": -7.2, "Unit": "% GDP"},
            {"Indicator": "FX reserves", "2026": 5.3, "2027": 5.1, "2028": 5.4, "Unit": "bn USD"},
        ],
    },
}

MONTHLY_CHARTS = {
    "Prices": ["cpi_yoy", "cpi_qoq", "cpi_mom"],
    "Exchange Rates": ["usd_mnt", "cny_mnt", "usd_mnt_yoy", "cny_mnt_yoy"],
    "Rates": ["rate_pol", "rate_loan_mnt_new", "rate_timedepo_mnt_new"],
    "Money and Credit": [
        "ms_m2_yoy",
        "bank_ass_credit_nfi_yoy",
        "dc_loan_ind_yoy",
        "dc_loan_corp_yoy",
    ],
    "Fiscal": ["gov_rev_cum_yoy", "gov_exp_cum_yoy", "rev_gdp", "exp_gdp"],
    "Trade": ["ex_cum_yoy", "im_cum_yoy", "ex_gdp", "im_gdp"],
    "Coal": ["ex_coal_vol_cum", "ex_coal_cum", "ex_coal_p"],
}

QUARTERLY_CHARTS = {
    "GDP": ["gdp_q1", "gdp_q2", "gdp_q3", "gdp_q4"],
    "Households": ["hh_inc", "hh_exp_inc", "hh_inc_yoy", "hh_exp_yoy"],
}

MACRO_CHART_SECTIONS = {
    "Short Overview": ["short1.png", "short2.png", "short3.png"],
    "Real Economy": ["gdp1.png", "gdp2.png"],
    "Inflation and Prices": ["inf1.png", "inf2.png", "inf3.png", "inf4.png"],
    "Exchange Rate": ["fx1.png", "fx2.png"],
    "Balance of Payments and Trade": [
        "bop1.png",
        "bop2.png",
        "bop3.png",
        "trade1.png",
        "res1.png",
    ],
    "Interest Rates": ["ir1.png"],
    "Bank and Money Supply": [
        "ms1.png",
        "ms2.png",
        "ms3.png",
        "ms4.png",
        "bank1.png",
        "bank2.png",
        "bank3.png",
        "bank4.png",
        "bank5.png",
        "bank6.png",
    ],
    "Fiscal Sector": ["budget1.png", "budget2.png", "budget3.png", "budget4.png"],
    "Socio-economic": ["hh1.png", "hh2.png", "hh3.png"],
    "Tables": ["tab1.png"],
    "Other": ["mse1.png"],
}

MACRO_CHART_LABELS = {
    "short1.png": "Quick macro indicators",
    "short2.png": "External and fiscal snapshot",
    "short3.png": "Money, credit, and reserves",
    "gdp1.png": "Real GDP growth",
    "gdp2.png": "GDP by sector",
    "inf1.png": "Inflation overview",
    "inf2.png": "Inflation composition",
    "inf3.png": "Monthly inflation",
    "inf4.png": "Food and non-food prices",
    "fx1.png": "Exchange rates",
    "fx2.png": "Exchange rate changes",
    "bop1.png": "Current account",
    "bop2.png": "Balance of payments",
    "bop3.png": "Financial account",
    "trade1.png": "Foreign trade",
    "res1.png": "International reserves",
    "ir1.png": "Interest rates",
    "ms1.png": "Monetary base",
    "ms2.png": "Money supply",
    "ms3.png": "Money supply growth",
    "ms4.png": "Deposit growth",
    "bank1.png": "Banking sector assets",
    "bank2.png": "Banking sector liabilities",
    "bank3.png": "Credit structure",
    "bank4.png": "Credit and NPL",
    "bank5.png": "Corporate NPL ratios",
    "bank6.png": "Individual NPL ratios",
    "budget1.png": "Budget balance",
    "budget2.png": "Budget revenue",
    "budget3.png": "Budget expenditure",
    "budget4.png": "Expenditure composition",
    "hh1.png": "Household income and expenses",
    "hh2.png": "Monthly salary",
    "hh3.png": "Poverty and household balance",
    "tab1.png": "Macro indicator table",
    "mse1.png": "MSE TOP 20",
}

PLOTLY_MACRO_SECTIONS = {
    "Real Economy": [
        {
            "title": "Real Economy",
            "layout": "2x2",
            "charts": [
                {
                    "title": "Real GDP growth (YTD)",
                    "dataset": "Quarterly",
                    "unit": "%",
                    "bars": [
                        {"column": "gdp_ytd_agr_contrib", "label": "Agriculture"},
                        {"column": "gdp_ytd_mine_contrib", "label": "Mining"},
                        {"column": "gdp_ytd_manu_contrib", "label": "Manufacturing"},
                        {"column": "gdp_ytd_elec_contrib", "label": "Electricity"},
                        {"column": "gdp_ytd_cons_contrib", "label": "Construction"},
                        {"column": "gdp_ytd_trad_contrib", "label": "Trade"},
                        {"column": "gdp_ytd_tran_contrib", "label": "Transport"},
                        {"column": "gdp_ytd_comm_contrib", "label": "Communication"},
                        {"column": "gdp_ytd_serv_oth_contrib", "label": "Other services"},
                        {"column": "gdp_ytd_tax_contrib", "label": "Net taxes"},
                    ],
                    "lines": [
                        {"column": "gdp_ytd_growth", "label": "GDP growth"}
                    ],
                },
                {
                    "title": "Real GDP growth (quarter YoY)",
                    "dataset": "Quarterly",
                    "unit": "%",
                    "bars": [
                        {"column": "gdp_q_agr_contrib", "label": "Agriculture"},
                        {"column": "gdp_q_mine_contrib", "label": "Mining"},
                        {"column": "gdp_q_manu_contrib", "label": "Manufacturing"},
                        {"column": "gdp_q_elec_contrib", "label": "Electricity"},
                        {"column": "gdp_q_cons_contrib", "label": "Construction"},
                        {"column": "gdp_q_trad_contrib", "label": "Trade"},
                        {"column": "gdp_q_tran_contrib", "label": "Transport"},
                        {"column": "gdp_q_comm_contrib", "label": "Communication"},
                        {"column": "gdp_q_serv_oth_contrib", "label": "Other services"},
                        {"column": "gdp_q_tax_contrib", "label": "Net taxes"},
                    ],
                    "lines": [
                        {"column": "gdp_q_growth", "label": "GDP growth"}
                    ],
                },
                {
                    "title": "Real GDP growth (yearly)",
                    "dataset": "Yearly",
                    "unit": "%",
                    "bars": [
                        {"column": "gdp_y_agr_contrib", "label": "Agriculture"},
                        {"column": "gdp_y_mine_contrib", "label": "Mining"},
                        {"column": "gdp_y_manu_contrib", "label": "Manufacturing"},
                        {"column": "gdp_y_elec_contrib", "label": "Electricity"},
                        {"column": "gdp_y_cons_contrib", "label": "Construction"},
                        {"column": "gdp_y_trad_contrib", "label": "Trade"},
                        {"column": "gdp_y_tran_contrib", "label": "Transport"},
                        {"column": "gdp_y_comm_contrib", "label": "Communication"},
                        {"column": "gdp_y_serv_oth_contrib", "label": "Other services"},
                        {"column": "gdp_y_tax_contrib", "label": "Net taxes"},
                    ],
                    "lines": [
                        {"column": "gdp_y_growth", "label": "GDP growth"}
                    ],
                },
                {
                    "title": "Real GDP decomposition (shares)",
                    "dataset": "Yearly",
                    "unit": "%",
                    "bars": [
                        {"column": "gdp_agr_share", "label": "Agriculture"},
                        {"column": "gdp_mine_share", "label": "Mining"},
                        {"column": "gdp_manu_share", "label": "Manufacturing"},
                        {"column": "gdp_elec_share", "label": "Electricity"},
                        {"column": "gdp_cons_share", "label": "Construction"},
                        {"column": "gdp_trad_share", "label": "Trade"},
                        {"column": "gdp_tran_share", "label": "Transport"},
                        {"column": "gdp_comm_share", "label": "Communication"},
                        {"column": "gdp_serv_oth_share", "label": "Other services"},
                        {"column": "gdp_tax_share", "label": "Net taxes"},
                    ],
                },
            ],
        },
        {
            "title": "Nominal GDP",
            "dataset": "Yearly",
            "unit": "tn MNT / bn USD",
            "lines": [
                {"column": "gdp_nom_tn", "label": "MNT, tn"},
                {"column": "gdp_nom_usd", "label": "USD, bn"},
            ],
        },
    ],
    "Inflation and Prices": [
        {
            "title": "Headline Inflation",
            "dataset": "Monthly",
            "unit": "%",
            "lines": [
                {"column": "cpi", "label": "YoY", "transform": "yoy", "lag": 12},
                {"column": "cpi", "label": "MoM", "transform": "pct_change", "lag": 1},
                {"column": "cpi", "label": "3-month annualized", "transform": "annualized_pct_change", "lag": 3, "annualizer": 4},
            ],
        },
        {
            "title": "Inflation by Main Components",
            "dataset": "Monthly",
            "unit": "%",
            "lines": [
                {"column": "cpi_food", "label": "Food", "transform": "yoy", "lag": 12},
                {"column": "cpi_nonfood", "label": "Non-food", "transform": "yoy", "lag": 12},
                {"column": "cpi", "label": "Headline", "transform": "yoy", "lag": 12},
            ],
        },
        {
            "title": "Selected CPI Components",
            "dataset": "Monthly",
            "unit": "%",
            "lines": [
                {"column": "cpi_food", "label": "Food", "transform": "yoy", "lag": 12},
                {"column": "cpi_tran", "label": "Transport", "transform": "yoy", "lag": 12},
                {"column": "cpi_hote", "label": "Restaurants and hotels", "transform": "yoy", "lag": 12},
                {"column": "cpi_educ", "label": "Education", "transform": "yoy", "lag": 12},
            ],
        },
    ],
    "Exchange Rate": [
        {
            "title": "Exchange Rates",
            "dataset": "Monthly",
            "lines": [
                {"column": "usd_mnt", "label": "USD/MNT"},
                {"column": "cny_mnt", "label": "CNY/MNT"},
                {"column": "rub_mnt", "label": "RUB/MNT"},
                {"column": "eur_mnt", "label": "EUR/MNT"},
            ],
        },
        {
            "title": "Exchange Rate Changes",
            "dataset": "Monthly",
            "unit": "%",
            "lines": [
                {"column": "usd_mnt", "label": "USD/MNT YoY", "transform": "yoy", "lag": 12},
                {"column": "cny_mnt", "label": "CNY/MNT YoY", "transform": "yoy", "lag": 12},
                {"column": "usd_mnt", "label": "USD/MNT MoM", "transform": "pct_change", "lag": 1},
            ],
        },
    ],
    "Balance of Payments and Trade": [
        {
            "title": "Current Account",
            "dataset": "Quarterly",
            "unit": "mn USD",
            "bars": [
                {"column": "bop_ca_goods", "label": "Goods"},
                {"column": "bop_ca_serv", "label": "Services"},
                {"column": "bop_ca_prim", "label": "Primary income"},
                {"column": "bop_ca_sec", "label": "Secondary income"},
            ],
            "lines": [{"column": "bop_ca", "label": "Current account"}],
        },
        {
            "title": "Balance of Payments",
            "dataset": "Quarterly",
            "unit": "mn USD",
            "bars": [
                {"column": "bop_ca", "label": "Current account"},
                {"column": "bop_capa", "label": "Capital account"},
                {"column": "bop_fa", "label": "Financial account"},
                {"column": "bop_eo", "label": "Errors and omissions"},
            ],
            "lines": [{"column": "bop", "label": "Overall balance"}],
        },
        {
            "title": "Trade and Reserves",
            "dataset": "Monthly",
            "lines": [
                {"column": "ex_cum", "label": "Exports, bn USD", "scale": 0.001},
                {"column": "im_cum", "label": "Imports, bn USD", "scale": 0.001},
                {"column": "fx_reserve", "label": "FX reserves, bn USD", "scale": 0.001},
            ],
        },
        {
            "title": "Coal Exports",
            "dataset": "Monthly",
            "lines": [
                {"column": "ex_coal_vol_cum", "label": "Volume, mn tons", "scale": 0.001},
                {"column": "ex_coal_cum", "label": "Revenue, bn USD", "scale": 0.000001},
                {"column": "ex_coal_p", "label": "Price, USD/ton"},
            ],
        },
    ],
    "Interest Rates": [
        {
            "title": "Policy, Lending, and Deposit Rates",
            "dataset": "Monthly",
            "unit": "%",
            "lines": [
                {"column": "rate_pol", "label": "Policy rate"},
                {"column": "rate_loan_mnt_new", "label": "New MNT loans"},
                {"column": "rate_timedepo_mnt_new", "label": "New MNT time deposits"},
            ],
        },
        {
            "title": "Money Market Rates",
            "dataset": "Monthly",
            "unit": "%",
            "lines": [
                {"column": "rate_ib_on", "label": "Interbank overnight"},
                {"column": "rate_ib_depo", "label": "Interbank deposits"},
                {"column": "rate_cbb_4w", "label": "CBB 4w"},
                {"column": "rate_gb_12w", "label": "Government bills 12w"},
            ],
        },
    ],
    "Bank and Money Supply": [
        {
            "title": "Money Supply Growth",
            "dataset": "Monthly",
            "unit": "%",
            "lines": [
                {"column": "cb_mbase", "label": "Monetary base", "transform": "yoy", "lag": 12},
                {"column": "ms_m1", "label": "M1", "transform": "yoy", "lag": 12},
                {"column": "ms_m2", "label": "M2", "transform": "yoy", "lag": 12},
            ],
        },
        {
            "title": "Money Supply Level",
            "dataset": "Monthly",
            "unit": "tn MNT",
            "bars": [
                {"column": "ms_cashout", "label": "Currency outside banks", "scale": 0.000001},
                {"column": "ms_m2_dep_ca_dc", "label": "Current accounts LCY", "scale": 0.000001},
                {"column": "ms_dep_mnt", "label": "Time deposits LCY", "scale": 0.000001},
                {"column": "ms_ca_fx", "label": "Current accounts FCY", "scale": 0.000001},
                {"column": "ms_dep_fx", "label": "Time deposits FCY", "scale": 0.000001},
            ],
            "lines": [{"column": "ms_m2", "label": "M2", "scale": 0.000001}],
        },
        {
            "title": "Credit Growth",
            "dataset": "Monthly",
            "unit": "%",
            "lines": [
                {"column": "bank_ass_credit_nfi", "label": "Total credit", "transform": "yoy", "lag": 12},
                {"column": "dc_loan_corp", "label": "Corporate loans", "transform": "yoy", "lag": 12},
                {"column": "dc_loan_ind", "label": "Individual loans", "transform": "yoy", "lag": 12},
            ],
        },
        {
            "title": "Credit Structure",
            "dataset": "Quarterly",
            "unit": "tn MNT",
            "bars": [
                {"column": "bank_ass_credit_norm", "label": "Standard", "scale": 0.000001},
                {"column": "bank_ass_credit_ovrd", "label": "Overdue", "scale": 0.000001},
                {"column": "bank_ass_credit_npl", "label": "NPL", "scale": 0.000001},
            ],
            "lines": [{"column": "bank_ass_credit_nfi", "label": "Total credit", "scale": 0.000001}],
        },
        {
            "title": "NPL Ratios",
            "dataset": "Monthly",
            "unit": "%",
            "lines": [
                {"column": "bank_ass_credit_npl", "denominator": "bank_ass_credit_nfi", "label": "Total NPL ratio", "transform": "ratio"},
                {"column": "bank_ass_credit_npl_corp", "denominator": "bank_ass_credit_corp", "label": "Corporate NPL ratio", "transform": "ratio"},
                {"column": "bank_ass_credit_npl_ind", "denominator": "bank_ass_credit_ind", "label": "Individual NPL ratio", "transform": "ratio"},
            ],
        },
    ],
    "Fiscal Sector": [
        {
            "title": "Budget Balance",
            "dataset": "Quarterly",
            "unit": "tn MNT",
            "bars": [
                {"column": "gov_rev_eq", "label": "Revenue", "scale": 0.001},
                {"column": "gov_exp", "label": "Expenditure", "scale": -0.001},
            ],
            "lines": [
                {"columns_sum": ["gov_rev_eq"], "minus_columns": ["gov_exp"], "label": "Balance", "scale": 0.001}
            ],
        },
        {
            "title": "Fiscal Ratios",
            "dataset": "Quarterly",
            "unit": "% of GDP",
            "lines": [
                {"column": "gov_rev_eq", "denominator": "gdp_nom_y", "label": "Revenue / GDP", "transform": "ratio", "scale": 1000},
                {"column": "gov_exp", "denominator": "gdp_nom_y", "label": "Expenditure / GDP", "transform": "ratio", "scale": 1000},
            ],
        },
        {
            "title": "Budget Growth",
            "dataset": "Monthly",
            "unit": "%",
            "lines": [
                {"column": "gov_rev_cum", "label": "Revenue YoY", "transform": "yoy", "lag": 12},
                {"column": "gov_exp_cum", "label": "Expenditure YoY", "transform": "yoy", "lag": 12},
            ],
        },
    ],
    "Socio-economic and Other": [
        {
            "title": "Wages and Household Budget",
            "dataset": "Quarterly",
            "unit": "%",
            "lines": [
                {"column": "wage_avg", "label": "Average wage YoY", "transform": "yoy", "lag": 4},
                {"column": "wage_median", "label": "Median wage YoY", "transform": "yoy", "lag": 4},
                {"column": "hh_inc", "label": "Household income YoY", "transform": "yoy", "lag": 4},
                {"column": "hh_exp", "label": "Household spending YoY", "transform": "yoy", "lag": 4},
            ],
        },
        {
            "title": "MSE TOP 20",
            "dataset": "Monthly",
            "lines": [
                {"column": "mse_top20_avg", "label": "Index"},
                {"column": "mse_top20_avg", "label": "YoY change, %", "transform": "yoy", "lag": 12},
            ],
        },
    ],
}

DATASET_DEFAULTS = {
    "Monthly": ["cpi", "usd_mnt", "rate_pol", "ms_m2", "bank_ass_credit_nfi"],
    "Quarterly": ["gdp", "gdp_nom", "hh_inc", "hh_exp"],
    "Yearly": ["gdp", "gdp_nom", "usd_mnt_avg", "cpi_last"],
    "Daily": ["mnt_usd"],
}

LABEL_OVERRIDES = {
    "cpi_yoy": "Inflation YoY",
    "cpi_qoq": "Inflation QoQ annualized",
    "cpi_mom": "Inflation MoM",
    "usd_mnt": "USD/MNT",
    "usd_mnt_yoy": "USD/MNT YoY",
    "usd_mnt_qoq": "USD/MNT QoQ annualized",
    "usd_mnt_mom": "USD/MNT MoM",
    "cny_mnt": "CNY/MNT",
    "cny_mnt_yoy": "CNY/MNT YoY",
    "rate_pol": "Policy rate",
    "rate_loan_mnt_new": "New MNT loan rate",
    "rate_timedepo_mnt_new": "New MNT time deposit rate",
    "ms_m2": "M2",
    "ms_m2_yoy": "M2 YoY",
    "m2_gdp": "M2 / GDP",
    "bank_ass_credit_nfi": "Credit to non-financial sector",
    "bank_ass_credit_nfi_yoy": "Credit YoY",
    "dc_loan_ind_yoy": "Individual loan YoY",
    "dc_loan_corp_yoy": "Corporate loan YoY",
    "loan_gdp": "Credit / GDP",
    "gov_rev_cum_yoy": "Budget revenue YoY",
    "gov_exp_cum_yoy": "Budget expenditure YoY",
    "rev_gdp": "Budget revenue / GDP",
    "exp_gdp": "Budget expenditure / GDP",
    "ex_cum_yoy": "Exports YoY",
    "im_cum_yoy": "Imports YoY",
    "ex_gdp": "Exports / GDP",
    "im_gdp": "Imports / GDP",
    "fx_reserve": "FX reserves",
    "ex_coal_vol_cum": "Coal export volume",
    "ex_coal_cum": "Coal export revenue",
    "ex_coal_p": "Coal export price",
    "gdp_q1": "GDP YoY, latest quarter",
    "gdp_q2": "GDP YoY, 2-quarter sum",
    "gdp_q3": "GDP YoY, 3-quarter sum",
    "gdp_q4": "GDP YoY, 4-quarter sum",
    "hh_inc": "Household income",
    "hh_exp_inc": "Household income / expense",
    "hh_inc_yoy": "Household income YoY",
    "hh_exp_yoy": "Household expense YoY",
}

SECTOR_COLORS = {
    "Agriculture": "#2ca02c",
    "Mining": "#ff7f0e",
    "Manufacturing": "#1f77b4",
    "Electricity": "#9467bd",
    "Construction": "#8c564b",
    "Trade": "#e377c2",
    "Transport": "#7f7f7f",
    "Communication": "#bcbd22",
    "Other services": "#17becf",
    "Net taxes": "#d62728",
}

LINE_COLORS = {
    "GDP growth": "#111827",
}



def main() -> None:
    st.set_page_config(
        page_title="Mongolian Macroeconomic Dashboard",
        page_icon="MN",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_css()
    user = require_login()

    macro_data = load_macro_data(str(DATA_PICKLE), file_mtime(DATA_PICKLE))
    indicator_frames = build_indicator_frames(macro_data)
    monthly_ts = indicator_frames.get("m", pd.DataFrame())
    quarterly_ts = indicator_frames.get("q", pd.DataFrame())
    indicator_tables = build_indicator_tables(monthly_ts, quarterly_ts)

    render_header(macro_data, monthly_ts, quarterly_ts, user)

    overview_tab, updates_tab, forecast_tab, explorer_tab, archive_tab = st.tabs(
        ["Overview", "Updates", "Forecasts", "Data Explorer", "Archive"]
    )

    with overview_tab:
        render_overview(macro_data, monthly_ts, quarterly_ts)

    with updates_tab:
        render_updates_section()

    with forecast_tab:
        render_forecast_section()

    with explorer_tab:
        render_data_explorer(macro_data)

    with archive_tab:
        render_archive(indicator_tables)


def require_login() -> dict[str, str]:
    if os.getenv("STREAMLIT_RUNTIME") != "cloud":
        return {
            "email": "local",
            "name": "Local User",
            "role": "admin",
        }

    users = load_auth_users()

    if not users:
        render_auth_setup()
        st.stop()

    if st.session_state.get("authenticated"):
        return {
            "email": st.session_state.get("email", ""),
            "name": st.session_state.get("display_name", "User"),
            "role": st.session_state.get("role", "viewer"),
        }

    st.title("Mongolian Macroeconomic Dashboard")
    left, middle, right = st.columns([1, 1.1, 1])
    with middle:
        st.subheader("Sign in")
        with st.form("login_form", clear_on_submit=False):
            email = st.text_input("Email").strip().lower()
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button(
                "Sign in",
                type="primary",
                use_container_width=True,
            )

        if submitted:
            matched_email, user_config = find_user(email, users)
            if matched_email and password_is_valid(password, user_config):
                st.session_state["authenticated"] = True
                st.session_state["email"] = matched_email
                st.session_state["display_name"] = str(
                    user_config.get("name") or matched_email
                )
                st.session_state["role"] = str(user_config.get("role") or "viewer")
                st.rerun()
            st.error("Invalid email or password.")

    st.stop()


def render_auth_setup() -> None:
    st.title("Mongolian Macroeconomic Dashboard")
    st.warning("Access is not configured yet.")
    st.markdown(
        """
Create `.streamlit/secrets.toml` from `.streamlit/secrets.toml.example`,
then add at least one allowed user with a password hash.

Generate a password hash with:

```powershell
python tools/create_password_hash.py
```
"""
    )


def load_auth_users() -> dict[str, dict[str, Any]]:
    try:
        auth_config = st.secrets.get("auth", {})
    except Exception:
        return {}

    users = safe_dict(auth_config).get("users", {})
    return {
        str(email).lower(): safe_dict(config)
        for email, config in safe_dict(users).items()
    }


def safe_dict(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    try:
        return dict(value)
    except (TypeError, ValueError):
        return {}


def find_user(
    submitted_email: str,
    users: dict[str, dict[str, Any]],
) -> tuple[str | None, dict[str, Any]]:
    normalized = submitted_email.strip().lower()
    for email, config in users.items():
        if email.lower() == normalized:
            return email, config
    return None, {}


def password_is_valid(password: str, user_config: dict[str, Any]) -> bool:
    password_hash = str(user_config.get("password_hash") or "")
    if password_hash:
        return verify_password(password, password_hash)

    plaintext_password = str(user_config.get("password") or "")
    if plaintext_password:
        return hmac.compare_digest(password, plaintext_password)

    return False


def sign_out() -> None:
    for key in ("authenticated", "email", "display_name", "role"):
        st.session_state.pop(key, None)


def inject_css() -> None:
    st.markdown(
        """
<style>
    details summary p {
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.04em;
    }
    header,
    footer,
    #MainMenu,
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"] {
        visibility: hidden;
        height: 0;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    [data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #e4e8ee;
        border-radius: 8px;
        padding: 0.85rem 0.95rem;
    }
    [data-testid="stMetricLabel"] p {
        color: #425466;
        font-size: 0.86rem;
    }
    [data-testid="stMetricValue"] {
        color: #1f2a37;
        font-size: 1.45rem;
    }
    div[data-testid="stTabs"] button p {
        font-size: 0.95rem;
    }
    .small-muted {
        color: #667085;
        font-size: 0.9rem;
    }
    div[data-testid="stDialog"] div[role="dialog"] {
        width: min(96vw, 1500px);
        max-width: 96vw;
    }
    div[data-testid="stDialog"] div[role="dialog"] > div {
        max-height: 92vh;
    }
</style>
""",
        unsafe_allow_html=True,
    )


def file_mtime(path: Path) -> float:
    return path.stat().st_mtime if path.exists() else 0.0


@st.cache_data(show_spinner=False)
def load_macro_data(path: str, _mtime: float) -> dict[str, pd.DataFrame]:
    data_path = Path(path)
    if not data_path.exists():
        return {}

    with data_path.open("rb") as handle:
        daily, monthly, quarterly, yearly = pickle.load(handle)

    return {
        "Monthly": monthly,
        "Quarterly": quarterly,
        "Yearly": yearly,
        "Daily": daily,
    }


def build_indicator_frames(macro_data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    monthly = build_monthly_indicator_frame(
        macro_data.get("Monthly", pd.DataFrame()),
        macro_data.get("Quarterly", pd.DataFrame()),
    )
    quarterly = build_quarterly_indicator_frame(macro_data.get("Quarterly", pd.DataFrame()))
    return {"m": monthly, "q": quarterly}


def build_monthly_indicator_frame(dm: pd.DataFrame, dq: pd.DataFrame) -> pd.DataFrame:
    if dm is None or dm.empty:
        return pd.DataFrame()

    frame = pd.DataFrame(index=dm.index.astype(str))
    add_existing_columns(
        frame,
        dm,
        [
            "cpi",
            "usd_mnt",
            "cny_mnt",
            "rate_pol",
            "rate_loan_mnt_new",
            "rate_timedepo_mnt_new",
            "ex_coal_p",
        ],
    )

    if "cpi" in dm:
        frame["cpi_yoy"] = pct_change(dm["cpi"], 12)
        frame["cpi_qoq"] = pct_change(dm["cpi"], 3) * 4
        frame["cpi_mom"] = pct_change(dm["cpi"], 1)

    for currency in ("usd_mnt", "cny_mnt"):
        if currency in dm:
            frame[f"{currency}_yoy"] = pct_change(dm[currency], 12)
            frame[f"{currency}_qoq"] = pct_change(dm[currency], 3) * 4
            frame[f"{currency}_mom"] = pct_change(dm[currency], 1)

    for column in ("ms_m2", "bank_ass_credit_nfi", "dc_loan_ind", "dc_loan_corp"):
        if column in dm:
            frame[column] = pd.to_numeric(dm[column], errors="coerce") / 1e6
            frame[f"{column}_yoy"] = pct_change(dm[column], 12)
            frame[f"{column}_qoq"] = pct_change(dm[column], 3) * 4
            frame[f"{column}_mom"] = pct_change(dm[column], 1)

    gdp_nom_y = monthly_gdp_nom_y(dq, frame.index)
    if gdp_nom_y is not None:
        if "ms_m2" in dm:
            frame["m2_gdp"] = pd.to_numeric(dm["ms_m2"], errors="coerce").reindex(frame.index).div(gdp_nom_y) * 100
        if "bank_ass_credit_nfi" in dm:
            frame["loan_gdp"] = pd.to_numeric(dm["bank_ass_credit_nfi"], errors="coerce").reindex(frame.index).div(gdp_nom_y) * 100
        if "dc_loan_ind" in dm:
            frame["loan_ind_gdp"] = pd.to_numeric(dm["dc_loan_ind"], errors="coerce").reindex(frame.index).div(gdp_nom_y) * 100
        if "dc_loan_corp" in dm:
            frame["loan_corp_gdp"] = pd.to_numeric(dm["dc_loan_corp"], errors="coerce").reindex(frame.index).div(gdp_nom_y) * 100
        if "gov_rev_cum" in dm:
            frame["rev_gdp"] = pd.to_numeric(dm["gov_rev_cum"], errors="coerce").reindex(frame.index).div(gdp_nom_y) * 100
        if "gov_exp_cum" in dm:
            frame["exp_gdp"] = pd.to_numeric(dm["gov_exp_cum"], errors="coerce").reindex(frame.index).div(gdp_nom_y) * 100
        if "ex_cum" in dm and "usd_mnt" in dm:
            frame["ex_gdp"] = (
                pd.to_numeric(dm["ex_cum"], errors="coerce")
                .mul(pd.to_numeric(dm["usd_mnt"], errors="coerce"))
                .reindex(frame.index)
                .div(gdp_nom_y)
                * 100
            )
        if "im_cum" in dm and "usd_mnt" in dm:
            frame["im_gdp"] = (
                pd.to_numeric(dm["im_cum"], errors="coerce")
                .mul(pd.to_numeric(dm["usd_mnt"], errors="coerce"))
                .reindex(frame.index)
                .div(gdp_nom_y)
                * 100
            )

    for column in ("gov_rev_cum", "gov_exp_cum"):
        if column in dm:
            frame[column] = pd.to_numeric(dm[column], errors="coerce") / 1e6
            frame[f"{column}_yoy"] = pct_change(dm[column], 12)

    for column in ("ex_cum", "im_cum"):
        if column in dm:
            frame[column] = pd.to_numeric(dm[column], errors="coerce") / 1e3
            frame[f"{column}_yoy"] = pct_change(dm[column], 12)

    if "fx_reserve" in dm:
        frame["fx_reserve"] = pd.to_numeric(dm["fx_reserve"], errors="coerce") / 1e3
    if "ex_coal_vol_cum" in dm:
        frame["ex_coal_vol_cum"] = pd.to_numeric(dm["ex_coal_vol_cum"], errors="coerce") / 1e3
    if "ex_coal_cum" in dm:
        frame["ex_coal_cum"] = pd.to_numeric(dm["ex_coal_cum"], errors="coerce") / 1e6

    return frame.apply(pd.to_numeric, errors="coerce")


def build_quarterly_indicator_frame(dq: pd.DataFrame) -> pd.DataFrame:
    if dq is None or dq.empty:
        return pd.DataFrame()

    frame = pd.DataFrame(index=dq.index.astype(str))
    if "gdp" in dq:
        gdp = pd.to_numeric(dq["gdp"], errors="coerce")
        frame["gdp_q1"] = pct_change(gdp, 4)
        frame["gdp_q2"] = pct_change(gdp.rolling(window=2, min_periods=1).sum(), 4)
        frame["gdp_q3"] = pct_change(gdp.rolling(window=3, min_periods=1).sum(), 4)
        frame["gdp_q4"] = pct_change(gdp.rolling(window=4, min_periods=1).sum(), 4)

    add_existing_columns(frame, dq, ["hh_inc", "hh_exp"])
    if "hh_inc" in dq and "hh_exp" in dq:
        frame["hh_exp_inc"] = pd.to_numeric(dq["hh_inc"], errors="coerce").div(pd.to_numeric(dq["hh_exp"], errors="coerce")) * 100
        frame["hh_inc_yoy"] = pct_change(dq["hh_inc"], 4)
        frame["hh_exp_yoy"] = pct_change(dq["hh_exp"], 4)

    return frame.apply(pd.to_numeric, errors="coerce")


def build_indicator_tables(monthly_ts: pd.DataFrame, quarterly_ts: pd.DataFrame) -> dict[str, pd.DataFrame]:
    tables: dict[str, pd.DataFrame] = {}
    if not monthly_ts.empty:
        tables["m"] = monthly_ts.tail(50).transpose()
    if not quarterly_ts.empty:
        tables["q"] = quarterly_ts.tail(18).transpose()
    return tables


def add_existing_columns(target: pd.DataFrame, source: pd.DataFrame, columns: list[str]) -> None:
    for column in columns:
        if column in source:
            target[column] = pd.to_numeric(source[column], errors="coerce")


def pct_change(series: pd.Series, lag: int) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").pct_change(lag, fill_method=None) * 100


def monthly_gdp_nom_y(dq: pd.DataFrame, monthly_index: pd.Index) -> pd.Series | None:
    if dq is None or dq.empty or "gdp_nom" not in dq:
        return None

    gdp_nom = pd.to_numeric(dq["gdp_nom"], errors="coerce").dropna()
    if gdp_nom.empty:
        return None

    parsed_quarters = [parse_period(index_value) for index_value in gdp_nom.index]
    if any(pd.isna(value) for value in parsed_quarters):
        return None

    quarterly = pd.Series(gdp_nom.values, index=pd.DatetimeIndex(parsed_quarters)).sort_index()
    try:
        monthly = quarterly.resample("ME").ffill() / 3
    except ValueError:
        monthly = quarterly.resample("M").ffill() / 3
    monthly_periods = monthly.index.year.astype(str).str[-2:] + "M" + monthly.index.month.astype(str).str.zfill(2)
    monthly.index = monthly_periods
    monthly = monthly.reindex(monthly_index).ffill()
    return monthly.rolling(window=12, min_periods=12).sum()


def render_header(
    macro_data: dict[str, pd.DataFrame],
    monthly_ts: pd.DataFrame,
    quarterly_ts: pd.DataFrame,
    user: dict[str, str],
) -> None:
    title_col, action_col = st.columns([5, 1])
    with title_col:
        st.title("Mongolian Macroeconomic Dashboard")
    with action_col:
        st.caption(f"Signed in as {user['name']}")
        if st.button("Sign out", use_container_width=True):
            sign_out()
            st.rerun()

    monthly_latest = latest_index(monthly_ts)
    quarterly_latest = latest_index(quarterly_ts)
    raw_latest = {
        name: latest_index(frame)
        for name, frame in macro_data.items()
        if isinstance(frame, pd.DataFrame) and not frame.empty
    }

    caption_parts = []
    if monthly_latest:
        caption_parts.append(f"monthly indicators through {monthly_latest}")
    if quarterly_latest:
        caption_parts.append(f"quarterly indicators through {quarterly_latest}")
    if not caption_parts and raw_latest:
        caption_parts.extend(f"{name.lower()} through {period}" for name, period in raw_latest.items())

    st.caption(" | ".join(caption_parts) if caption_parts else "No data files found.")


def latest_index(frame: pd.DataFrame) -> str:
    if frame is None or frame.empty:
        return ""
    clean = frame.dropna(how="all")
    if clean.empty:
        return ""
    return str(clean.index[-1])


def render_overview(
    macro_data: dict[str, pd.DataFrame],
    monthly_ts: pd.DataFrame,
    quarterly_ts: pd.DataFrame,
) -> None:
    if monthly_ts.empty and quarterly_ts.empty:
        st.warning("No derived indicators found. Run `code/macro_charts.py` to rebuild `data/macro_data.pickle`.")
        return

    if not monthly_ts.empty:
        st.subheader("Monthly Snapshot")
        render_metric_grid(monthly_ts, MONTHLY_METRICS)

    if not quarterly_ts.empty:
        st.subheader("Quarterly Snapshot")
        render_metric_grid(quarterly_ts, QUARTERLY_METRICS)

    render_plotly_macro_sections(macro_data)

    # with st.expander("Interactive Indicator Trends", expanded=False):
    #     if not monthly_ts.empty:
    #         render_chart_section("Monthly Trends", monthly_ts, MONTHLY_CHARTS, default_observations=60)
    #     if not quarterly_ts.empty:
    #         render_chart_section("Quarterly Trends", quarterly_ts, QUARTERLY_CHARTS, default_observations=36)


def render_plotly_macro_sections(macro_data: dict[str, pd.DataFrame]) -> None:
    st.subheader("Macro Charts")

    if not macro_data:
        st.info("No macro dataset found. Run the data pipeline to create `data/macro_data.pickle`.")
        return

    control_cols = st.columns([1, 1, 2])
    monthly_window = control_cols[0].slider(
        "Monthly periods",
        min_value=12,
        max_value=180,
        value=72,
        step=6,
    )
    quarterly_window = control_cols[1].slider(
        "Quarterly periods",
        min_value=8,
        max_value=80,
        value=40,
        step=4,
    )
    expand_all = control_cols[2].checkbox("Expand all macro chart sections", value=False)

    windows = {
        "Monthly": int(monthly_window),
        "Quarterly": int(quarterly_window),
        "Yearly": 30,
        "Daily": 365,
    }

    for index, (section_name, chart_specs) in enumerate(PLOTLY_MACRO_SECTIONS.items()):

        with st.expander(
            section_name.upper(),
            expanded=expand_all or index == 0,
        ):
            for chart_index, chart_spec in enumerate(chart_specs):
                if chart_index:
                    st.divider()
                chart_key_prefix = f"{index}_{chart_index}_{slugify(section_name)}"
                if chart_spec.get("layout") == "2x2":
                    render_macro_plotly_page(macro_data, chart_spec, windows, chart_key_prefix)
                else:
                    render_macro_plotly_chart(macro_data, chart_spec, windows, chart_key_prefix)


def render_macro_plotly_page(
    macro_data: dict[str, pd.DataFrame],
    page_spec: dict[str, Any],
    windows: dict[str, int],
    key_prefix: str,
) -> None:
    charts = list(page_spec.get("charts", []))[:4]
    if not charts:
        return

    has_chart = False
    for row_start in range(0, len(charts), 2):
        columns = st.columns(2)
        for offset, chart_spec in enumerate(charts[row_start : row_start + 2]):
            index = row_start + offset
            with columns[offset]:
                single = build_macro_plotly_chart_figure(
                    macro_data,
                    chart_spec,
                    windows,
                    height=410,
                    title_size=14,
                    legend_y=-0.34,
                )
                if single is None:
                    continue
                has_chart = True
                fig, chart_title = single
                render_expandable_plotly(
                    fig,
                    key=f"macro_plotly_page_{key_prefix}_{index}",
                    title=chart_title,
                    expanded_height=860,
                    compact=True,
                )

    if not has_chart:
        st.info(f"No available series for {page_spec.get('title', 'this page')}.")


def render_macro_plotly_chart(
    macro_data: dict[str, pd.DataFrame],
    chart_spec: dict[str, Any],
    windows: dict[str, int],
    key_prefix: str,
) -> None:
    built = build_macro_plotly_chart_figure(macro_data, chart_spec, windows)
    if built is None:
        st.info(f"No available series for {chart_spec.get('title', 'this chart')}.")
        return

    fig, chart_title = built
    chart_key = f"macro_plotly_{key_prefix}"
    render_expandable_plotly(
        fig,
        key=chart_key,
        title=chart_title,
        expanded_height=760,
    )


def build_macro_plotly_chart_figure(
    macro_data: dict[str, pd.DataFrame],
    chart_spec: dict[str, Any],
    windows: dict[str, int],
    height: int = 360,
    title_size: int = 15,
    legend_y: float = -0.36,
) -> tuple[go.Figure, str] | None:
    dataset_name = str(chart_spec.get("dataset", "Monthly"))
    frame = macro_data.get(dataset_name)
    if frame is None or frame.empty:
        return None

    bars = build_chart_series(frame, chart_spec.get("bars", []))
    lines = build_chart_series(frame, chart_spec.get("lines", []))
    all_series = bars + lines
    if not all_series:
        return None

    observations = int(chart_spec.get("observations") or windows.get(dataset_name, 60))
    chart_frame = pd.concat({label: series for label, series in all_series}, axis=1)
    chart_frame = chart_frame.apply(pd.to_numeric, errors="coerce").dropna(how="all").tail(observations)

    if str(chart_spec.get("title", "")) == "Real GDP decomposition (shares)":
        bar_labels = [label for label, _series in bars]
        bar_totals = chart_frame[bar_labels].sum(axis=1, min_count=1)

        chart_frame[bar_labels] = (
            chart_frame[bar_labels]
            .div(bar_totals.replace(0, pd.NA), axis=0)
            * 100
        )

    if chart_frame.empty:
        return None

    chart_title = title_with_last_period(str(chart_spec.get("title", "")), all_series)
    x_values, x_title = chart_x_values(chart_frame.index)
    fig = go.Figure()

    for label, _series in bars:
        fig.add_trace(
            go.Bar(
                x=x_values,
                y=chart_frame[label],
                name=label,
                marker_color=SECTOR_COLORS.get(label),
            )
        )

    for label, _series in lines:
        fig.add_trace(
            go.Scatter(
                x=x_values,
                y=chart_frame[label],
                name=label,
                mode="lines",
                line=dict(
                    width=2.2,
                    color=LINE_COLORS.get(label),
                ),
            )
        )

    fig.update_layout(
        title=dict(text=chart_title, font=dict(size=title_size)),
        template="plotly_white",
        height=height,
        margin=dict(l=12, r=12, t=52, b=16),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=legend_y, xanchor="left", x=0),
        barmode="relative",
    )
    fig.update_xaxes(
    title_text=x_title,
    tickangle=-90,
)
    fig.update_yaxes(
    title_text=str(chart_spec.get("unit", "")),
    tickformat=".1f",
    )
    return fig, chart_title


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return slug or "chart"


def render_expandable_plotly(
    fig: go.Figure,
    key: str,
    title: str,
    expanded_height: int = 820,
    compact: bool = False,
) -> None:
    _spacer, expand_col = st.columns([8, 0.7] if compact else [5, 0.8])
    with expand_col:
        expand = st.button(
            "↗",
            key=f"{key}_expand",
            help=f"Expand {title}",
            use_container_width=True,
        )

    st.plotly_chart(fig, use_container_width=True, key=key)

    if not expand:
        return

    open_plotly_dialog(fig, key=key, title=title, expanded_height=expanded_height)


def open_plotly_dialog(
    fig: go.Figure,
    key: str,
    title: str,
    expanded_height: int,
) -> None:
    dialog = getattr(st, "dialog", None) or getattr(st, "experimental_dialog", None)
    if dialog is None:
        st.info("Use the chart toolbar to open Plotly's fullscreen view.")
        return

    @dialog(title, width="large")
    def expanded_chart() -> None:
        expanded_fig = go.Figure(fig)
        expanded_fig.update_layout(height=expanded_height)
        st.plotly_chart(expanded_fig, use_container_width=True, key=f"{key}_expanded")

    expanded_chart()


def title_with_last_period(title: str, series_items: list[tuple[str, pd.Series]]) -> str:
    period = latest_series_period(series_items)
    if not period:
        return title
    return f"{title}, last: {period}"


def latest_series_period(series_items: list[tuple[str, pd.Series]]) -> str:
    latest_date = None
    latest_label = ""
    for _label, series in series_items:
        clean = pd.to_numeric(series, errors="coerce").dropna()
        if clean.empty:
            continue
        label = str(clean.index[-1])
        date_value = parse_period(label)
        sort_value = date_value if not pd.isna(date_value) else pd.Timestamp.min
        if latest_date is None or sort_value > latest_date:
            latest_date = sort_value
            latest_label = label
    return latest_label


def build_chart_series(
    frame: pd.DataFrame,
    series_specs: list[dict[str, Any]],
) -> list[tuple[str, pd.Series]]:
    built: list[tuple[str, pd.Series]] = []
    for series_spec in series_specs:
        series = transformed_series(frame, series_spec)
        if series is None:
            continue
        clean = pd.to_numeric(series, errors="coerce")
        if clean.dropna().empty:
            continue
        built.append((str(series_spec.get("label") or series_spec.get("column")), clean))
    return built


def transformed_series(frame: pd.DataFrame, series_spec: dict[str, Any]) -> pd.Series | None:
    base = base_series(frame, series_spec)
    if base is None:
        return derived_real_economy_series(frame, series_spec)

    transform = str(series_spec.get("transform") or "level")
    lag = int(series_spec.get("lag") or 1)

    if transform in {"level", ""}:
        result = base
    elif transform in {"pct_change", "yoy"}:
        result = base.pct_change(lag, fill_method=None) * 100
    elif transform == "annualized_pct_change":
        annualizer = float(series_spec.get("annualizer") or 1)
        result = base.pct_change(lag, fill_method=None) * annualizer * 100
    elif transform == "rolling_yoy":
        window = int(series_spec.get("window") or lag)
        result = base.rolling(window=window, min_periods=window).sum().pct_change(lag, fill_method=None) * 100
    elif transform == "ratio":
        denominator = denominator_series(frame, series_spec)
        if denominator is None:
            return None
        result = base.div(denominator) * 100
    elif transform == "diff_share":
        denominator = denominator_series(frame, series_spec)
        if denominator is None:
            return None
        result = base.diff(lag).div(denominator.shift(lag)) * 100
    else:
        result = base

    scale = float(series_spec.get("scale") or 1)
    return result * scale


def base_series(frame: pd.DataFrame, series_spec: dict[str, Any]) -> pd.Series | None:
    if "column" in series_spec:
        column = str(series_spec["column"])
        if column not in frame.columns:
            return None
        base = pd.to_numeric(frame[column], errors="coerce")
    else:
        columns = [str(column) for column in series_spec.get("columns_sum", [])]
        existing = [column for column in columns if column in frame.columns]
        if not existing:
            return None
        base = frame[existing].apply(pd.to_numeric, errors="coerce").sum(axis=1, min_count=1)

    minus_columns = [str(column) for column in series_spec.get("minus_columns", [])]
    existing_minus = [column for column in minus_columns if column in frame.columns]
    if existing_minus:
        base = base - frame[existing_minus].apply(pd.to_numeric, errors="coerce").sum(axis=1, min_count=1)

    return base


def denominator_series(frame: pd.DataFrame, series_spec: dict[str, Any]) -> pd.Series | None:
    denominator = str(series_spec.get("denominator") or "")
    if denominator not in frame.columns:
        return None
    return pd.to_numeric(frame[denominator], errors="coerce")


def derived_real_economy_series(frame: pd.DataFrame, series_spec: dict[str, Any]) -> pd.Series | None:
    column = str(series_spec.get("column") or "")
    if not column:
        return None

    ytd_match = re.fullmatch(r"gdp_ytd_(.+)_contrib", column)
    if ytd_match:
        return ytd_gdp_contribution(frame, f"gdp_{ytd_match.group(1)}")

    q_match = re.fullmatch(r"gdp_q_(.+)_contrib", column)
    if q_match:
        return diff_share_series(frame, f"gdp_{q_match.group(1)}", "gdp", 4)

    y_match = re.fullmatch(r"gdp_y_(.+)_contrib", column)
    if y_match:
        return diff_share_series(frame, f"gdp_{y_match.group(1)}", "gdp", 1)

    share_match = re.fullmatch(r"gdp_(.+)_share", column)
    if share_match:
        sector_columns = [
            "gdp_agr",
            "gdp_mine",
            "gdp_manu",
            "gdp_elec",
            "gdp_cons",
            "gdp_trad",
            "gdp_tran",
            "gdp_comm",
            "gdp_serv_oth",
            "gdp_tax",
        ]

        numerator = f"gdp_{share_match.group(1)}"
        existing = [col for col in sector_columns if col in frame.columns]

        if numerator not in frame.columns or not existing:
            return None

        denominator = frame[existing].apply(pd.to_numeric, errors="coerce").sum(axis=1, min_count=1)

        return (
            pd.to_numeric(frame[numerator], errors="coerce")
            .div(denominator)
            * 100
        )
    if column == "gdp_ytd_growth":
        return ytd_gdp_contribution(frame, "gdp")
    if column == "gdp_q_growth":
        return diff_share_series(frame, "gdp", "gdp", 4)
    if column == "gdp_y_growth":
        return diff_share_series(frame, "gdp", "gdp", 1)
    if column == "gdp_nom_tn" and "gdp_nom" in frame.columns:
        return pd.to_numeric(frame["gdp_nom"], errors="coerce") / 1e6

    return None


def diff_share_series(frame: pd.DataFrame, numerator: str, denominator: str, lag: int) -> pd.Series | None:
    if numerator not in frame.columns or denominator not in frame.columns:
        return None
    base = pd.to_numeric(frame[numerator], errors="coerce")
    denom = pd.to_numeric(frame[denominator], errors="coerce")
    return base.diff(lag).div(denom.shift(lag)) * 100


def ytd_gdp_contribution(frame: pd.DataFrame, numerator: str) -> pd.Series | None:
    if numerator not in frame.columns or "gdp" not in frame.columns:
        return None

    period_frame = pd.DataFrame(
        [quarter_period_parts(value) for value in frame.index],
        index=frame.index,
        columns=["year", "quarter"],
    )
    values = pd.DataFrame(
        {
            "numerator": pd.to_numeric(frame[numerator], errors="coerce"),
            "gdp": pd.to_numeric(frame["gdp"], errors="coerce"),
            "year": period_frame["year"],
            "quarter": period_frame["quarter"],
        },
        index=frame.index,
    )
    result = pd.Series(index=frame.index, dtype="float64")

    for period, row in period_frame.dropna().iterrows():
        year = int(row["year"])
        quarter = int(row["quarter"])
        current_mask = (values["year"] == year) & (values["quarter"] <= quarter)
        previous_mask = (values["year"] == year - 1) & (values["quarter"] <= quarter)
        current_sum = values.loc[current_mask, "numerator"].sum(min_count=1)
        previous_sum = values.loc[previous_mask, "numerator"].sum(min_count=1)
        previous_gdp = values.loc[previous_mask, "gdp"].sum(min_count=1)
        if pd.isna(current_sum) or pd.isna(previous_sum) or pd.isna(previous_gdp) or previous_gdp == 0:
            continue
        result.loc[period] = (current_sum - previous_sum) / previous_gdp * 100

    return result


def quarter_period_parts(value: Any) -> tuple[int | None, int | None]:
    text = str(value).strip()
    quarterly = re.fullmatch(r"(\d{2})Q([1-4])", text)
    if quarterly:
        return expand_two_digit_year(quarterly.group(1)), int(quarterly.group(2))

    parsed = parse_period(value)
    if pd.isna(parsed):
        return None, None
    timestamp = pd.Timestamp(parsed)
    return int(timestamp.year), int((timestamp.month - 1) // 3 + 1)


def chart_x_values(index: pd.Index) -> tuple[pd.Series | pd.Index, str]:
    labels = index.astype(str)

    # Quarterly labels: 25Q1
    if all(re.fullmatch(r"\d{2}Q[1-4]", value) for value in labels):
        return labels, ""

    # Yearly labels: 19Y -> 2019
    if all(re.fullmatch(r"\d{2}Y", value) for value in labels):
        yearly_labels = [f"20{value[:2]}" for value in labels]
        return yearly_labels, ""

    dates = index_to_datetime(index)

    if dates.notna().all():
        return dates, ""

    return labels, "Period"


def render_metric_grid(
    frame: pd.DataFrame,
    metrics: list[tuple[str, str, str, str]],
) -> None:
    existing = [metric for metric in metrics if metric[0] in frame.columns]
    if not existing:
        return

    columns = st.columns(min(3, len(existing)) if len(existing) <= 3 else 6)
    for index, (variable, label, suffix, delta_suffix) in enumerate(existing):
        value, previous, period = latest_values(frame[variable])
        delta = value - previous if value is not None and previous is not None else None
        columns[index % len(columns)].metric(
            label=f"{label} ({period})" if period else label,
            value=format_value(value, suffix),
            delta=format_delta(delta, delta_suffix),
        )


def latest_values(series: pd.Series) -> tuple[float | None, float | None, str]:
    clean = pd.to_numeric(series, errors="coerce").dropna()
    if clean.empty:
        return None, None, ""

    value = float(clean.iloc[-1])
    previous = float(clean.iloc[-2]) if len(clean) > 1 else None
    period = str(clean.index[-1])
    return value, previous, period


def format_value(value: float | None, suffix: str = "") -> str:
    if value is None or pd.isna(value):
        return "n/a"

    absolute = abs(value)
    if absolute >= 1000:
        formatted = f"{value:,.0f}"
    elif absolute >= 100:
        formatted = f"{value:,.1f}"
    else:
        formatted = f"{value:,.2f}"

    return f"{formatted} {suffix}".strip()


def format_delta(value: float | None, suffix: str = "") -> str | None:
    if value is None or pd.isna(value):
        return None
    return f"{value:+,.2f} {suffix}".strip()


def render_chart_section(
    title: str,
    frame: pd.DataFrame,
    chart_groups: dict[str, list[str]],
    default_observations: int,
) -> None:
    st.markdown(f"#### {title}")
    control_cols = st.columns([1, 2, 1])
    group = control_cols[0].selectbox(
        "Group",
        list(chart_groups),
        key=f"{title}_group",
    )
    available_defaults = [column for column in chart_groups[group] if column in frame.columns]
    selected = control_cols[1].multiselect(
        "Series",
        list(frame.columns),
        default=available_defaults,
        format_func=series_label,
        key=f"{title}_series",
    )
    observations = control_cols[2].number_input(
        "Periods",
        min_value=4,
        max_value=max(4, len(frame)),
        value=min(default_observations, len(frame)),
        step=1,
        key=f"{title}_periods",
    )
    render_line_chart(frame, selected, int(observations), key=title)


def render_line_chart(
    frame: pd.DataFrame,
    selected: list[str],
    observations: int,
    key: str,
) -> None:
    selected = [column for column in selected if column in frame.columns]
    if not selected:
        st.info("Choose one or more series.")
        return

    chart_data = frame[selected].tail(observations).apply(pd.to_numeric, errors="coerce")
    chart_data = chart_data.dropna(how="all")
    if chart_data.empty:
        st.info("Selected series have no numeric observations.")
        return

    plot_data = chart_data.copy()
    plot_data["Period"] = plot_data.index.astype(str)
    plot_data["Date"] = index_to_datetime(plot_data.index)
    date_complete = plot_data["Date"].notna().all()

    long = plot_data.melt(
        id_vars=["Period", "Date"],
        var_name="Series",
        value_name="Value",
    ).dropna(subset=["Value"])
    long["Indicator"] = long["Series"].map(series_label)
    x_axis = "Date" if date_complete else "Period"

    fig = px.line(
        long,
        x=x_axis,
        y="Value",
        color="Indicator",
        markers=False,
        height=390,
        template="plotly_white",
    )
    fig.update_layout(
        legend_title_text="",
        margin=dict(l=12, r=12, t=18, b=12),
        hovermode="x unified",
    )
    fig.update_xaxes(
    title_text="",
    tickangle=-90,
)
    fig.update_yaxes(title_text="")
    render_expandable_plotly(
        fig,
        key=f"chart_{key}",
        title=str(key),
        expanded_height=760,
    )


def index_to_datetime(index: pd.Index) -> pd.Series:
    values = [parse_period(value) for value in index]
    return pd.Series(values, index=index)


def parse_period(value: Any) -> pd.Timestamp | pd.NaT:
    if isinstance(value, pd.Timestamp):
        return value

    if isinstance(value, (int, float)) and not pd.isna(value):
        try:
            return pd.to_datetime(float(value), unit="D", origin="1899-12-30")
        except (ValueError, OverflowError):
            return pd.NaT

    text = str(value).strip()
    if re.fullmatch(r"\d+(\.0)?", text):
        try:
            return pd.to_datetime(float(text), unit="D", origin="1899-12-30")
        except (ValueError, OverflowError):
            pass

    monthly = re.fullmatch(r"(\d{2})M(\d{1,2})", text)
    if monthly:
        year = expand_two_digit_year(monthly.group(1))
        month = int(monthly.group(2))
        return pd.Period(f"{year}-{month:02d}", freq="M").to_timestamp()

    quarterly = re.fullmatch(r"(\d{2})Q([1-4])", text)
    if quarterly:
        year = expand_two_digit_year(quarterly.group(1))
        quarter = int(quarterly.group(2))
        return pd.Period(f"{year}Q{quarter}", freq="Q").to_timestamp()

    yearly = re.fullmatch(r"(\d{2})Y", text)
    if yearly:
        year = expand_two_digit_year(yearly.group(1))
        return pd.Timestamp(year=year, month=1, day=1)

    return pd.to_datetime(text, errors="coerce")


def expand_two_digit_year(value: str) -> int:
    year = int(value)
    return 1900 + year if year >= 80 else 2000 + year


def render_indicator_tables(indicators: dict[str, pd.DataFrame]) -> None:
    if not indicators:
        st.warning("No derived indicator tables are available from the macro data pickle.")
        return

    for sheet_name, title in (("m", "Monthly Indicators"), ("q", "Quarterly Indicators")):
        frame = indicators.get(sheet_name)
        if frame is None or frame.empty:
            continue
        st.subheader(title)
        display = frame.copy()
        display.insert(0, "Indicator", [series_label(index) for index in display.index])
        st.dataframe(display, use_container_width=True, height=360)
        st.download_button(
            f"Download {title} CSV",
            display.to_csv(index=True).encode("utf-8"),
            file_name=f"{sheet_name}_indicators.csv",
            mime="text/csv",
        )

def render_updates_section() -> None:
    st.subheader("Macroeconomic Updates")
    selected_period = st.selectbox(
        "Update",
        list(SAMPLE_ANALYSIS),
        format_func=lambda period: f"{period} - {SAMPLE_ANALYSIS[period]['title']}",
    )
    analysis = SAMPLE_ANALYSIS[selected_period]

    st.caption(f"Published {analysis['date']}")
    st.markdown(f"### {analysis['title']}")
    st.write(analysis["summary"])

    left, right = st.columns([1.15, 0.85])
    with left:
        st.markdown("#### Key Messages")
        for item in analysis["bullets"]:
            st.markdown(f"- {item}")

    with right:
        st.markdown("#### Watchlist")
        for item in analysis["risks"]:
            st.markdown(f"- {item}")

    st.markdown("#### Supporting Reports")
    analysis_reports = [
        FORECAST_REPORT_DIR / "Data report.pdf",
        FORECAST_REPORT_DIR / "Filtered History.pdf",
        FORECAST_REPORT_DIR / "Shocks Decomposition.pdf",
        FORECAST_REPORT_DIR / "Model.pdf",
    ]
    render_download_list(
        [path for path in analysis_reports if path.exists()],
        empty_message="No analysis support reports found.",
        key_prefix="analysis_report",
    )


def render_forecast_section() -> None:
    st.subheader("Forecasts")
    scenario = st.radio(
        "Scenario",
        list(SAMPLE_FORECASTS),
        index=list(SAMPLE_FORECASTS).index("Baseline"),
        horizontal=True,
    )
    scenario = scenario or "Baseline"
    forecast = SAMPLE_FORECASTS[scenario]

    st.write(forecast["narrative"])
    forecast_table = pd.DataFrame(forecast["table"])
    st.dataframe(forecast_table, use_container_width=True, hide_index=True)

    chart_frame = forecast_table.set_index("Indicator")[["2026", "2027", "2028"]].transpose()
    fig = px.line(
        chart_frame,
        x=chart_frame.index,
        y=chart_frame.columns,
        markers=True,
        template="plotly_white",
        height=360,
    )
    fig.update_layout(
        legend_title_text="",
        margin=dict(l=12, r=12, t=20, b=12),
        hovermode="x unified",
    )
    fig.update_xaxes(
    title_text="",
    tickangle=-90,
)
    fig.update_yaxes(title_text="Forecast value")
    render_expandable_plotly(
        fig,
        key=f"forecast_chart_{scenario}",
        title=f"{scenario} forecast",
        expanded_height=760,
    )

    st.markdown("#### Forecast Reports")
    forecast_reports = [
        FORECAST_REPORT_DIR / "forecast_base_2603.pdf",
        FORECAST_REPORT_DIR / "forecast_alt.pdf",
        FORECAST_REPORT_DIR / "forecast_compare.pdf",
        FORECAST_REPORT_DIR / "back_test.pdf",
    ]
    render_download_list(
        [path for path in forecast_reports if path.exists()],
        empty_message="No forecast reports found.",
        key_prefix="forecast_report",
    )


def render_data_explorer(macro_data: dict[str, pd.DataFrame]) -> None:
    if not macro_data:
        st.warning("No macro data pickle found.")
        return

    dataset = st.selectbox("Dataset", list(macro_data), index=0)
    frame = macro_data[dataset].copy()
    frame.columns = frame.columns.astype(str)

    controls = st.columns([1.2, 2, 1, 1])
    search = controls[0].text_input("Filter", "")
    available = sorted(
        column
        for column in frame.columns
        if not search or search.lower() in column.lower() or search.lower() in series_label(column).lower()
    )
    defaults = [column for column in DATASET_DEFAULTS.get(dataset, []) if column in available]
    selected = controls[1].multiselect(
        "Series",
        available,
        default=defaults[:4],
        format_func=series_label,
    )
    observations = controls[2].number_input(
        "Periods",
        min_value=5,
        max_value=max(5, len(frame)),
        value=min(120, len(frame)),
        step=5,
    )
    transform = controls[3].selectbox(
        "Transform",
        ["Level", "Difference", "Percent change", "Year-over-year"],
    )

    transformed = transform_frame(frame, dataset, transform)
    render_line_chart(transformed, selected, int(observations), key=f"explorer_{dataset}_{transform}")

    if selected:
        table = transformed[selected].tail(int(observations)).copy()
        table.insert(0, "Period", table.index.astype(str))
        st.dataframe(table, use_container_width=True, height=360)
        st.download_button(
            "Download selected data CSV",
            table.to_csv(index=False).encode("utf-8"),
            file_name=f"{dataset.lower()}_selected_data.csv",
            mime="text/csv",
        )


def transform_frame(frame: pd.DataFrame, dataset: str, transform: str) -> pd.DataFrame:
    numeric = frame.apply(pd.to_numeric, errors="coerce")
    if transform == "Difference":
        return numeric.diff()
    if transform == "Percent change":
        return numeric.pct_change(fill_method=None) * 100
    if transform == "Year-over-year":
        lags = {"Daily": 365, "Monthly": 12, "Quarterly": 4, "Yearly": 1}
        return numeric.pct_change(lags.get(dataset, 1), fill_method=None) * 100
    return numeric


def render_archive(indicators: dict[str, pd.DataFrame]) -> None:
    st.subheader("Archive")

    report_files = find_files(REPORT_DIRS, ("*.pdf", "*.xlsx"))
    forecast_reports = find_files([FORECAST_REPORT_DIR], ("*.pdf",))
    historical_models = find_files([HISTORICAL_FORECAST_DIR, FORECAST_DATABASE_DIR], ("*.mat", "*.csv"))
    figure_files = find_files([FIGURE_DIR], ("*.png", "*.jpg", "*.jpeg"))

    report_tab, forecast_tab, figure_tab, data_tab = st.tabs(
        ["Macro Reports", "Forecast Archive", "Chart Images", "Data Downloads"]
    )

    with report_tab:
        render_download_list(report_files, "No macro reports found.", "archive_macro_report")

    with forecast_tab:
        st.markdown("#### Historical Forecast Reports")
        historical_pdf = [
            path
            for path in forecast_reports
            if re.search(r"forecast_(21|22|23|24|base|alt|compare)", path.name, re.IGNORECASE)
        ]
        render_download_list(historical_pdf, "No historical forecast PDFs found.", "archive_forecast_pdf")

        st.markdown("#### Forecast Model Files")
        render_download_list(historical_models, "No historical forecast data files found.", "archive_forecast_model")

    with figure_tab:
        st.markdown("#### Static Report Chart Gallery")
        if not figure_files:
            st.info("No figures found.")
        else:
            names = [path.name for path in figure_files]
            selected_name = st.selectbox("Figure", names)
            selected_path = next(path for path in figure_files if path.name == selected_name)
            st.image(str(selected_path), use_column_width=True)
            st.download_button(
                "Download figure",
                selected_path.read_bytes(),
                file_name=selected_path.name,
                mime=mime_for(selected_path),
            )

    with data_tab:
        render_indicator_tables(indicators)


def render_download_list(paths: list[Path], empty_message: str, key_prefix: str) -> None:
    if not paths:
        st.info(empty_message)
        return

    for path in paths:
        label = f"{path.name} ({path.stat().st_size / 1024:,.0f} KB)"
        st.download_button(
            label,
            path.read_bytes(),
            file_name=path.name,
            mime=mime_for(path),
            key=f"{key_prefix}_{path.name}",
            use_container_width=True,
        )


def find_files(directories: list[Path], patterns: tuple[str, ...]) -> list[Path]:
    files: list[Path] = []
    for directory in directories:
        if not directory.exists():
            continue
        for pattern in patterns:
            files.extend(directory.glob(pattern))
    return sorted(files, key=lambda path: path.stat().st_mtime, reverse=True)


def mime_for(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return "application/pdf"
    if suffix == ".xlsx":
        return "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    if suffix == ".png":
        return "image/png"
    if suffix in {".jpg", ".jpeg"}:
        return "image/jpeg"
    return "application/octet-stream"


def series_label(value: Any) -> str:
    key = str(value)
    if key in LABEL_OVERRIDES:
        return LABEL_OVERRIDES[key]

    label = key.replace("_", " ").strip().title()
    replacements = {
        "Gdp": "GDP",
        "Usd": "USD",
        "Mnt": "MNT",
        "Cny": "CNY",
        "Fx": "FX",
        "Cpi": "CPI",
        "Yoy": "YoY",
        "Qoq": "QoQ",
        "Mom": "MoM",
        "Npl": "NPL",
        "Mse": "MSE",
        "Bom": "BoM",
    }
    for old, new in replacements.items():
        label = label.replace(old, new)
    return label


def dataframe_to_excel_bytes(frame: pd.DataFrame, sheet_name: str) -> bytes:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        frame.to_excel(writer, sheet_name=sheet_name[:31])
    return buffer.getvalue()


if __name__ == "__main__":
    main()
