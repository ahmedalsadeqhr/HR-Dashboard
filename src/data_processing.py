import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime
from src.db import fetch_employees

# ── Column maps for the two new source files ──────────────────────────────────
# Both files export row 0 as English display-name headers; real data starts row 1.

_ACTIVE_COLS = {
    'JobNumber': 'Employee ID',
    'UserID-ExportName': 'Full Name',
    'UserID-Email': 'Email',
    'extcrmzh_615692_156087692': 'CRM Account',
    'parent_Gender': 'Gender',
    'OIdDepartment': 'Department',
    'OIdJobPost': 'Position',
    'EmployType': 'Employment Type',
    'EmploymentForm': 'Employment Form',
    'OIdJobLevel': 'Job Level',
    'POIdEmpAdmin-ExportName': 'Line Manager',
    'EntryDate': 'Join Date',
    'ProbationStopDate': 'Probation Period End Date',
    'RegularizationDate': 'Regularization Date',
    'parent_Nationality': 'Nationality',
    'parent_Birthday': 'Birthday Date',
    'LookupPrefix_UserID_TerminateDate': 'Contract End Date',
}

_LEAVERS_COLS = {
    'JobNumber': 'Employee ID',
    'UserID-ExportName': 'Full Name',
    'UserID-Email': 'Email',
    'extcrmzh_615692_156087692': 'CRM Account',
    'EntryDate': 'Join Date',
    'TransitionTypeOID': 'Exit Type',
    'ChangeReason': 'Exit Reason Category',
    'LastWorkDate': 'Exit Date',
    'OIdDepartment': 'Department',
    'OIdJobPosition': 'Position',
    'OIdJobLevel': 'Job Level',
}

# "Departed Employees_*.xlsx" export: far richer than Offboarding Management (gender,
# line manager, nationality, birthday, probation dates...). Its column names carry a
# 'LookupPrefix_UserID_' prefix, and a few are GUID-prefixed ('<guid>~Field'), so we
# match those by suffix.
_DEPARTED_COLS = {
    'LookupPrefix_UserID_JobNumber': 'Employee ID',
    'Name': 'Full Name',
    'Email': 'Email',
    'LookupPrefix_UserID_extcrmzh_615692_156087692': 'CRM Account',
    'Gender': 'Gender',
    'LookupPrefix_UserID_TransitionTypeOID': 'Exit Type',
    'LookupPrefix_UserID_ChangeReason': 'Exit Reason Category',
    'LookupPrefix_UserID_OIdDepartment': 'Department',
    'LookupPrefix_UserID_OIdJobPost': 'Position',
    'LookupPrefix_UserID_EmployType': 'Employment Type',
    'LookupPrefix_UserID_EmploymentForm': 'Employment Form',
    'LookupPrefix_UserID_OIdJobLevel': 'Job Level',
    'LookupPrefix_UserID_EntryDate': 'Join Date',
    'LookupPrefix_UserID_ProbationStopDate': 'Probation Period End Date',
    'LookupPrefix_UserID_RegularizationDate': 'Regularization Date',
    'LookupPrefix_UserID_LastWorkDate': 'Exit Date',
    'Nationality': 'Nationality',
    'Birthday': 'Birthday Date',
}
_DEPARTED_SUFFIX_COLS = {'~POIdEmpAdmin-ExportName': 'Line Manager'}


def _is_departed_export(df: pd.DataFrame) -> bool:
    return 'LookupPrefix_UserID_JobNumber' in df.columns


def _departed_column_map(df: pd.DataFrame) -> dict:
    mapping = {src: tgt for src, tgt in _DEPARTED_COLS.items() if src in df.columns}
    for col in df.columns:
        for suffix, tgt in _DEPARTED_SUFFIX_COLS.items():
            if str(col).endswith(suffix):
                mapping[col] = tgt
    return mapping


