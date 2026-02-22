from src.config import COLORS, COLOR_SEQUENCE, CHART_CONFIG, REQUIRED_COLUMNS, DATA_FILE, detect_name_column
import pandas as pd


def test_colors_has_required_keys():
    for key in ['primary', 'success', 'danger', 'warning', 'info', 'purple', 'pink', 'brown', 'gray']:
        assert key in COLORS
        assert isinstance(COLORS[key], str)
        assert COLORS[key].startswith('#')


def test_color_sequence_length():
    assert len(COLOR_SEQUENCE) == 8
    for c in COLOR_SEQUENCE:
        assert c in COLORS.values()


def test_chart_config_structure():
    assert CHART_CONFIG['displayModeBar'] is True
    assert CHART_CONFIG['displaylogo'] is False
    assert 'toImageButtonOptions' in CHART_CONFIG


def test_required_columns():
    assert len(REQUIRED_COLUMNS) == 5
    for col in REQUIRED_COLUMNS:
        assert isinstance(col, str)


def test_data_file():
    assert DATA_FILE == "Master.xlsx"


def test_detect_name_column_full_name():
    df = pd.DataFrame({'Full Name': ['Alice'], 'Age': [30]})
    assert detect_name_column(df) == 'Full Name'


def test_detect_name_column_double_space():
    df = pd.DataFrame({'Full  Name': ['Alice'], 'Age': [30]})
    assert detect_name_column(df) == 'Full  Name'


def test_detect_name_column_fullname():
    df = pd.DataFrame({'FullName': ['Alice'], 'Age': [30]})
    assert detect_name_column(df) == 'FullName'


def test_detect_name_column_fallback():
    df = pd.DataFrame({'Employee Name': ['Alice'], 'Age': [30]})
    assert detect_name_column(df) == 'Employee Name'


def test_detect_name_column_none():
    df = pd.DataFrame({'ID': [1], 'Age': [30]})
    assert detect_name_column(df) is None


def test_detect_name_column_skips_bank_name():
    df = pd.DataFrame({'Bank Name': ['HSBC'], 'ID': [1]})
    assert detect_name_column(df) is None
