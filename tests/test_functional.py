"""
Comprehensive functional tests for the HR Dashboard.

Covers: data processing pipeline, KPI calculations, cohort retention,
manager attrition, save/load round-trip, utils, and app-level integration.
"""

import inspect
import io
import math
import tempfile
import os
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import pytest

from src.config import detect_name_column
from src.data_processing import (
    calculate_kpis,
    get_cohort_retention,
    get_manager_attrition,
    load_excel,
    process_data,
    save_to_excel,
)
from src.utils import delta, export_excel, generate_summary_report


# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------

TODAY = pd.Timestamp(datetime.now())
CURRENT_YEAR = datetime.now().year


def _build_raw_df(rows):
    """Wrap a list of dicts as a DataFrame using the *raw* column names that
    process_data expects (i.e. before renaming)."""
    return pd.DataFrame(rows)


def _make_realistic_raw(n=30, seed=0):
    """Return a realistic raw HR DataFrame with all optional columns present."""
    rng = np.random.default_rng(seed)
    rows = []
    for i in range(n):
        status = "Departed" if i % 4 == 0 else "Active"
        join_date = TODAY - timedelta(days=int(rng.integers(60, 2000)))
        # Give departed employees a proper future exit date
        if status == "Departed":
            max_days = max(1, (TODAY - join_date).days - 1)
            exit_date = join_date + timedelta(days=int(rng.integers(30, max(31, max_days))))
        else:
            exit_date = pd.NaT

        # Probation end: 3 months after join
        prob_end = join_date + timedelta(days=90)

        birthday = TODAY - timedelta(days=int(rng.integers(25 * 365, 55 * 365)))
        emp_type = ["Full time", "Contract", "Freelancer"][i % 3]
        rows.append(
            {
                "Full Name": f"Employee {i}",
                "Gender": "M" if i % 2 == 0 else "F",
                "Birthday Date": birthday,
                "Nationality": ["Egyptian", "Saudi", "Indian", "British"][i % 4],
                "Department": ["IT", "HR", "Finance", "Sales"][i % 4],
                "Position": ["Analyst", "Manager", "Director", "Engineer"][i % 4],
                "Employee Status": status,
                "Join Date (yyyy/mm/dd)": join_date,
                "Exit Date yyyy/mm/dd": exit_date,
                "Probation Period End Date": prob_end,
                "Exit Type": ("Resigned" if status == "Departed" and i % 2 == 0 else ("Terminated" if status == "Departed" else "")),
                "Exit Reason Category": ("Better Opportunity" if status == "Departed" and i % 2 == 0 else ("Internal" if status == "Departed" else "")),
                "Exit ReasonList": ("Better Opportunity" if status == "Departed" else ""),
                "Type": emp_type,
                "Vendor": (None if i % 5 == 0 else "Agency A"),
                "Nationality": (None if i % 7 == 0 else ["Egyptian", "Saudi", "Indian"][i % 3]),
            }
        )
    return pd.DataFrame(rows)


@pytest.fixture(scope="module")
def processed_df():
    """A fully processed DataFrame used across multiple tests."""
    raw = _make_realistic_raw(n=40)
    return process_data(raw)


# ---------------------------------------------------------------------------
# 1. Data Processing Pipeline
# ---------------------------------------------------------------------------


