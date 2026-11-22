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
