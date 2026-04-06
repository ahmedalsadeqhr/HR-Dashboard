COLORS = {
    'primary':   '#0057B8',
    'secondary': '#FFD100',
    'success':   '#10B981',
    'danger':    '#EF4444',
    'warning':   '#F59E0B',
    'info':      '#06B6D4',
    'purple':    '#8B5CF6',
    'pink':      '#E879F9',
    'brown':     '#92400E',
    'gray':      '#64748B',
    'light':     '#F1F5F9',
    'dark':      '#0F172A',
}

COLOR_SEQUENCE = [
    '#0057B8', '#10B981', '#8B5CF6', '#F59E0B',
    '#EF4444', '#06B6D4', '#E879F9', '#92400E',
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