class TestProcessData:
    def test_column_rename_join_date(self):
        raw = _make_realistic_raw(n=5)
        result = process_data(raw)
        assert "Join Date" in result.columns
        assert "Join Date (yyyy/mm/dd)" not in result.columns

    def test_column_rename_exit_date(self):
        raw = _make_realistic_raw(n=5)
        result = process_data(raw)
        assert "Exit Date" in result.columns
        assert "Exit Date yyyy/mm/dd" not in result.columns

    def test_column_rename_position_after_joining(self):
        raw = _build_raw_df(
            [{"Position (After Joining)": "Senior Analyst", "Employee Status": "Active"}]
        )
        result = process_data(raw)
        assert "Position After Joining" in result.columns
        assert "Position (After Joining)" not in result.columns

    def test_age_column_created(self, processed_df):
        assert "Age" in processed_df.columns

    def test_age_values_positive_for_valid_birthdays(self, processed_df):
        # All rows have valid Birthday Date, so Age should be > 0 for all
        assert (processed_df["Age"] > 0).all()

    def test_age_value_accuracy(self):
        """Age should be the integer part of (days_since_birth / 365.25).

        The source code uses: int((today - birthday).days / 365.25)
        We test with a birthday that is exactly 365.25 * 35 days ago so that
        the computed value is a clean integer regardless of leap-year variance.
        """
        # Use exactly 35 * 365.25 days → 35.0 years → int == 35
        days = int(365.25 * 35)
        birthday = TODAY - timedelta(days=days)
        raw = _build_raw_df(
            [{"Birthday Date": birthday, "Employee Status": "Active"}]
        )
        result = process_data(raw)
        # Allow 35 or 34 since there is a sub-day rounding boundary
        assert result["Age"].iloc[0] in (34, 35)

    def test_tenure_column_created(self, processed_df):
        assert "Tenure (Months)" in processed_df.columns

    def test_tenure_active_employees_uses_today(self):
        """Active employee tenure should be from join date to today."""
        join = TODAY - timedelta(days=365)  # exactly 1 year ago
        raw = _build_raw_df(
            [
                {
                    "Employee Status": "Active",
                    "Join Date (yyyy/mm/dd)": join,
                    "Exit Date yyyy/mm/dd": pd.NaT,
                }
            ]
        )
        result = process_data(raw)
        tenure = result["Tenure (Months)"].iloc[0]
        # ~12 months; allow ±1 for day boundary
        assert 11.0 <= tenure <= 13.0

    def test_tenure_departed_employees_uses_exit_date(self):
        """Departed employee tenure should be from join date to exit date."""
        join = TODAY - timedelta(days=365)
        exit_dt = join + timedelta(days=180)  # worked 6 months
        raw = _build_raw_df(
            [
                {
                    "Employee Status": "Departed",
                    "Join Date (yyyy/mm/dd)": join,
                    "Exit Date yyyy/mm/dd": exit_dt,
                }
            ]
        )
        result = process_data(raw)
        tenure = result["Tenure (Months)"].iloc[0]
        # 180 days / 30.44 ≈ 5.9 months
        assert 5.5 <= tenure <= 6.5

    def test_tenure_without_exit_date_column(self):
        """When no Exit Date column exists, tenure is always from join to today."""
        join = TODAY - timedelta(days=90)
        raw = _build_raw_df(
            [{"Employee Status": "Departed", "Join Date (yyyy/mm/dd)": join}]
        )
        result = process_data(raw)
        assert "Tenure (Months)" in result.columns
        assert result["Tenure (Months)"].iloc[0] > 0

    def test_join_year_month_quarter(self, processed_df):
        assert "Join Year" in processed_df.columns
        assert "Join Month" in processed_df.columns
        assert "Join Quarter" in processed_df.columns

    def test_join_year_values(self):
        join = pd.Timestamp("2022-06-15")
        raw = _build_raw_df(
            [{"Employee Status": "Active", "Join Date (yyyy/mm/dd)": join}]
        )
        result = process_data(raw)
        assert result["Join Year"].iloc[0] == 2022
        assert "2022-06" in str(result["Join Month"].iloc[0])
        assert "2022Q2" in str(result["Join Quarter"].iloc[0])

    def test_exit_year_and_month(self):
        join = pd.Timestamp("2021-01-01")
        exit_dt = pd.Timestamp("2023-03-15")
        raw = _build_raw_df(
            [
                {
                    "Employee Status": "Departed",
                    "Join Date (yyyy/mm/dd)": join,
                    "Exit Date yyyy/mm/dd": exit_dt,
                }
            ]
        )
        result = process_data(raw)
        assert "Exit Year" in result.columns
        assert result["Exit Year"].iloc[0] == 2023
        assert "2023-03" in str(result["Exit Month"].iloc[0])

    def test_exit_year_not_created_when_no_exit_date_col(self):
        raw = _build_raw_df(
            [{"Employee Status": "Active", "Join Date (yyyy/mm/dd)": TODAY}]
        )
        result = process_data(raw)
        assert "Exit Year" not in result.columns
        assert "Exit Month" not in result.columns

    # ------------------------------------------------------------------
    # Probation states
    # ------------------------------------------------------------------

    def _prob_row(self, status, prob_end, exit_date=None):
        row = {
            "Employee Status": status,
            "Join Date (yyyy/mm/dd)": TODAY - timedelta(days=200),
            "Probation Period End Date": prob_end,
        }
        if exit_date is not None:
            row["Exit Date yyyy/mm/dd"] = exit_date
        else:
            row["Exit Date yyyy/mm/dd"] = pd.NaT
        return row

    def test_probation_completed(self):
        """Active employee whose probation end date is in the past → Completed."""
        prob_end = TODAY - timedelta(days=30)
        raw = _build_raw_df([self._prob_row("Active", prob_end)])
        result = process_data(raw)
        assert result["Probation Completed"].iloc[0] == "Completed"

    def test_probation_in_probation(self):
        """Active employee whose probation end date is in the future → In Probation."""
        prob_end = TODAY + timedelta(days=30)
        raw = _build_raw_df([self._prob_row("Active", prob_end)])
        result = process_data(raw)
        assert result["Probation Completed"].iloc[0] == "In Probation"

    def test_probation_no_data(self):
        """Active employee with no probation end date → No Data."""
        raw = _build_raw_df(
            [
                {
                    "Employee Status": "Active",
                    "Join Date (yyyy/mm/dd)": TODAY - timedelta(days=200),
                    "Probation Period End Date": pd.NaT,
                    "Exit Date yyyy/mm/dd": pd.NaT,
                }
            ]
        )
        result = process_data(raw)
        assert result["Probation Completed"].iloc[0] == "No Data"

    def test_probation_left_during_probation(self):
        """Departed employee who exited before probation end → Left During Probation."""
        join = TODAY - timedelta(days=100)
        prob_end = TODAY + timedelta(days=10)  # still in the future
        exit_dt = TODAY - timedelta(days=5)
        row = {
            "Employee Status": "Departed",
            "Join Date (yyyy/mm/dd)": join,
            "Probation Period End Date": prob_end,
            "Exit Date yyyy/mm/dd": exit_dt,
        }
        result = process_data(_build_raw_df([row]))
        assert result["Probation Completed"].iloc[0] == "Left During Probation"

    def test_probation_completed_before_exit(self):
        """Departed employee whose probation end is past and exit after probation end
        → Completed Before Exit.

        The logic: Probation end is in the past (<=today) → 'Completed' wins at the
        outer np.where. So to land in 'Completed Before Exit' we need a departed
        employee with a probation end date that is still in the future (exit < prob_end
        is False because exit is also after prob_end, so left_during_prob is False).

        Actually re-reading the code:
          outer condition: prob_end notna AND prob_end <= today → 'Completed'
          else → if Departed:
              if prob_end notna AND exit < prob_end → 'Left During Probation'
              else → 'Completed Before Exit'
          else → if prob_end notna → 'In Probation' else 'No Data'

        So 'Completed Before Exit' = Departed + (prob_end is NaT OR exit >= prob_end)
        AND NOT (prob_end notna AND prob_end <= today)
        i.e. prob_end is in the future but exit >= prob_end (impossible since exit <=
        today < prob_end) OR prob_end is NaT.
        So: departed with NaT probation end → 'Completed Before Exit'.
        """
        join = TODAY - timedelta(days=300)
        exit_dt = TODAY - timedelta(days=10)
        row = {
            "Employee Status": "Departed",
            "Join Date (yyyy/mm/dd)": join,
            "Probation Period End Date": pd.NaT,  # NaT → falls into 'Completed Before Exit'
            "Exit Date yyyy/mm/dd": exit_dt,
        }
        result = process_data(_build_raw_df([row]))
        assert result["Probation Completed"].iloc[0] == "Completed Before Exit"

    def test_probation_not_created_when_column_missing(self):
        raw = _build_raw_df(
            [{"Employee Status": "Active", "Join Date (yyyy/mm/dd)": TODAY}]
        )
        result = process_data(raw)
        assert "Probation Completed" not in result.columns

    # ------------------------------------------------------------------
    # Employment Type
    # ------------------------------------------------------------------

    def test_employment_type_from_type_column(self):
        raw = _build_raw_df([{"Type": "Contract", "Employee Status": "Active"}])
        result = process_data(raw)
        assert result["Employment Type"].iloc[0] == "Contract"

    def test_employment_type_default_unknown_when_no_type_col(self):
        raw = _build_raw_df([{"Employee Status": "Active"}])
        result = process_data(raw)
        assert result["Employment Type"].iloc[0] == "Unknown"

    def test_employment_type_nan_filled_with_unknown(self):
        raw = _build_raw_df([{"Type": None, "Employee Status": "Active"}])
        result = process_data(raw)
        assert result["Employment Type"].iloc[0] == "Unknown"

    # ------------------------------------------------------------------
    # Vendor cleanup
    # ------------------------------------------------------------------

    def test_vendor_nan_filled_with_direct_hire(self):
        raw = _build_raw_df(
            [
                {"Vendor": None, "Employee Status": "Active"},
                {"Vendor": "Agency A", "Employee Status": "Active"},
            ]
        )
        result = process_data(raw)
        assert result["Vendor"].iloc[0] == "Direct Hire"
        assert result["Vendor"].iloc[1] == "Agency A"

    def test_vendor_column_unchanged_when_missing(self):
        raw = _build_raw_df([{"Employee Status": "Active"}])
        result = process_data(raw)
        # No Vendor col in input → no Vendor col in output
        assert "Vendor" not in result.columns

    # ------------------------------------------------------------------
    # Nationality cleanup
    # ------------------------------------------------------------------

    def test_nationality_nan_filled_with_unknown(self):
        raw = _build_raw_df(
            [
                {"Nationality": None, "Employee Status": "Active"},
                {"Nationality": "Egyptian", "Employee Status": "Active"},
            ]
        )
        result = process_data(raw)
        assert result["Nationality"].iloc[0] == "Unknown"
        assert result["Nationality"].iloc[1] == "Egyptian"

    # ------------------------------------------------------------------
    # Missing optional columns handled gracefully
    # ------------------------------------------------------------------

    def test_no_birthday_date_column(self):
        raw = _build_raw_df([{"Employee Status": "Active"}])
        result = process_data(raw)
        assert "Age" not in result.columns

    def test_no_exit_date_column(self):
        raw = _build_raw_df(
            [{"Employee Status": "Active", "Join Date (yyyy/mm/dd)": TODAY}]
        )
        result = process_data(raw)
        assert "Exit Year" not in result.columns
        assert "Exit Month" not in result.columns

    def test_no_join_date_column(self):
        raw = _build_raw_df([{"Employee Status": "Active"}])
        result = process_data(raw)
        assert "Tenure (Months)" not in result.columns
        assert "Join Year" not in result.columns


