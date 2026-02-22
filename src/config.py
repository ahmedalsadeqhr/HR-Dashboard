COLORS = {
    'primary': '#0057B8',
    'secondary': '#FFD100',
    'success': '#28A745',
    'danger': '#DC3545',
    'warning': '#FFC107',
    'info': '#17A2B8',
    'purple': '#6F42C1',
    'pink': '#E83E8C',
    'brown': '#8C564B',
    'gray': '#6C757D',
    'light': '#F8F9FA',
    'dark': '#343A40',
}

COLOR_SEQUENCE = [
    COLORS['primary'], COLORS['success'], COLORS['danger'],
    COLORS['warning'], COLORS['info'], COLORS['purple'],
    COLORS['pink'], COLORS['brown'],
]

# 51Talk brand-themed Plotly chart template
CHART_TEMPLATE = {
    'layout': {
        'font': {'family': 'Inter, Segoe UI, sans-serif', 'color': '#343A40'},
        'paper_bgcolor': 'rgba(0,0,0,0)',
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'title': {'font': {'size': 16, 'color': '#0057B8'}},
        'colorway': [
            '#0057B8', '#28A745', '#DC3545', '#FFC107',
            '#17A2B8', '#6F42C1', '#E83E8C', '#8C564B',
        ],
    }
}

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
