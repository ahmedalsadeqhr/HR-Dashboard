import pandas as pd
import pytest
from unittest.mock import MagicMock, patch

from src.data_processing import merge_two_sources
from src.db import replace_employees


def _active(ids):
    rows = [{'JobNumber': 'hdr', 'parent_Gender': 'g', 'EntryDate': 'd', 'OIdDepartment': 'd'}]
    rows += [{'JobNumber': i, 'parent_Gender': 'Male', 'EntryDate': '2024-01-01',
              'OIdDepartment': 'EGSS'} for i in ids]
    return pd.DataFrame(rows)


def _leavers(ids, with_exit_date=True):
    rows = [{'JobNumber': 'hdr', 'ApprovalStatus': 'x', 'EntryDate': 'd', 'LastWorkDate': 'd',
             'TransitionTypeOID': 't'}]
    rows += [{'JobNumber': i, 'ApprovalStatus': 'Effective', 'EntryDate': '2023-01-01',
              'LastWorkDate': '2024-05-01', 'TransitionTypeOID': 'Resigned'} for i in ids]
    df = pd.DataFrame(rows)
    return df if with_exit_date else df.drop(columns=['LastWorkDate'])


def test_merge_keeps_active_row_when_id_in_both_files():
    merged = merge_two_sources(_active(['1', '2']), _leavers(['2', '3']))
    assert sorted(merged['Employee ID']) == ['1', '2', '3']
    assert merged.loc[merged['Employee ID'] == '2', 'Employee Status'].iloc[0] == 'Active'
    assert merged.attrs['duplicates_dropped'] == 1


def test_merge_drops_repeated_ids_within_a_file():
    merged = merge_two_sources(_active(['1', '1']), _leavers(['3']))
    assert len(merged) == 2
    assert merged.attrs['duplicates_dropped'] == 1


def test_merge_raises_clear_error_when_exit_date_missing():
    with pytest.raises(ValueError, match="Exit Date"):
        merge_two_sources(_active(['1']), _leavers(['3'], with_exit_date=False))


def _client(fail_on_insert_call=None, old_max=10):
    c = MagicMock()
    t = c.table.return_value
    t.select.return_value.order.return_value.limit.return_value.execute.return_value.data = (
        [{"id": old_max}] if old_max is not None else [])
    if fail_on_insert_call is not None:
        t.insert.return_value.execute.side_effect = RuntimeError("boom")
    return c, t


def test_replace_inserts_before_deleting_old_rows():
    c, t = _client()
    df = pd.DataFrame({"Gender": ["M", "F"]})
    with patch("src.db.get_supabase_client", return_value=c):
        replace_employees(df)
    names = [call[0] for call in t.method_calls if call[0] in ("insert", "delete")]
    assert names.index("insert") < names.index("delete")
    t.delete.return_value.lte.assert_called_once_with("id", 10)


def test_replace_failure_keeps_old_data_and_removes_partial_rows():
    c, t = _client(fail_on_insert_call=1)
    df = pd.DataFrame({"Gender": ["M", "F"]})
    with patch("src.db.get_supabase_client", return_value=c):
        with pytest.raises(RuntimeError):
            replace_employees(df)
    t.delete.return_value.gt.assert_called_once_with("id", 10)
    t.delete.return_value.lte.assert_not_called()


def _departed(rows):
    base = {'LookupPrefix_UserID_TransitionTypeOID': 'Voluntary Termination',
            'LookupPrefix_UserID_EntryDate': '2024-01-01', 'LookupPrefix_UserID_OIdDepartment': 'EGSS',
            'LookupPrefix_UserID_LastWorkDate': '2026-05-01',
            'abc-guid~POIdEmpAdmin-ExportName': 'Boss', 'Birthday': '1995-01-01'}
    hdr = {'LookupPrefix_UserID_JobNumber': 'Employee ID', 'Name': 'Name', 'Gender': 'Gender',
           **{k: 'h' for k in base}}
    return pd.DataFrame([hdr] + [{**base, **r} for r in rows])