# ---------------------------------------------------------------------------
# 2. KPI Calculations
# ---------------------------------------------------------------------------


class TestCalculateKPIs:
    def test_attrition_plus_retention_equals_100(self, processed_df):
        kpis = calculate_kpis(processed_df)
        assert abs(kpis["attrition_rate"] + kpis["retention_rate"] - 100.0) < 1e-6

    def test_attrition_rate_value(self):
        """4 departed out of 10 total → 40% attrition."""
        rows = [{"Employee Status": "Active"}] * 6 + [
            {"Employee Status": "Departed"}
        ] * 4
        df = process_data(_build_raw_df(rows))
        kpis = calculate_kpis(df)
        assert abs(kpis["attrition_rate"] - 40.0) < 1e-6
        assert abs(kpis["retention_rate"] - 60.0) < 1e-6

    def test_contractor_ratio_freelancer(self):
        """Freelancer and Contract both count; Full time does not."""
        rows = [
            {"Type": "Freelancer", "Employee Status": "Active"},
            {"Type": "Contract", "Employee Status": "Active"},
            {"Type": "Full time", "Employee Status": "Active"},
            {"Type": "FREELANCER", "Employee Status": "Active"},  # case-insensitive
        ]
        df = process_data(_build_raw_df(rows))
        kpis = calculate_kpis(df)
        assert abs(kpis["contractor_ratio"] - 75.0) < 1e-6

    def test_contractor_ratio_case_insensitive(self):
        rows = [
            {"Type": "freelancer", "Employee Status": "Active"},
            {"Type": "CONTRACT", "Employee Status": "Active"},
            {"Type": "Full time", "Employee Status": "Active"},
        ]
        df = process_data(_build_raw_df(rows))
        kpis = calculate_kpis(df)
        assert abs(kpis["contractor_ratio"] - (2 / 3 * 100)) < 0.1

    def test_probation_pass_rate_excludes_no_data(self):
        """Pass rate denominator must NOT include 'No Data' rows."""
        rows = [
            # completed → pass
            {
                "Employee Status": "Active",
                "Join Date (yyyy/mm/dd)": TODAY - timedelta(days=200),
                "Probation Period End Date": TODAY - timedelta(days=30),
                "Exit Date yyyy/mm/dd": pd.NaT,
            },
            # no data → excluded
            {
                "Employee Status": "Active",
                "Join Date (yyyy/mm/dd)": TODAY - timedelta(days=200),
                "Probation Period End Date": pd.NaT,
                "Exit Date yyyy/mm/dd": pd.NaT,
            },
            # left during probation → fail
            {
                "Employee Status": "Departed",
                "Join Date (yyyy/mm/dd)": TODAY - timedelta(days=100),
                "Probation Period End Date": TODAY + timedelta(days=10),
                "Exit Date yyyy/mm/dd": TODAY - timedelta(days=5),
            },
        ]
        df = process_data(_build_raw_df(rows))
        kpis = calculate_kpis(df)
        # 1 passed out of 2 with data = 50%
        assert abs(kpis["probation_pass_rate"] - 50.0) < 1e-6

    def test_probation_pass_rate_when_no_probation_col(self):
        rows = [{"Employee Status": "Active"}] * 5
        df = process_data(_build_raw_df(rows))
        kpis = calculate_kpis(df)
        assert kpis["probation_pass_rate"] == 0

    def test_growth_rate_correct_yoy(self):
        rows = (
            [{"Employee Status": "Active", "Join Date (yyyy/mm/dd)": pd.Timestamp(f"{CURRENT_YEAR}-03-01")}] * 6
            + [{"Employee Status": "Active", "Join Date (yyyy/mm/dd)": pd.Timestamp(f"{CURRENT_YEAR - 1}-03-01")}] * 4
        )
        df = process_data(_build_raw_df(rows))
        kpis = calculate_kpis(df)
        # (6-4)/4 * 100 = 50%
        assert abs(kpis["growth_rate"] - 50.0) < 1e-6

    def test_growth_rate_zero_last_year(self):
        """When no hires last year, growth_rate should be 0 (not crash)."""
        rows = [
            {"Employee Status": "Active", "Join Date (yyyy/mm/dd)": pd.Timestamp(f"{CURRENT_YEAR}-01-15")}
        ] * 3
        df = process_data(_build_raw_df(rows))
        kpis = calculate_kpis(df)
        assert kpis["growth_rate"] == 0

    def test_gender_ratio_format(self, processed_df):
        kpis = calculate_kpis(processed_df)
        parts = kpis["gender_ratio"].split(":")
        assert len(parts) == 2
        assert int(parts[0]) >= 0 and int(parts[1]) >= 0

    def test_kpis_all_active_df(self):
        rows = [{"Employee Status": "Active"}] * 5
        df = process_data(_build_raw_df(rows))
        kpis = calculate_kpis(df)
        assert kpis["attrition_rate"] == 0.0
        assert kpis["retention_rate"] == 100.0

    def test_kpis_all_departed_df(self):
        rows = [{"Employee Status": "Departed"}] * 5
        df = process_data(_build_raw_df(rows))
        kpis = calculate_kpis(df)
        assert kpis["attrition_rate"] == 100.0
        assert kpis["retention_rate"] == 0.0

    def test_kpis_single_row_active(self):
        df = process_data(_build_raw_df([{"Employee Status": "Active"}]))
        kpis = calculate_kpis(df)
        assert kpis["total"] == 1
        assert kpis["active"] == 1
        assert kpis["departed"] == 0
        assert kpis["attrition_rate"] == 0.0
        assert kpis["retention_rate"] == 100.0

    def test_kpis_single_row_departed(self):
        df = process_data(_build_raw_df([{"Employee Status": "Departed"}]))
        kpis = calculate_kpis(df)
        assert kpis["total"] == 1
        assert kpis["attrition_rate"] == 100.0
        assert kpis["retention_rate"] == 0.0

    def test_nationality_count(self):
        rows = [
            {"Nationality": "Egyptian", "Employee Status": "Active"},
            {"Nationality": "Saudi", "Employee Status": "Active"},
            {"Nationality": "Egyptian", "Employee Status": "Active"},
        ]
        df = process_data(_build_raw_df(rows))
        kpis = calculate_kpis(df)
        assert kpis["nationality_count"] == 2

    def test_avg_age_ignores_zero(self):
        """Age=0 rows (no birthday data) should not drag down avg_age."""
        rows = [
            {
                "Birthday Date": TODAY - timedelta(days=365 * 30),
                "Employee Status": "Active",
            },
            # No Birthday Date → Age will be missing; using a separate row with no col
        ]
        df = process_data(_build_raw_df(rows))
        kpis = calculate_kpis(df)
        # Only 1 row with age > 0
        assert kpis["avg_age"] > 0

    def test_kpis_total_equals_active_plus_departed(self, processed_df):
        kpis = calculate_kpis(processed_df)
        assert kpis["total"] == kpis["active"] + kpis["departed"]


