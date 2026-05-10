from __future__ import annotations

import hmac
import io
import pickle
import re
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.express as px
import streamlit as st

from auth_utils import verify_password


ROOT = Path(__file__).resolve().parent
DATA_PICKLE = ROOT / "data" / "macro_data.pickle"
MAIN_INDICATORS = ROOT / "main_indicators.xlsx"
FIGURE_DIR = ROOT / "figures"
REPORT_DIRS = [ROOT / "output", ROOT / "report" / "table"]


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


def main() -> None:
    st.set_page_config(
        page_title="Mongolia Macro Dashboard",
        page_icon="MN",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_css()
    user = require_login()

    with st.sidebar:
        st.caption(f"Signed in as {user['name']}")
        if st.button("Sign out", use_container_width=True):
            sign_out()
            st.rerun()

        st.divider()
        st.caption("Data cache")
        if st.button("Reload files", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    macro_data = load_macro_data(str(DATA_PICKLE), file_mtime(DATA_PICKLE))
    indicators = load_indicator_workbook(str(MAIN_INDICATORS), file_mtime(MAIN_INDICATORS))

    monthly_ts = indicator_timeseries(indicators.get("m"))
    quarterly_ts = indicator_timeseries(indicators.get("q"))

    render_header(macro_data, monthly_ts, quarterly_ts)

    overview_tab, table_tab, explorer_tab, report_tab = st.tabs(
        ["Overview", "Indicator Tables", "Data Explorer", "Reports"]
    )

    with overview_tab:
        render_overview(monthly_ts, quarterly_ts)

    with table_tab:
        render_indicator_tables(indicators)

    with explorer_tab:
        render_data_explorer(macro_data)

    with report_tab:
        render_reports()


def require_login() -> dict[str, str]:
    users = load_auth_users()

    if not users:
        render_auth_setup()
        st.stop()

    if st.session_state.get("authenticated"):
        return {
            "username": st.session_state.get("username", ""),
            "name": st.session_state.get("display_name", "User"),
            "role": st.session_state.get("role", "viewer"),
        }

    st.title("Mongolia Macro Dashboard")
    left, middle, right = st.columns([1, 1.1, 1])
    with middle:
        st.subheader("Sign in")
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Username").strip()
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button(
                "Sign in",
                type="primary",
                use_container_width=True,
            )

        if submitted:
            matched_username, user_config = find_user(username, users)
            if matched_username and password_is_valid(password, user_config):
                st.session_state["authenticated"] = True
                st.session_state["username"] = matched_username
                st.session_state["display_name"] = str(
                    user_config.get("name") or matched_username
                )
                st.session_state["role"] = str(user_config.get("role") or "viewer")
                st.rerun()
            st.error("Invalid username or password.")

    st.stop()


def render_auth_setup() -> None:
    st.title("Mongolia Macro Dashboard")
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
        str(username): safe_dict(config)
        for username, config in safe_dict(users).items()
    }


def safe_dict(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    try:
        return dict(value)
    except (TypeError, ValueError):
        return {}


def find_user(
    submitted_username: str,
    users: dict[str, dict[str, Any]],
) -> tuple[str | None, dict[str, Any]]:
    normalized = submitted_username.strip().lower()
    for username, config in users.items():
        if username.lower() == normalized:
            return username, config
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
    for key in ("authenticated", "username", "display_name", "role"):
        st.session_state.pop(key, None)


def inject_css() -> None:
    st.markdown(
        """
<style>
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


@st.cache_data(show_spinner=False)
def load_indicator_workbook(path: str, _mtime: float) -> dict[str, pd.DataFrame]:
    workbook = Path(path)
    if not workbook.exists():
        return {}

    sheets: dict[str, pd.DataFrame] = {}
    excel_file = pd.ExcelFile(workbook)
    for sheet_name in ("m", "q"):
        if sheet_name in excel_file.sheet_names:
            frame = pd.read_excel(workbook, sheet_name=sheet_name, index_col=0)
            frame = frame.apply(pd.to_numeric, errors="coerce")
            frame.index = frame.index.astype(str)
            frame.columns = frame.columns.astype(str)
            sheets[sheet_name] = frame
    return sheets


def indicator_timeseries(indicator_frame: pd.DataFrame | None) -> pd.DataFrame:
    if indicator_frame is None or indicator_frame.empty:
        return pd.DataFrame()

    frame = indicator_frame.transpose()
    frame.index = frame.index.astype(str)
    return frame.apply(pd.to_numeric, errors="coerce")


def render_header(
    macro_data: dict[str, pd.DataFrame],
    monthly_ts: pd.DataFrame,
    quarterly_ts: pd.DataFrame,
) -> None:
    st.title("Mongolia Macro Dashboard")

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


def render_overview(monthly_ts: pd.DataFrame, quarterly_ts: pd.DataFrame) -> None:
    if monthly_ts.empty and quarterly_ts.empty:
        st.warning("No indicator workbook found. Run `code/process_data.py` and `code/macro_table.py` first.")
        return

    if not monthly_ts.empty:
        st.subheader("Monthly Snapshot")
        render_metric_grid(monthly_ts, MONTHLY_METRICS)

    if not quarterly_ts.empty:
        st.subheader("Quarterly Snapshot")
        render_metric_grid(quarterly_ts, QUARTERLY_METRICS)

    render_macro_chart_sections()

    with st.expander("Interactive Indicator Trends", expanded=False):
        if not monthly_ts.empty:
            render_chart_section("Monthly Trends", monthly_ts, MONTHLY_CHARTS, default_observations=60)
        if not quarterly_ts.empty:
            render_chart_section("Quarterly Trends", quarterly_ts, QUARTERLY_CHARTS, default_observations=36)


def render_macro_chart_sections() -> None:
    st.subheader("Macro Charts")

    if not FIGURE_DIR.exists():
        st.info("No `figures` folder found. Run `code/macro_charts.py` to generate macro chart PNGs.")
        return

    available_count = sum(
        1
        for chart_files in MACRO_CHART_SECTIONS.values()
        for filename in chart_files
        if (FIGURE_DIR / filename).exists()
    )
    if available_count == 0:
        st.info("No macro chart PNGs found yet. Run `code/macro_charts.py` to populate the `figures` folder.")
        return

    expand_all = st.checkbox("Expand all macro chart sections", value=False)
    for index, (section_name, chart_files) in enumerate(MACRO_CHART_SECTIONS.items()):
        existing_files = [FIGURE_DIR / filename for filename in chart_files if (FIGURE_DIR / filename).exists()]
        missing_count = len(chart_files) - len(existing_files)
        if not existing_files:
            continue

        label = f"{section_name} ({len(existing_files)} charts)"
        with st.expander(label, expanded=expand_all or index == 0):
            if missing_count:
                st.caption(f"{missing_count} expected chart file(s) are not available.")

            columns = st.columns(2)
            for chart_index, path in enumerate(existing_files):
                with columns[chart_index % 2]:
                    st.markdown(f"**{MACRO_CHART_LABELS.get(path.name, path.stem)}**")
                    st.image(str(path), use_column_width=True)
                    st.download_button(
                        "Download",
                        path.read_bytes(),
                        file_name=path.name,
                        mime=mime_for(path),
                        key=f"macro_chart_download_{section_name}_{path.name}",
                        use_container_width=True,
                    )


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
    fig.update_xaxes(title_text="")
    fig.update_yaxes(title_text="")
    st.plotly_chart(fig, use_container_width=True, key=f"chart_{key}")


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
        st.warning("No `main_indicators.xlsx` workbook found.")
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

    if MAIN_INDICATORS.exists():
        st.download_button(
            "Download main_indicators.xlsx",
            MAIN_INDICATORS.read_bytes(),
            file_name="main_indicators.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
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
        return numeric.pct_change() * 100
    if transform == "Year-over-year":
        lags = {"Daily": 365, "Monthly": 12, "Quarterly": 4, "Yearly": 1}
        return numeric.pct_change(lags.get(dataset, 1)) * 100
    return numeric


def render_reports() -> None:
    report_files = find_files(REPORT_DIRS, ("*.pdf", "*.xlsx"))
    figure_files = find_files([FIGURE_DIR], ("*.png", "*.jpg", "*.jpeg"))

    report_col, figure_col = st.columns([1, 1.25])

    with report_col:
        st.subheader("Report Files")
        if not report_files:
            st.info("No reports found.")
        for path in report_files[:12]:
            label = f"{path.name} ({path.stat().st_size / 1024:,.0f} KB)"
            st.download_button(
                label,
                path.read_bytes(),
                file_name=path.name,
                mime=mime_for(path),
                use_container_width=True,
            )

    with figure_col:
        st.subheader("Figure Gallery")
        if not figure_files:
            st.info("No figures found.")
            return

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
