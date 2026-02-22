import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from src.data_processing import process_data, calculate_kpis, get_cohort_retention, get_manager_attrition


def _make_sample_df(n=20):
    """Create a sample HR dataframe for testing."""
    np.random.seed(42)
    today = datetime.now()
    rows = []
    for i in range(n):
        status = 'Active' if i % 3 != 0 else 'Departed'
        join_date = today - timedelta(days=np.random.randint(90, 1800))
        exit_date = join_date + timedelta(days=np.random.randint(30, 500)) if status == 'Departed' else pd.NaT
        rows.append({
            'Full Name': f'Employee {i}',
            'Gender': 'M' if i % 2 == 0 else 'F',
            'Birthday Date': today - timedelta(days=365 * np.random.randint(25, 55)),
            'Nationality': ['Egyptian', 'Saudi', 'Indian'][i % 3],
            'Department': ['IT', 'HR', 'Finance', 'Sales'][i % 4],
            'Position': ['Analyst', 'Manager', 'Director', 'Engineer'][i % 4],
            'Employee Status': status,
            'Join Date (yyyy/mm/dd)': join_date,
            'Exit Date yyyy/mm/dd': exit_date,
            'Exit Type': 'Resigned' if status == 'Departed' and i % 2 == 0 else ('Terminated' if status == 'Departed' else ''),
            'Exit Reason Category': 'Better Opportunity' if status == 'Departed' else '',
            'Type': ['Full time', 'Contract', 'Freelancer'][i % 3],
            'Vendor': ['Direct Hire', 'Agency A'][i % 2],
        })
    return pd.DataFrame(rows)


def test_process_data_creates_age():
    df = _make_sample_df()
    result = process_data(df)
    assert 'Age' in result.columns
    assert (result['Age'] > 0).any()


def test_process_data_creates_tenure():
    df = _make_sample_df()
    result = process_data(df)
    assert 'Tenure (Months)' in result.columns
    assert (result['Tenure (Months)'] > 0).any()


def test_process_data_creates_join_year():
    df = _make_sample_df()
    result = process_data(df)
    assert 'Join Year' in result.columns
    assert 'Join Month' in result.columns
    assert 'Join Quarter' in result.columns


def test_process_data_renames_columns():
    df = _make_sample_df()
    result = process_data(df)
    assert 'Join Date' in result.columns
    assert 'Exit Date' in result.columns


def test_process_data_employment_type():
    df = _make_sample_df()
    result = process_data(df)
    assert 'Employment Type' in result.columns


def test_calculate_kpis_returns_all_keys():
    df = process_data(_make_sample_df())
    kpis = calculate_kpis(df)
    expected_keys = ['total', 'active', 'departed', 'attrition_rate', 'retention_rate',
                     'avg_tenure', 'avg_age', 'contractor_ratio', 'nationality_count',
                     'gender_ratio', 'male_count', 'female_count', 'probation_pass_rate', 'growth_rate']
    for key in expected_keys:
        assert key in kpis, f"Missing KPI key: {key}"


def test_calculate_kpis_math():
    df = process_data(_make_sample_df())
    kpis = calculate_kpis(df)
    assert kpis['total'] == kpis['active'] + kpis['departed']
    assert 0 <= kpis['attrition_rate'] <= 100
    assert 0 <= kpis['retention_rate'] <= 100
    assert abs(kpis['attrition_rate'] + kpis['retention_rate'] - 100) < 0.1


def test_calculate_kpis_empty_df():
    df = process_data(_make_sample_df()).head(0)
    kpis = calculate_kpis(df)
    assert kpis['total'] == 0
    assert kpis['attrition_rate'] == 0


def test_cohort_retention():
    df = process_data(_make_sample_df())
    cohort = get_cohort_retention(df)
    assert len(cohort) > 0
    assert 'Join Year' in cohort.columns
    assert 'Retention Rate %' in cohort.columns


def test_cohort_retention_empty():
    df = pd.DataFrame({'Employee Status': []})
    cohort = get_cohort_retention(df)
    assert len(cohort) == 0


def test_manager_attrition_no_column():
    df = process_data(_make_sample_df())
    result = get_manager_attrition(df)
    assert len(result) == 0  # No manager CRM column


def test_manager_attrition_with_column():
    df = process_data(_make_sample_df())
    df['Direct Manager CRM while Resignation'] = ['MGR_A', 'MGR_B'] * (len(df) // 2)
    result = get_manager_attrition(df)
    if len(df[df['Employee Status'] == 'Departed']) > 0:
        assert len(result) > 0
        assert 'Manager CRM' in result.columns
        assert 'Departures' in result.columns


def test_gender_ratio_format():
    df = process_data(_make_sample_df())
    kpis = calculate_kpis(df)
    assert ':' in kpis['gender_ratio']
    parts = kpis['gender_ratio'].split(':')
    assert len(parts) == 2
    assert int(parts[0]) >= 0
    assert int(parts[1]) >= 0