def merge_two_sources(active_raw: pd.DataFrame, leavers_raw: pd.DataFrame) -> pd.DataFrame:
    """Normalise and merge the Active Employees file with a leavers file.

    The leavers file may be either the "Departed Employees" export (preferred, all rows
    are leavers) or the "Offboarding Management" export (only ApprovalStatus ==
    'Effective' rows are kept). Row 0 of each file holds English display names and is
    skipped.
    """
    # Skip display-name header row
    active = active_raw.iloc[1:].reset_index(drop=True).copy()
    leavers = leavers_raw.iloc[1:].reset_index(drop=True).copy()

    # Keep only effective leavers
    if 'ApprovalStatus' in leavers.columns:
        leavers = leavers[leavers['ApprovalStatus'] == 'Effective'].reset_index(drop=True)

    # Select and rename active columns
    active_keep = {src: tgt for src, tgt in _ACTIVE_COLS.items() if src in active.columns}
    active = active[list(active_keep.keys())].rename(columns=active_keep)
    active['Employee Status'] = 'Active'

    # Select and rename leavers columns
    if _is_departed_export(leavers):
        leavers_keep = _departed_column_map(leavers)
    else:
        leavers_keep = {src: tgt for src, tgt in _LEAVERS_COLS.items() if src in leavers.columns}
    leavers = leavers[list(leavers_keep.keys())].rename(columns=leavers_keep)
    leavers['Employee Status'] = 'Departed'

    _require_source_columns(active_raw, leavers_raw, active, leavers)

    # Employee ID duplicates: within a file keep the last row; if someone is in
    # both files (e.g. a rehire) the Active row wins so they are not counted twice.
    dropped = 0
    if 'Employee ID' in active.columns:
        n = len(active)
        active = active.drop_duplicates(subset='Employee ID', keep='last')
        dropped += n - len(active)
    if 'Employee ID' in leavers.columns:
        n = len(leavers)
        if 'Exit Date' in leavers.columns:
            order = pd.to_datetime(leavers['Exit Date'], errors='coerce').argsort(kind='stable')
            leavers = leavers.iloc[order]
        leavers = leavers.drop_duplicates(subset='Employee ID', keep='last')
        dropped += n - len(leavers)
        if 'Employee ID' in active.columns:
            n = len(leavers)
            leavers = leavers[~leavers['Employee ID'].isin(active['Employee ID'])]
            dropped += n - len(leavers)

    combined = pd.concat([active, leavers], ignore_index=True, sort=False)
    combined.attrs['duplicates_dropped'] = dropped
    return combined


def _require_source_columns(active_raw, leavers_raw, active, leavers):
    """Fail with a clear message when an export is missing columns the dashboard needs."""
    problems = []
    for tgt in ('Join Date', 'Department'):
        if tgt not in active.columns:
            problems.append(f"Active Employees file has no '{tgt}' column")
    if len(leavers) > 0:
        for tgt in ('Exit Date', 'Exit Type', 'Join Date'):
            if tgt not in leavers.columns:
                problems.append(
                    f"Leavers file has no '{tgt}' column. "
                    f"Columns found: {', '.join(map(str, leavers_raw.columns[:25]))}"
                )
    if problems:
        raise ValueError('; '.join(problems))


@st.cache_data
def load_excel(file_path_or_buffer):
    """Load Excel file from path or uploaded buffer."""
    df = pd.read_excel(file_path_or_buffer)
    return process_data(df)


@st.cache_data(ttl=300)
def load_from_db() -> pd.DataFrame:
    """Load employee data from Supabase and process it. Cached for 5 minutes."""
    df = fetch_employees()
    if df.empty:
        return df
    return process_data(df)


_DEPT_NAME_FIXES = {
    'KSA市场部': 'KSA Marketing Department',
    '阿教项目部': 'Arabic Teaching Project Department',
}


def _normalise_department(name):
    if not isinstance(name, str):
        return name
    name = name.strip()
    if name in _DEPT_NAME_FIXES:
        return _DEPT_NAME_FIXES[name]
    return name.replace('小组', ' Team') if name.endswith('小组') else name


