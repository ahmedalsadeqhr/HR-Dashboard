"""Data processing pipeline for employee data."""

import pandas as pd
import streamlit as st
from datetime import datetime
from src.db import fetch_employees


def load_excel(file_path_or_buffer) -> pd.DataFrame:
    """Load employee data from an Excel file for local development fallback."""
    df = pd.read_excel(file_path_or_buffer)
    return process_data(df)


@st.cache_data(ttl=300)
def load_from_db() -> pd.DataFrame:
    """Load employee data from Supabase and process it. Cached for 5 minutes."""
    df = fetch_employees()
    if df.empty:
        return df
    return process_data(df)


def process_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and process raw employee data.
    Adds derived columns: Tenure (Months), Join Year, etc.
    """
    df = df.copy()

    # Parse date columns
    date_columns = ["Join Date", "Exit Date"]
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # Calculate Tenure (Months)
    if "Join Date" in df.columns:
        today = datetime.now()
        df["Tenure (Months)"] = (
            df["Join Date"].apply(
                lambda x: int((today - x).days / 30.44)
                if pd.notna(x)
                else None
            )
        )

    # Calculate Join Year
    if "Join Date" in df.columns:
        df["Join Year"] = df["Join Date"].dt.year

    # Clean Employee Status
    if "Employee Status" in df.columns:
        df["Employee Status"] = df["Employee Status"].str.strip()

    # Clean Department
    if "Department" in df.columns:
        df["Department"] = df["Department"].str.strip()

    # Clean Position
    if "Position" in df.columns:
        df["Position"] = df["Position"].str.strip()

    # Clean Gender
    if "Gender" in df.columns:
        df["Gender"] = df["Gender"].str.strip().str.upper()

    return df


def calculate_kpis(df: pd.DataFrame) -> dict:
    """
    Calculate key performance indicators from employee data.
    Returns a dictionary of KPI values.
    """
    if df.empty:
        return {}

    kpis = {}

    # Total employees
    if "Employee Status" in df.columns:
        kpis["total_employees"] = len(df)
        kpis["active_employees"] = len(df[df["Employee Status"] == "Active"])
        kpis["departed_employees"] = len(df[df["Employee Status"] == "Departed"])

    # Department breakdown
    if "Department" in df.columns:
        kpis["by_department"] = df["Department"].value_counts().to_dict()

    # Average tenure
    if "Tenure (Months)" in df.columns:
        avg_tenure = df["Tenure (Months)"].mean()
        kpis["avg_tenure_months"] = round(avg_tenure, 1) if pd.notna(avg_tenure) else 0

    # Resignation rate
    if "Employee Status" in df.columns and "Exit Type" in df.columns:
        departed = df[df["Employee Status"] == "Departed"]
        if len(departed) > 0:
            resignations = len(departed[departed["Exit Type"] == "Resignation"])
            kpis["resignation_count"] = resignations
            kpis["resignation_rate"] = round(
                (resignations / len(departed)) * 100, 1
            )

    return kpis
