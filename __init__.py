"""
RF Spectrum Interference Calculator
===================================

SETUP & USAGE:
1. Install dependencies: pip install streamlit pandas matplotlib openpyxl
2. Run application: streamlit run app.py
3. Select bands from left panel, move to right panel
4. Set guard band margin if needed
5. Click "Calculate Interference"
6. View results table and risk frequency chart
7. Export results to CSV/Excel if needed

FEATURES:
- Complete 3GPP LTE bands 1-71 with official frequency allocations
- Wi-Fi 2.4G, 5G, 6E channels with proper bandwidths
- Bluetooth LE, ISM, HaLow, LoRaWAN, GNSS bands
- 2nd/3rd harmonics and IM3/IM5 intermodulation analysis
- Interactive results table with risk flagging
- Visual frequency spectrum chart
- CSV/Excel export functionality

AUTHOR: Adam Engelbrecht 
VERSION: 1.0
"""
try:
    from .bands import Band, BAND_LIST, BANDS
except ImportError:
    from bands import Band, BAND_LIST, BANDS