def test_merge_supports_departed_employees_export():
    dep = _departed([
        {'LookupPrefix_UserID_JobNumber': '7', 'Name': 'A', 'Gender': 'Female'},
        {'LookupPrefix_UserID_JobNumber': '8', 'Name': 'B', 'Gender': 'Male'},
    ])
    merged = merge_two_sources(_active(['1']), dep)
    left = merged[merged['Employee Status'] == 'Departed']
    assert len(left) == 2
    assert set(left['Gender']) == {'Female', 'Male'}
    assert set(left['Line Manager']) == {'Boss'}
    assert left['Exit Type'].iloc[0] == 'Voluntary Termination'
    assert 'Exit Date' in merged.columns and 'Birthday Date' in merged.columns


def test_departed_export_keeps_latest_stint_per_employee():
    dep = _departed([
        {'LookupPrefix_UserID_JobNumber': '7', 'LookupPrefix_UserID_LastWorkDate': '2026-09-01'},
        {'LookupPrefix_UserID_JobNumber': '7', 'LookupPrefix_UserID_LastWorkDate': '2025-01-01'},
    ])
    merged = merge_two_sources(_active(['1']), dep)
    left = merged[merged['Employee Status'] == 'Departed']
    assert len(left) == 1 and str(left['Exit Date'].iloc[0]).startswith('2026-09-01')


def test_turnover_12m_formula():
    from src.data_processing import calculate_turnover_12m
    today = pd.Timestamp('2026-06-30')
    df = pd.DataFrame({
        # A, B active all year; C left inside window; D left before window; E joined inside window
        'Join Date': ['2024-01-01', '2024-01-01', '2024-01-01', '2024-01-01', '2026-03-01'],
        'Exit Date': [None, None, '2026-02-01', '2025-01-01', None],
    })
    r = calculate_turnover_12m(df, today)
    # headcount 2025-06-30: A,B,C = 3 ; headcount today: A,B,E = 3 ; avg 3 ; exits 1
    assert r['exits_12m'] == 1
    assert r['avg_headcount_12m'] == 3
    assert r['turnover_12m'] == pytest.approx(33.33, abs=0.01)


def test_turnover_12m_safe_without_exit_column_or_empty():
    from src.data_processing import calculate_turnover_12m
    assert calculate_turnover_12m(pd.DataFrame({'Join Date': ['2024-01-01']}))['turnover_12m'] == 0
    assert calculate_turnover_12m(pd.DataFrame(columns=['Join Date', 'Exit Date']))['exits_12m'] == 0


def test_chinese_team_names_are_normalised_to_english():
    from src.data_processing import process_data
    df = pd.DataFrame({
        'Employee Status': ['Active', 'Departed', 'Departed', 'Departed'],
        'Department': ['ME-EGSS-GCC01 Team', 'ME-EGSS-GCC01小组', 'KSA市场部', '阿教项目部'],
        'Join Date': ['2025-01-01'] * 4,
    })
    out = process_data(df)['Department'].tolist()
    assert out == ['ME-EGSS-GCC01 Team', 'ME-EGSS-GCC01 Team',
                   'KSA Marketing Department', 'Arabic Teaching Project Department']


def test_period_turnover_uses_average_headcount():
    from src.data_processing import calculate_period_turnover
    df = pd.DataFrame({
        'Employee Status': ['Active', 'Active', 'Departed', 'Departed'],
        'Join Date': ['2025-01-01'] * 4,
        'Exit Date': [None, None, '2026-02-10', '2025-06-01'],
    })
    out = calculate_period_turnover(df, 'M', 24, today='2026-03-31').set_index('Period')
    # Feb 2026: headcount start-of-month 3 (C still there), end 2 -> avg 2.5 ; 1 exit -> 40%
    assert out.loc['2026-02', 'Exits'] == 1
    assert out.loc['2026-02', 'Avg Headcount'] == 2.5
    assert out.loc['2026-02', 'Turnover Rate %'] == 40.0
    assert out.loc['2026-03', 'Turnover Rate %'] == 0.0
    q = calculate_period_turnover(df, 'Q', 8, today='2026-03-31').set_index('Period')
    assert q.loc['2026Q1', 'Exits'] == 1