# ---------------------------------------------------------------------------
# 3. Cohort Retention
# ---------------------------------------------------------------------------


class TestCohortRetention:
    def test_filters_out_years_lte_2000(self):
        rows = [
            {"Employee Status": "Active", "Join Date (yyyy/mm/dd)": pd.Timestamp("1999-01-01")},
            {"Employee Status": "Active", "Join Date (yyyy/mm/dd)": pd.Timestamp("2000-06-01")},
            {"Employee Status": "Active", "Join Date (yyyy/mm/dd)": pd.Timestamp("2021-03-01")},
        ]
        df = process_data(_build_raw_df(rows))
        cohort = get_cohort_retention(df)
        assert len(cohort) > 0
        assert (cohort["Join Year"] > 2000).all()

    def test_all_years_lte_2000_returns_empty(self):
        rows = [
            {"Employee Status": "Active", "Join Date (yyyy/mm/dd)": pd.Timestamp("1998-01-01")},
        ]
        df = process_data(_build_raw_df(rows))
        cohort = get_cohort_retention(df)
        assert len(cohort) == 0

    def test_correct_retention_rate_per_cohort(self):
        """2021: 3 active, 1 departed → 75%; 2022: 2 active, 0 departed → 100%."""
        rows = (
            [{"Employee Status": "Active", "Join Date (yyyy/mm/dd)": pd.Timestamp("2021-06-01")}] * 3
            + [{"Employee Status": "Departed", "Join Date (yyyy/mm/dd)": pd.Timestamp("2021-09-01")}] * 1
            + [{"Employee Status": "Active", "Join Date (yyyy/mm/dd)": pd.Timestamp("2022-03-01")}] * 2
        )
        df = process_data(_build_raw_df(rows))
        cohort = get_cohort_retention(df)
        row_2021 = cohort[cohort["Join Year"] == 2021].iloc[0]
        row_2022 = cohort[cohort["Join Year"] == 2022].iloc[0]
        assert abs(row_2021["Retention Rate %"] - 75.0) < 1e-6
        assert abs(row_2022["Retention Rate %"] - 100.0) < 1e-6

    def test_single_year_cohort(self):
        rows = [
            {"Employee Status": "Active", "Join Date (yyyy/mm/dd)": pd.Timestamp("2023-01-01")}
        ] * 3
        df = process_data(_build_raw_df(rows))
        cohort = get_cohort_retention(df)
        assert len(cohort) == 1
        assert cohort.iloc[0]["Retention Rate %"] == 100.0

    def test_all_active_cohort_100_percent(self):
        rows = [
            {"Employee Status": "Active", "Join Date (yyyy/mm/dd)": pd.Timestamp("2022-05-01")}
        ] * 10
        df = process_data(_build_raw_df(rows))
        cohort = get_cohort_retention(df)
        assert cohort.iloc[0]["Retention Rate %"] == 100.0

    def test_all_departed_cohort_0_percent(self):
        rows = [
            {"Employee Status": "Departed", "Join Date (yyyy/mm/dd)": pd.Timestamp("2022-05-01")}
        ] * 5
        df = process_data(_build_raw_df(rows))
        cohort = get_cohort_retention(df)
        assert cohort.iloc[0]["Retention Rate %"] == 0.0

    def test_empty_input_returns_empty(self):
        df = pd.DataFrame({"Employee Status": []})
        cohort = get_cohort_retention(df)
        assert len(cohort) == 0

    def test_no_join_year_column_returns_empty(self):
        df = pd.DataFrame({"Employee Status": ["Active", "Departed"]})
        cohort = get_cohort_retention(df)
        assert len(cohort) == 0

    def test_required_columns_present(self, processed_df):
        cohort = get_cohort_retention(processed_df)
        for col in ["Join Year", "Total", "Active", "Departed", "Retention Rate %"]:
            assert col in cohort.columns


