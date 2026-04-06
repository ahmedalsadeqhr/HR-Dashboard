COLORS = {
    'primary':   '#7C3AED',   # purple
    'secondary': '#06B6D4',   # cyan
    'success':   '#10B981',   # emerald
    'danger':    '#EF4444',   # red
    'warning':   '#F59E0B',   # amber
    'info':      '#3B82F6',   # blue
    'purple':    '#A78BFA',   # purple-light
    'pink':      '#D946EF',   # magenta
    'brown':     '#F97316',   # orange
    'gray':      '#475569',
    'light':     '#1E1F35',
    'dark':      '#0D0E1A',
}

# Neon palette for dark theme
COLOR_SEQUENCE = [
    '#06B6D4',  # cyan
    '#7C3AED',  # purple
    '#D946EF',  # magenta
    '#10B981',  # emerald
    '#F59E0B',  # amber
    '#3B82F6',  # blue
    '#EF4444',  # red
    '#F97316',  # orange
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
