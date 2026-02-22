COLORS = {
    'primary': '#1f77b4',
    'success': '#2ca02c',
    'danger': '#d62728',
    'warning': '#ff7f0e',
    'info': '#17becf',
    'purple': '#9467bd',
    'pink': '#e377c2',
    'brown': '#8c564b',
    'gray': '#7f7f7f',
}

COLOR_SEQUENCE = [
    COLORS['primary'], COLORS['success'], COLORS['danger'],
    COLORS['warning'], COLORS['info'], COLORS['purple'],
    COLORS['pink'], COLORS['brown'],
]

DATA_FILE = "Master.xlsx"

REQUIRED_COLUMNS = ['Gender', 'Department', 'Position', 'Employee Status', 'Exit Type']

CHART_CONFIG = {
    'displayModeBar': True,
    'toImageButtonOptions': {
        'format': 'png',
        'scale': 3,
        'filename': 'hr_chart',
    },
    'modeBarButtonsToAdd': ['downloadCsv'],
    'displaylogo': False,
}


def detect_name_column(df):
    """Detect the name column from various naming conventions."""
    for c in df.columns:
        if 'full' in str(c).lower() and 'name' in str(c).lower():
            return c
    for c in df.columns:
        if 'name' in str(c).lower() and c != 'Bank Name':
            return c
    return None