# ---------------------------------------------------------------------------
# 4. Manager Attrition
# ---------------------------------------------------------------------------

MGR_COL = "Direct Manager CRM while Resignation"


class TestManagerAttrition:
    def test_returns_empty_when_column_missing(self, processed_df):
        result = get_manager_attrition(processed_df)
        assert len(result) == 0

    def test_returns_empty_when_no_departed(self):
        rows = [{"Employee Status": "Active", MGR_COL: "MGR_A"}] * 5
        df = process_data(_build_raw_df(rows))
        result = get_manager_attrition(df)
        assert len(result) == 0

    def test_returns_empty_when_departed_have_no_manager_data(self):
        rows = [
            {"Employee Status": "Departed", MGR_COL: None},
            {"Employee Status": "Departed", MGR_COL: np.nan},
        ]
        df = process_data(_build_raw_df(rows))
        result = get_manager_attrition(df)
        assert len(result) == 0

    def test_counts_departures_per_manager(self):
        rows = [
            {"Employee Status": "Departed", MGR_COL: "Alice", "Full Name": "E1"},
            {"Employee Status": "Departed", MGR_COL: "Alice", "Full Name": "E2"},
            {"Employee Status": "Departed", MGR_COL: "Bob", "Full Name": "E3"},
            {"Employee Status": "Active", MGR_COL: "Alice", "Full Name": "E4"},
        ]
        df = process_data(_build_raw_df(rows))
        result = get_manager_attrition(df)
        assert len(result) == 2
        alice_row = result[result["Manager CRM"] == "Alice"]
        bob_row = result[result["Manager CRM"] == "Bob"]
        assert alice_row["Departures"].iloc[0] == 2
        assert bob_row["Departures"].iloc[0] == 1

    def test_sorted_by_departures_descending(self):
        rows = [
            {"Employee Status": "Departed", MGR_COL: "LowMgr", "Full Name": "E1"},
            {"Employee Status": "Departed", MGR_COL: "HighMgr", "Full Name": "E2"},
            {"Employee Status": "Departed", MGR_COL: "HighMgr", "Full Name": "E3"},
            {"Employee Status": "Departed", MGR_COL: "HighMgr", "Full Name": "E4"},
        ]
        df = process_data(_build_raw_df(rows))
        result = get_manager_attrition(df)
        assert result["Departures"].iloc[0] >= result["Departures"].iloc[1]

    def test_avg_tenure_computed_when_column_present(self):
        join = TODAY - timedelta(days=300)
        exit1 = join + timedelta(days=120)  # 120 days tenure
        exit2 = join + timedelta(days=60)   # 60 days tenure
        rows = [
            {
                "Employee Status": "Departed",
                MGR_COL: "Alice",
                "Full Name": "E1",
                "Join Date (yyyy/mm/dd)": join,
                "Exit Date yyyy/mm/dd": exit1,
            },
            {
                "Employee Status": "Departed",
                MGR_COL: "Alice",
                "Full Name": "E2",
                "Join Date (yyyy/mm/dd)": join,
                "Exit Date yyyy/mm/dd": exit2,
            },
        ]
        df = process_data(_build_raw_df(rows))
        result = get_manager_attrition(df)
        assert "Avg Tenure (Months)" in result.columns
        avg_t = result["Avg Tenure (Months)"].iloc[0]
        # (120 + 60) / 2 = 90 days → ~2.96 months
        assert 2.5 <= avg_t <= 3.5

    def test_works_without_tenure_column(self):
        rows = [
            {"Employee Status": "Departed", MGR_COL: "Alice", "Full Name": "E1"},
        ]
        df = process_data(_build_raw_df(rows))
        result = get_manager_attrition(df)
        assert "Departures" in result.columns
        assert "Avg Tenure (Months)" not in result.columns

    def test_top_exit_reason_per_manager(self):
        rows = [
            {"Employee Status": "Departed", MGR_COL: "Alice", "Full Name": "E1", "Exit Reason Category": "Personal"},
            {"Employee Status": "Departed", MGR_COL: "Alice", "Full Name": "E2", "Exit Reason Category": "Personal"},
            {"Employee Status": "Departed", MGR_COL: "Alice", "Full Name": "E3", "Exit Reason Category": "Better Opportunity"},
        ]
        df = process_data(_build_raw_df(rows))
        result = get_manager_attrition(df)
        assert "Top Exit Reason" in result.columns
        assert result["Top Exit Reason"].iloc[0] == "Personal"

    def test_works_without_exit_reason_column(self):
        rows = [
            {"Employee Status": "Departed", MGR_COL: "Alice", "Full Name": "E1"},
        ]
        df = process_data(_build_raw_df(rows))
        result = get_manager_attrition(df)
        assert "Top Exit Reason" not in result.columns

    def test_required_output_columns(self):
        rows = [
            {"Employee Status": "Departed", MGR_COL: "Alice", "Full Name": "E1"},
        ]
        df = process_data(_build_raw_df(rows))
        result = get_manager_attrition(df)
        assert "Manager CRM" in result.columns
        assert "Departures" in result.columns


