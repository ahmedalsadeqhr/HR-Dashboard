import pandas as pd
import numpy as np
from datetime import datetime


def load_excel(file_path_or_buffer):
    """Load Excel file from path or uploaded buffer."""
    df = pd.read_excel(file_path_or_buffer)
    return process_data(df)


def process_data(df):
    """Process raw HR data: clean columns, parse dates, calculate derived fields."""
    # Ensure all column names are strings, then clean
    df.columns = [str(c) for c in df.columns]
    df.columns = df.columns.str.replace('\n', ' ').str.strip()

    # Rename columns for consistency
    rename_map = {
        'Join Date (yyyy/mm/dd)': 'Join Date',
        'Exit Date yyyy/mm/dd': 'Exit Date',
        'Position (After Joining)': 'Position After Joining',
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

    # Parse date columns
    date_cols = ['Join Date', 'Exit Date', 'Birthday Date', 'Probation Period End Date']
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')

    today = pd.Timestamp(datetime.now())

    # Age
    if 'Birthday Date' in df.columns:
        df['Age'] = ((today - df['Birthday Date']).dt.days / 365.25).fillna(0).astype(int)

    # Tenure in months
    if 'Join Date' in df.columns:
        df['Tenure (Months)'] = np.where(
            df['Employee Status'] == 'Active',
            ((today - df['Join Date']).dt.days / 30.44).fillna(0),
            ((df['Exit Date'] - df['Join Date']).dt.days / 30.44).fillna(0)
        )
        df['Tenure (Months)'] = df['Tenure (Months)'].round(1)

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
        df['Probation Completed'] = np.where(
            df['Probation Period End Date'].notna() & (df['Probation Period End Date'] <= today),
            'Completed',
            np.where(
                df['Employee Status'] == 'Departed',
                np.where(
                    df['Probation Period End Date'].notna() & (df['Exit Date'] < df['Probation Period End Date']),
                    'Left During Probation',
                    'Completed Before Exit'
                ),
                np.where(
                    df['Probation Period End Date'].notna(),
                    'In Probation',
                    'No Data'
                )
            )
        )

    # Employment type cleanup
    if 'Type' in df.columns:
        df['Employment Type'] = df['Type'].fillna('Unknown')
    else:
        df['Employment Type'] = 'Unknown'

    # Vendor cleanup
    if 'Vendor' in df.columns:
        df['Vendor'] = df['Vendor'].fillna('Direct Hire')

    # Nationality cleanup
    if 'Nationality' in df.columns:
        df['Nationality'] = df['Nationality'].fillna('Unknown')

    # Exit Reason List cleanup (the cleaner 17-category version)
    if 'Exit ReasonList' in df.columns:
        df['Exit ReasonList'] = df['Exit ReasonList'].fillna('')

    return df


def calculate_kpis(df):
    """Calculate all KPI metrics from filtered dataframe."""
    total = len(df)
    active = len(df[df['Employee Status'] == 'Active'])
    departed = len(df[df['Employee Status'] == 'Departed'])
    attrition_rate = (departed / total * 100) if total > 0 else 0
    avg_tenure = df['Tenure (Months)'].mean() if 'Tenure (Months)' in df.columns else 0
    avg_age = df[df['Age'] > 0]['Age'].mean() if 'Age' in df.columns else 0

    # Retention rate (active / total)
    retention_rate = (active / total * 100) if total > 0 else 0

    # Contractor ratio
    contractor_ratio = 0
    if 'Employment Type' in df.columns:
        freelancers = len(df[df['Employment Type'].str.contains('Freelancer|freelancer|Contract', case=False, na=False)])
        contractor_ratio = (freelancers / total * 100) if total > 0 else 0

    # Diversity ratio (nationality)
    nationality_count = df['Nationality'].nunique() if 'Nationality' in df.columns else 0

    # Gender ratio
    male_count = len(df[df['Gender'] == 'M']) if 'Gender' in df.columns else 0
    female_count = len(df[df['Gender'] == 'F']) if 'Gender' in df.columns else 0
    gender_ratio = f"{male_count}:{female_count}"

    # Probation pass rate
    probation_pass_rate = 0
    if 'Probation Completed' in df.columns:
        prob_data = df[df['Probation Completed'] != 'No Data']
        if len(prob_data) > 0:
            completed = len(prob_data[prob_data['Probation Completed'].isin(['Completed', 'Completed Before Exit'])])
            probation_pass_rate = (completed / len(prob_data) * 100)

    # Headcount growth YoY
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
    }


def get_cohort_retention(df):
    """Calculate retention rate by join year cohort."""
    if 'Join Year' not in df.columns:
        return pd.DataFrame()

    cohort = df.groupby('Join Year').agg(
        Total=('Employee Status', 'count'),
        Active=('Employee Status', lambda x: (x == 'Active').sum()),
        Departed=('Employee Status', lambda x: (x == 'Departed').sum())
    ).reset_index()

    cohort = cohort[cohort['Join Year'] > 2000]
    cohort['Retention Rate %'] = (cohort['Active'] / cohort['Total'] * 100).round(1)
    return cohort


def get_manager_attrition(df):
    """Analyze attrition linked to managers."""
    col = 'Direct Manager CRM while Resignation'
    if col not in df.columns:
        return pd.DataFrame()

    departed = df[df['Employee Status'] == 'Departed']
    if len(departed) == 0:
        return pd.DataFrame()

    manager_data = departed[departed[col].notna()].groupby(col).agg(
        Departures=('Full Name', 'count'),
        Avg_Tenure=('Tenure (Months)', 'mean'),
        Top_Reason=('Exit Reason Category', lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else 'N/A')
    ).reset_index()

    manager_data.columns = ['Manager CRM', 'Departures', 'Avg Tenure (Months)', 'Top Exit Reason']
    manager_data['Avg Tenure (Months)'] = manager_data['Avg Tenure (Months)'].round(1)
    return manager_data.sort_values('Departures', ascending=False)


def save_to_excel(df, file_path):
    """Save dataframe back to Excel, preserving original column names."""
    save_df = df.copy()

    # Reverse rename for saving
    reverse_map = {
        'Join Date': 'Join Date\n(yyyy/mm/dd)',
        'Exit Date': 'Exit Date\nyyyy/mm/dd',
        'Position After Joining': 'Position\n(After Joining)',
    }
    save_df = save_df.rename(columns={k: v for k, v in reverse_map.items() if k in save_df.columns})

    # Drop calculated columns
    calc_cols = ['Age', 'Tenure (Months)', 'Join Year', 'Join Month', 'Join Quarter',
                 'Exit Year', 'Exit Month', 'Probation Completed', 'Employment Type']
    save_df = save_df.drop(columns=[c for c in calc_cols if c in save_df.columns], errors='ignore')

    save_df.to_excel(file_path, index=False)
