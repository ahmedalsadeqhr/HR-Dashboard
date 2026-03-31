import pytest
import pandas as pd
from src.upload import detect_schema_changes, apply_column_mapping, validate_required_columns

REQUIRED = ["Gender", "Department", "Position", "Employee Status", "Exit Type"]


def test_detect_schema_changes_returns_empty_when_columns_match():
    """No changes detected when file columns match required columns exactly."""
    df = pd.DataFrame(columns=["Gender", "Department", "Position", "Employee Status", "Exit Type", "Join Date"])
    changes = detect_schema_changes(df, REQUIRED)
    assert changes == {}


def test_detect_schema_changes_flags_renamed_columns():
    """Flags columns that are missing from required but similar names exist in file."""
    df = pd.DataFrame(columns=["gender", "Department", "Position", "Employee Status", "Exit Type"])
    changes = detect_schema_changes(df, REQUIRED)
    # "gender" vs "Gender" — case mismatch should be detected
    assert "Gender" in changes


def test_apply_column_mapping_renames_columns():
    """apply_column_mapping() renames df columns according to the mapping dict."""
    df = pd.DataFrame({"Emp Status": ["Active"], "Dept": ["Tech"]})
    mapping = {"Emp Status": "Employee Status", "Dept": "Department"}
    result = apply_column_mapping(df, mapping)
    assert "Employee Status" in result.columns
    assert "Department" in result.columns
    assert "Emp Status" not in result.columns


def test_apply_column_mapping_skips_none_values():
    """Columns mapped to None are dropped from the dataframe."""
    df = pd.DataFrame({"Gender": ["M"], "UNKNOWN_COL": ["X"]})
    mapping = {"UNKNOWN_COL": None}
    result = apply_column_mapping(df, mapping)
    assert "UNKNOWN_COL" not in result.columns
    assert "Gender" in result.columns


def test_validate_required_columns_passes_when_all_present():
    """No error raised when all required columns are present."""
    df = pd.DataFrame(columns=["Gender", "Department", "Position", "Employee Status", "Exit Type"])
    missing = validate_required_columns(df, REQUIRED)
    assert missing == []


def test_validate_required_columns_returns_missing_list():
    """Returns list of missing required columns."""
    df = pd.DataFrame(columns=["Gender", "Department"])
    missing = validate_required_columns(df, REQUIRED)
    assert "Position" in missing
    assert "Employee Status" in missing
    assert "Exit Type" in missing


def test_prepare_upload_applies_mapping_and_converts_dates():
    """prepare_upload() applies column mapping and converts dates to ISO strings."""
    from src.upload import prepare_upload

    df = pd.DataFrame({
        "Emp Status": ["Active"],
        "Join Date": [pd.Timestamp("2023-01-15")]
    })
    mapping = {"Emp Status": "Employee Status"}
    result = prepare_upload(df, mapping)

    assert "Employee Status" in result.columns
    assert result["Join Date"].iloc[0] == "2023-01-15"