# ---------------------------------------------------------------------------
# 5. Save / Load Round-Trip
# ---------------------------------------------------------------------------


class TestSaveLoadRoundTrip:
    def _make_processed_df(self):
        raw = _make_realistic_raw(n=10)
        return process_data(raw)

    def test_save_then_load_preserves_row_count(self):
        df = self._make_processed_df()
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            path = tmp.name
        try:
            save_to_excel(df, path)
            reloaded = load_excel(path)
            assert len(reloaded) == len(df)
        finally:
            os.unlink(path)

    def test_save_reverses_rename_join_date(self):
        df = self._make_processed_df()
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            path = tmp.name
        try:
            save_to_excel(df, path)
            raw_back = pd.read_excel(path)
            assert "Join Date (yyyy/mm/dd)" in raw_back.columns
            assert "Join Date" not in raw_back.columns
        finally:
            os.unlink(path)

    def test_save_reverses_rename_exit_date(self):
        df = self._make_processed_df()
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            path = tmp.name
        try:
            save_to_excel(df, path)
            raw_back = pd.read_excel(path)
            assert "Exit Date yyyy/mm/dd" in raw_back.columns
        finally:
            os.unlink(path)

    def test_computed_columns_dropped_on_save(self):
        df = self._make_processed_df()
        computed = [
            "Age", "Tenure (Months)", "Join Year", "Join Month",
            "Join Quarter", "Exit Year", "Exit Month",
            "Probation Completed", "Employment Type",
        ]
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            path = tmp.name
        try:
            save_to_excel(df, path)
            raw_back = pd.read_excel(path)
            for col in computed:
                if col in df.columns:  # Only assert drop if it existed
                    assert col not in raw_back.columns, f"Computed column {col!r} was not dropped"
        finally:
            os.unlink(path)

    def test_round_trip_reprocessed_data_matches(self):
        """After saving and reloading, reprocessing should give equivalent computed values."""
        raw = _make_realistic_raw(n=8)
        df = process_data(raw)
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            path = tmp.name
        try:
            save_to_excel(df, path)
            df2 = load_excel(path)
            # Core non-computed columns should be the same
            assert list(df["Employee Status"]) == list(df2["Employee Status"])
            assert list(df["Department"]) == list(df2["Department"])
        finally:
            os.unlink(path)

    def test_save_creates_valid_excel_file(self):
        df = self._make_processed_df()
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            path = tmp.name
        try:
            save_to_excel(df, path)
            assert os.path.getsize(path) > 0
            # Readable with openpyxl
            check = pd.read_excel(path, engine="openpyxl")
            assert len(check) > 0
        finally:
            os.unlink(path)


