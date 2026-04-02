"""Upload pipeline with column mapping and validation."""

import pandas as pd


def detect_schema_changes(df: pd.DataFrame, required: list[str]) -> dict[str, str | None]:
    """
    Compare df columns against required columns.
    Returns a mapping of {required_col: best_guess_from_file} for any that are missing.
    best_guess is the closest match found in df.columns (case-insensitive), or None.
    """
    file_cols = [str(c) for c in df.columns]
    file_cols_lower = {c.lower(): c for c in file_cols}
    changes = {}
    for req in required:
        if req not in file_cols:
            # Try case-insensitive match
            guess = file_cols_lower.get(req.lower())
            changes[req] = guess  # None if no guess found
    return changes


def apply_column_mapping(df: pd.DataFrame, mapping: dict[str, str | None]) -> pd.DataFrame:
    """
    Rename or drop columns based on mapping.
    mapping: {current_col_name: target_col_name} — None means drop.
    """
    rename = {k: v for k, v in mapping.items() if v is not None and k in df.columns}
    drop = [k for k, v in mapping.items() if v is None and k in df.columns]
    df = df.rename(columns=rename)
    df = df.drop(columns=drop, errors="ignore")
    return df


def validate_required_columns(df: pd.DataFrame, required: list[str]) -> list[str]:
    """Return list of required columns missing from df. Empty list means valid."""
    return [col for col in required if col not in df.columns]


def prepare_upload(df: pd.DataFrame, mapping: dict[str, str | None]) -> pd.DataFrame:
    """Apply column mapping then return the processed dataframe ready for DB insert."""
    import datetime
    df = apply_column_mapping(df, mapping).copy()
    # Convert all datetime-like columns to ISO strings for JSON serialisation
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.strftime("%Y-%m-%d").where(df[col].notna(), None)
        else:
            # Handle object columns containing Python datetime/date objects
            df[col] = df[col].apply(
                lambda v: v.strftime("%Y-%m-%d")
                if isinstance(v, (datetime.datetime, datetime.date))
                else v
            )
    # Replace NaN/NaT with None for JSON compatibility
    df = df.where(pd.notnull(df), None)
    return df
