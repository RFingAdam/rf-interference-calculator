"""
Centralized constants for RF Spectrum Interference Calculator.

Single source of truth for colors, risk styles, version, and other
shared constants used across modules.
"""

VERSION = "2.1.0"

# Product type color scheme for Plotly charts
# Harmonics: warm colors (progressive severity by order)
# IMD products: blue family
PRODUCT_TYPE_COLORS = {
    '2H': '#FFD700',     # Gold - 2nd harmonic
    '3H': '#FFA500',     # Orange - 3rd harmonic
    '4H': '#FF6347',     # Tomato - 4th harmonic
    '5H': '#DC143C',     # Crimson - 5th harmonic
    'IM2': '#87CEEB',    # Sky Blue - IM2
    'IM3': '#4169E1',    # Royal Blue - IM3
    'IM4': '#0000CD',    # Medium Blue - IM4
    'IM5': '#000080',    # Navy - IM5
    'IM7': '#191970',    # Midnight Blue - IM7
}

# Risk level definitions: (emoji, label, css_bg, css_color)
RISK_LEVELS = {
    'critical': ('🔴', 'Critical', '#ffebee', '#c62828'),
    'high':     ('🟠', 'High',     '#fff3e0', '#ef6c00'),
    'medium':   ('🟡', 'Medium',   '#fffde7', '#f57f17'),
    'low':      ('🔵', 'Low',      '#e3f2fd', '#1565c0'),
    'safe':     ('✅', 'Safe',     '#e8f5e8', '#2e7d32'),
}

# Mapping from emoji to risk level name
RISK_EMOJI_TO_NAME = {
    '🔴': 'Critical',
    '🟠': 'High',
    '🟡': 'Medium',
    '🔵': 'Low',
    '✅': 'Safe',
}

# Sort order for risk levels (lower = more severe = sorted first)
RISK_SORT_ORDER = {'🔴': 0, '🟠': 1, '🟡': 2, '🔵': 3, '✅': 4}

# Row styling for risk-highlighted DataFrames
RISK_STYLES = {
    '🔴': 'background-color: #ffebee; color: #c62828; font-weight: bold',
    '🟠': 'background-color: #fff3e0; color: #ef6c00; font-weight: bold',
    '🟡': 'background-color: #fffde7; color: #f57f17; font-weight: bold',
    '🔵': 'background-color: #e3f2fd; color: #1565c0',
    '✅': 'background-color: #e8f5e8; color: #2e7d32',
}

# Altair/Plotly unified risk color scales
RISK_COLOR_DOMAIN = ['Critical', 'High', 'Medium', 'Low', 'Safe']
RISK_COLOR_RANGE = ['#c62828', '#ef6c00', '#f57f17', '#1976d2', '#388e3c']

# Altair/Plotly risk color scales keyed by emoji (for donut/pie charts)
RISK_EMOJI_DOMAIN = ['🔴', '🟠', '🟡', '🔵', '✅']
RISK_EMOJI_COLOR_RANGE = ['#c62828', '#ef6c00', '#f57f17', '#1976d2', '#388e3c']

# Plotly pie chart color map (risk_level_name -> color)
RISK_PIE_COLOR_MAP = {
    'Critical': '#c62828',
    'High': '#ef6c00',
    'Medium': '#f57f17',
    'Low': '#1976d2',
    'Safe': '#388e3c',
}

# Technology-dependent desensitization thresholds (dB)
# Based on receiver sensitivity requirements and link budget margins per technology
TECHNOLOGY_RISK_THRESHOLDS = {
    'GNSS':          {'critical': 8.0, 'high': 3.0, 'medium': 1.0, 'low': 0.5},
    'GPS':           {'critical': 8.0, 'high': 3.0, 'medium': 1.0, 'low': 0.5},
    'PUBLIC_SAFETY':  {'critical': 6.0, 'high': 3.0, 'medium': 1.0, 'low': 0.5},
    'WIFI':          {'critical': 6.0, 'high': 3.0, 'medium': 1.0, 'low': 0.5},
    'BLE':           {'critical': 6.0, 'high': 3.0, 'medium': 1.0, 'low': 0.5},
    'LORA':          {'critical': 3.0, 'high': 1.0, 'medium': 0.5, 'low': 0.1},
    'HALOW':         {'critical': 6.0, 'high': 3.0, 'medium': 1.0, 'low': 0.5},
    'LTE':           {'critical': 12.0, 'high': 6.0, 'medium': 3.0, 'low': 1.0},
    'NR':            {'critical': 12.0, 'high': 6.0, 'medium': 3.0, 'low': 1.0},
    'DEFAULT':       {'critical': 12.0, 'high': 6.0, 'medium': 3.0, 'low': 1.0},
}


def get_technology_thresholds(victim_code: str) -> dict:
    """Look up risk thresholds based on victim band code pattern matching."""
    victim_upper = victim_code.upper()
    # Check in priority order (most specific first)
    if 'GNSS' in victim_upper or 'GPS' in victim_upper:
        return TECHNOLOGY_RISK_THRESHOLDS['GNSS']
    if any(ps in victim_upper for ps in ['B13', 'B14', 'FIRSTNET', 'PUBLIC', 'TETRA', 'P25']):
        return TECHNOLOGY_RISK_THRESHOLDS['PUBLIC_SAFETY']
    if 'LORA' in victim_upper:
        return TECHNOLOGY_RISK_THRESHOLDS['LORA']
    if 'HALOW' in victim_upper:
        return TECHNOLOGY_RISK_THRESHOLDS['HALOW']
    if 'WIFI' in victim_upper or 'WI-FI' in victim_upper or 'WiFi' in victim_code:
        return TECHNOLOGY_RISK_THRESHOLDS['WIFI']
    if 'BLE' in victim_upper or 'BLUETOOTH' in victim_upper:
        return TECHNOLOGY_RISK_THRESHOLDS['BLE']
    if 'NR_' in victim_upper or 'NR_N' in victim_upper:
        return TECHNOLOGY_RISK_THRESHOLDS['NR']
    if 'LTE' in victim_upper:
        return TECHNOLOGY_RISK_THRESHOLDS['LTE']
    return TECHNOLOGY_RISK_THRESHOLDS['DEFAULT']