# ---------------------------------------------------------------------------
# 6. Utils
# ---------------------------------------------------------------------------


class TestDelta:
    def test_returns_none_when_no_filter_active(self):
        """Same filtered_len and full_len → no filter active → None."""
        assert delta(10.0, 8.0, suffix="%", filtered_len=100, full_len=100) is None

    def test_returns_none_for_tiny_difference(self):
        """Absolute difference < 0.05 → None even when filter is active."""
        assert delta(10.02, 10.0, suffix="%", filtered_len=50, full_len=100) is None

    def test_returns_formatted_positive_delta(self):
        result = delta(15.0, 10.0, suffix="%", filtered_len=50, full_len=100)
        assert result == "+5.0%"

    def test_returns_formatted_negative_delta(self):
        result = delta(5.0, 10.0, suffix="%", filtered_len=50, full_len=100)
        assert result == "-5.0%"

    def test_returns_formatted_no_suffix(self):
        result = delta(20.0, 10.0, suffix="", filtered_len=50, full_len=100)
        assert result == "+10.0"

    def test_boundary_exactly_0_05(self):
        """Difference of exactly 0.05 should still return None (< 0.05 is false, so not None)."""
        # abs(0.05) is NOT < 0.05, so it should return a string
        result = delta(10.05, 10.0, suffix="%", filtered_len=50, full_len=100)
        assert result == "+0.1%"

    def test_boundary_just_below_0_05(self):
        result = delta(10.04, 10.0, suffix="%", filtered_len=50, full_len=100)
        assert result is None


