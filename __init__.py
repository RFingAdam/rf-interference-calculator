"""
RF Spectrum Interference Calculator
===================================

SETUP & USAGE:
1. Install dependencies: pip install -e . (or pip install -r requirements.txt)
2. Run application: streamlit run ui.py
3. Select bands from left panel, move to right panel
4. Set guard band margin if needed
5. Click "Calculate Interference"
6. View results table and risk frequency chart
7. Export results to CSV/Excel/Word if needed

FEATURES:
- 85 bands: 3GPP LTE (1-71), 5G NR FR1, Wi-Fi (2.4/5/6E), BLE, GNSS, IoT
- Harmonics (2nd-5th) and intermodulation (IM2-IM5) analysis
- Power-based quantitative analysis (dBm/dBc) with desensitization
- Monte Carlo statistical interference simulation
- Unified risk assessment bridging frequency and power analysis
- Isolation matrix with 34 critical band pairs
- Regulatory emission compliance checking with bandwidth normalization
- Interactive results with risk flagging and frequency spectrum charts
- Export to CSV, Excel, and Word report formats

AUTHOR: Adam Engelbrecht
"""
try:
    from .constants import VERSION
except ImportError:
    from constants import VERSION

__version__ = VERSION

try:
    from .bands import Band, BAND_LIST, BANDS
except ImportError:
    from bands import Band, BAND_LIST, BANDS