def _probation_status(df, today):
    """Classify each row's probation outcome.

    Departed: 'Left During Probation' if exit is before the probation end,
    'Completed Before Exit' if exit is on/after it, else 'No Data'.
    Active: 'Completed' once the end date has passed, 'In Probation' before,
    'No Data' when there is no end date.
    """
    end = df['Probation Period End Date']
    exit_dt = df['Exit Date'] if 'Exit Date' in df.columns else pd.Series(pd.NaT, index=df.index)
    departed = df['Employee Status'] == 'Departed'

    active_status = np.where(end.isna(), 'No Data',
                             np.where(end <= today, 'Completed', 'In Probation'))
    departed_status = np.where(
        end.isna() | exit_dt.isna(), 'No Data',
        np.where(exit_dt < end, 'Left During Probation', 'Completed Before Exit'))
    return np.where(departed, departed_status, active_status)


def process_data(df):
    """Process raw HR data: clean columns, parse dates, calculate derived fields."""
    df.columns = [str(c) for c in df.columns]
    df.columns = df.columns.str.replace('\n', ' ').str.replace('\r', ' ').str.replace('  ', ' ').str.strip()

    # Backward-compat renames for old Master-sheet column names
    rename_map = {
        'Join Date (yyyy/mm/dd)': 'Join Date',
        'Exit Date yyyy/mm/dd': 'Exit Date',
        'Position (After Joining)': 'Position After Joining',
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

    # Columns the dashboard filters/charts rely on: add empty ones if the stored
    # data lacks them (e.g. an upload with no leavers) so the app still loads.
    for col in ('Exit Type', 'Gender', 'Department', 'Position'):
        if col not in df.columns:
            df[col] = pd.NA
    if 'Employee Status' not in df.columns:
        df['Employee Status'] = 'Active'

    # The Departed export names a few teams in Chinese while Active uses English, which
    # splits one team into two in every department chart. Normalise to the English name.
    if 'Department' in df.columns:
        df['Department'] = df['Department'].map(_normalise_department)

    # Parse date columns
    date_cols = ['Join Date', 'Exit Date', 'Birthday Date', 'Probation Period End Date',
                 'Regularization Date', 'Contract End Date']
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')

    today = pd.Timestamp(datetime.now())

    # Age — recalculate from Birthday Date when available
    if 'Birthday Date' in df.columns:
        df['Age'] = ((today - df['Birthday Date']).dt.days / 365.25).fillna(0).astype(int)

    # Tenure in months
    if 'Join Date' in df.columns:
        if 'Exit Date' in df.columns:
            df['Tenure (Months)'] = np.where(
                df['Employee Status'] == 'Active',
                ((today - df['Join Date']).dt.days / 30.44).fillna(0),
                ((df['Exit Date'] - df['Join Date']).dt.days / 30.44).fillna(0)
            )
        else:
            df['Tenure (Months)'] = ((today - df['Join Date']).dt.days / 30.44).fillna(0)
        df['Tenure (Months)'] = df['Tenure (Months)'].clip(lower=0).round(1)

    # Time periods
    if 'Join Date' in df.columns:
        df['Join Year'] = df['Join Date'].dt.year
        df['Join Month'] = df['Join Date'].dt.to_period('M').astype(str)
        df['Join Quarter'] = df['Join Date'].dt.to_period('Q').astype(str)

    if 'Exit Date' in df.columns:
        df['Exit Year'] = df['Exit Date'].dt.year
        df['Exit Month'] = df['Exit Date'].dt.to_period('M').astype(str)

    # Probation status
    if 'Probation Period End Date' in df.columns:
        df['Probation Completed'] = _probation_status(df, today)

    # Employment type cleanup (handles both old and new schema)
    if 'Employment Type' not in df.columns:
        if 'Type' in df.columns:
            df['Employment Type'] = df['Type'].fillna('Unknown')
        else:
            df['Employment Type'] = 'Unknown'

    # Vendor cleanup (old schema only)
    if 'Vendor' in df.columns:
        df['Vendor'] = df['Vendor'].fillna('Direct Hire')

    # Nationality cleanup
    if 'Nationality' in df.columns:
        df['Nationality'] = df['Nationality'].fillna('Unknown')

    # Exit ReasonList cleanup (old schema)
    if 'Exit ReasonList' in df.columns:
        df['Exit ReasonList'] = df['Exit ReasonList'].fillna('')

    return df


def calculate_turnover_12m(df, today=None):
    """Rolling 12-month turnover.

    Turnover % = exits in the last 365 days / average headcount * 100, where average
    headcount is the mean of headcount 12 months ago and headcount today (headcount on a
    date = joined on/before it and not yet exited).
    """
    empty = {'turnover_12m': 0.0, 'exits_12m': 0, 'avg_headcount_12m': 0.0}
    if 'Join Date' not in df.columns or 'Exit Date' not in df.columns or len(df) == 0:
        return empty
    today = pd.Timestamp(today if today is not None else datetime.now()).normalize()
    start = today - pd.DateOffset(years=1)
    join = pd.to_datetime(df['Join Date'], errors='coerce')
    exit_dt = pd.to_datetime(df['Exit Date'], errors='coerce')

    def headcount(on):
        return int(((join <= on) & (exit_dt.isna() | (exit_dt > on))).sum())

    exits = int(((exit_dt > start) & (exit_dt <= today)).sum())
    avg_hc = (headcount(start) + headcount(today)) / 2
    return {
        'turnover_12m': (exits / avg_hc * 100) if avg_hc > 0 else 0.0,
        'exits_12m': exits,
        'avg_headcount_12m': avg_hc,
    }


@st.cache_data
def calculate_kpis(df):
    """Calculate all KPI metrics from filtered dataframe."""
    total = len(df)
    active = len(df[df['Employee Status'] == 'Active'])
    departed = len(df[df['Employee Status'] == 'Departed'])
    attrition_rate = (departed / total * 100) if total > 0 else 0
    avg_tenure = df['Tenure (Months)'].mean() if 'Tenure (Months)' in df.columns else 0
    avg_age = df[df['Age'] > 0]['Age'].mean() if 'Age' in df.columns else 0
    if pd.isna(avg_age):
        avg_age = 0

    retention_rate = (active / total * 100) if total > 0 else 0

    # Contractor ratio — handles both old schema (Employment Type with Freelancer/Contract)
    # and new schema (Employment Form with Outsourced)
    contractor_mask = pd.Series(False, index=df.index)
    if 'Employment Type' in df.columns:
        contractor_mask |= df['Employment Type'].str.contains(
            'Freelancer|freelancer|Contract', case=False, na=False
        )
    if 'Employment Form' in df.columns:
        contractor_mask |= df['Employment Form'].str.contains('Outsourced', case=False, na=False)
    contractor_ratio = (contractor_mask.sum() / total * 100) if total > 0 else 0

    nationality_count = df['Nationality'].nunique() if 'Nationality' in df.columns else 0

    # Gender — supports both M/F (old) and Male/Female (new)
    if 'Gender' in df.columns:
        male_count = df['Gender'].isin(['M', 'Male']).sum()
        female_count = df['Gender'].isin(['F', 'Female']).sum()
    else:
        male_count = female_count = 0
    gender_ratio = f"{male_count}:{female_count}"

    probation_pass_rate = 0
    if 'Probation Completed' in df.columns:
        # Only resolved outcomes count: still-in-probation and no-data rows are excluded.
        passed = df['Probation Completed'].isin(['Completed', 'Completed Before Exit']).sum()
        failed = (df['Probation Completed'] == 'Left During Probation').sum()
        if passed + failed > 0:
            probation_pass_rate = passed / (passed + failed) * 100

    growth_rate = 0
    if 'Join Year' in df.columns:
        current_year = datetime.now().year
        hired_this_year = len(df[df['Join Year'] == current_year])
        hired_last_year = len(df[df['Join Year'] == current_year - 1])
        if hired_last_year > 0:
            growth_rate = ((hired_this_year - hired_last_year) / hired_last_year * 100)

    return {
        'total': total,
        'active': active,
        'departed': departed,
        'attrition_rate': attrition_rate,
        'retention_rate': retention_rate,
        'avg_tenure': avg_tenure,
        'avg_age': avg_age,
        'contractor_ratio': contractor_ratio,
        'nationality_count': nationality_count,
        'gender_ratio': gender_ratio,
        'male_count': male_count,
        'female_count': female_count,
        'probation_pass_rate': probation_pass_rate,
        'growth_rate': growth_rate,
        **calculate_turnover_12m(df),
    }


def get_cohort_retention(df):
    """Calculate retention rate by join year cohort."""
    if 'Join Year' not in df.columns or len(df) == 0:
        return pd.DataFrame()

    cohort = df.groupby('Join Year').agg(
        Total=('Employee Status', 'count'),
        Active=('Employee Status', lambda x: (x == 'Active').sum()),
        Departed=('Employee Status', lambda x: (x == 'Departed').sum())
    ).reset_index()

    cohort = cohort[cohort['Join Year'] > 2000]
    if len(cohort) == 0:
        return pd.DataFrame()
    cohort['Retention Rate %'] = (cohort['Active'] / cohort['Total'] * 100).round(1)
    return cohort


def get_manager_attrition(df):
    """Analyze attrition linked to managers."""
    col = 'Direct Manager CRM while Resignation'
    if col not in df.columns:
        # Fall back to Line Manager if available
        col = 'Line Manager'
    if col not in df.columns:
        return pd.DataFrame()

    departed = df[df['Employee Status'] == 'Departed']
    if len(departed) == 0:
        return pd.DataFrame()

    mgr_df = departed[departed[col].notna()]
    if len(mgr_df) == 0:
        return pd.DataFrame()

    name_col = 'Full Name' if 'Full Name' in mgr_df.columns else mgr_df.columns[0]
    has_tenure = 'Tenure (Months)' in mgr_df.columns
    has_reason = 'Exit Reason Category' in mgr_df.columns

    agg_dict = {'Departures': (name_col, 'count')}
    if has_tenure:
        agg_dict['Avg_Tenure'] = ('Tenure (Months)', 'mean')
    if has_reason:
        agg_dict['Top_Reason'] = ('Exit Reason Category', lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else 'N/A')

    manager_data = mgr_df.groupby(col).agg(**agg_dict).reset_index()

    rename = {col: 'Manager', 'Departures': 'Departures'}
    if has_tenure:
        rename['Avg_Tenure'] = 'Avg Tenure (Months)'
    if has_reason:
        rename['Top_Reason'] = 'Top Exit Reason'
    manager_data = manager_data.rename(columns=rename)

    if 'Avg Tenure (Months)' in manager_data.columns:
        manager_data['Avg Tenure (Months)'] = manager_data['Avg Tenure (Months)'].round(1)
    return manager_data.sort_values('Departures', ascending=False)


def save_to_excel(df, file_path):
    """Save dataframe back to Excel, preserving original column names."""
    save_df = df.copy()

    reverse_map = {
        'Join Date': 'Join Date (yyyy/mm/dd)',
        'Exit Date': 'Exit Date yyyy/mm/dd',
        'Position After Joining': 'Position (After Joining)',
    }
    save_df = save_df.rename(columns={k: v for k, v in reverse_map.items() if k in save_df.columns})

    calc_cols = ['Age', 'Tenure (Months)', 'Join Year', 'Join Month', 'Join Quarter',
                 'Exit Year', 'Exit Month', 'Probation Completed', 'Employment Type']
    save_df = save_df.drop(columns=[c for c in calc_cols if c in save_df.columns], errors='ignore')

    save_df.to_excel(file_path, index=False)