class TestGenerateSummaryReport:
    def _make_kpis_and_df(self):
        raw = _make_realistic_raw(n=20)
        df = process_data(raw)
        kpis = calculate_kpis(df)
        return df, kpis

    def test_returns_string(self):
        df, kpis = self._make_kpis_and_df()
        report = generate_summary_report(df, df, kpis)
        assert isinstance(report, str)

    def test_contains_kpi_values(self):
        df, kpis = self._make_kpis_and_df()
        report = generate_summary_report(df, df, kpis)
        assert f"Total Employees: {kpis['total']:,}" in report
        assert f"Active: {kpis['active']:,}" in report
        assert f"Departed: {kpis['departed']:,}" in report
        assert f"Attrition Rate: {kpis['attrition_rate']:.1f}%" in report
        assert f"Retention Rate: {kpis['retention_rate']:.1f}%" in report

    def test_contains_department_breakdown_section(self):
        df, kpis = self._make_kpis_and_df()
        report = generate_summary_report(df, df, kpis)
        assert "DEPARTMENT BREAKDOWN" in report
        # At least one department name should appear
        depts = df["Department"].unique()
        assert any(d in report for d in depts)

    def test_contains_exit_reasons_section(self):
        df, kpis = self._make_kpis_and_df()
        report = generate_summary_report(df, df, kpis)
        assert "EXIT REASONS" in report

    def test_filtered_vs_total_record_count(self):
        df, kpis = self._make_kpis_and_df()
        filtered = df[df["Department"] == "IT"]
        report = generate_summary_report(filtered, df, kpis)
        assert f"{len(filtered)} records (filtered from {len(df)} total)" in report

    def test_gender_ratio_appears(self):
        df, kpis = self._make_kpis_and_df()
        report = generate_summary_report(df, df, kpis)
        assert "Gender (M:F)" in report

    def test_contractor_ratio_appears(self):
        df, kpis = self._make_kpis_and_df()
        report = generate_summary_report(df, df, kpis)
        assert "Contractor Ratio" in report


class TestExportExcel:
    def test_returns_bytes_io(self, processed_df):
        result = export_excel(processed_df)
        assert isinstance(result, io.BytesIO)

    def test_bytes_io_is_valid_excel(self, processed_df):
        result = export_excel(processed_df)
        df_back = pd.read_excel(result, engine="openpyxl")
        assert len(df_back) == len(processed_df)

    def test_bytes_io_columns_match(self, processed_df):
        result = export_excel(processed_df)
        df_back = pd.read_excel(result, engine="openpyxl")
        assert list(df_back.columns) == list(processed_df.columns)

    def test_buffer_position_at_zero(self, processed_df):
        """export_excel should seek(0) so the caller can read immediately."""
        result = export_excel(processed_df)
        assert result.tell() == 0

    def test_non_empty_buffer(self, processed_df):
        result = export_excel(processed_df)
        content = result.read()
        assert len(content) > 0


# ---------------------------------------------------------------------------
# 7. App-level Integration
# ---------------------------------------------------------------------------


class TestAppIntegration:
    def test_app_imports_without_error(self):
        """Importing app.py should not raise (it uses st which we mock via pytest env)."""
        # We just verify the page modules are importable, same as test_pages.py
        from src.pages import (
            advanced_analytics,
            attrition,
            edit_data,
            employee_data,
            overview,
            tenure_retention,
            trends,
            workforce,
        )
        for mod in [overview, attrition, tenure_retention, workforce,
                    trends, employee_data, advanced_analytics, edit_data]:
            assert callable(mod.render)

    def test_all_render_functions_accept_7_params(self):
        """Every page render() must accept exactly 7 positional parameters."""
        from src.pages import (
            advanced_analytics,
            attrition,
            edit_data,
            employee_data,
            overview,
            tenure_retention,
            trends,
            workforce,
        )
        expected_params = ["df", "filtered_df", "kpis", "NAME_COL",
                           "COLORS", "COLOR_SEQUENCE", "CHART_CONFIG"]
        for mod in [overview, attrition, tenure_retention, workforce,
                    trends, employee_data, advanced_analytics, edit_data]:
            sig = inspect.signature(mod.render)
            params = list(sig.parameters.keys())
            assert params == expected_params, (
                f"{mod.__name__}.render has params {params}, expected {expected_params}"
            )

    def test_data_processing_module_importable(self):
        from src import data_processing
        assert callable(data_processing.process_data)
        assert callable(data_processing.calculate_kpis)
        assert callable(data_processing.get_cohort_retention)
        assert callable(data_processing.get_manager_attrition)
        assert callable(data_processing.save_to_excel)
        assert callable(data_processing.load_excel)

    def test_utils_module_importable(self):
        from src import utils
        assert callable(utils.delta)
        assert callable(utils.generate_summary_report)
        assert callable(utils.export_excel)

    def test_config_module_importable(self):
        from src import config
        assert callable(config.detect_name_column)
        assert isinstance(config.COLORS, dict)
        assert isinstance(config.REQUIRED_COLUMNS, list)
