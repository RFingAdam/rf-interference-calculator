# Screenshot Documentation

This directory contains example screenshots demonstrating key RF interference scenarios:

## Critical Interference Examples

### 1. LTE Band 13 2nd Harmonic → GPS L1 Interference
**Scenario**: LTE Band 13 (777-787 MHz) 2nd harmonic at 1574 MHz interferes with GPS L1 (1575.42 MHz)
- **Risk Level**: 🔴 Critical (Severity 5)
- **Formula**: `2×Tx_high(LTE_B13) = 2×787 = 1574 MHz`
- **Impact**: GPS navigation degradation
- **Screenshot**: `lte_b13_2h_gps_l1.png`

### 2. LTE Band 4 3rd Harmonic → Wi-Fi 5G Interference  
**Scenario**: LTE Band 4 (1710-1755 MHz) 3rd harmonic at 5265 MHz interferes with Wi-Fi 5G (5150-5925 MHz)
- **Risk Level**: 🟠 High (Severity 4)
- **Formula**: `3×Tx_high(LTE_B4) = 3×1755 = 5265 MHz`
- **Impact**: Wi-Fi 5G channel interference
- **Screenshots**: `lte_b4_3h_wifi5g.png`
`lte_b4_3h_wifi5g_FrequencySpectrum.png`
`lte_b4_3h_wifi5g_RiskAnalysis.png`
`lte_b4_3h_wifi5g_BandCoverage.png`
`lte_b4_3h_wifi5g_ProductDistribution.png`

### 3. LTE Band 26 3rd Harmonic → Wi-Fi 2.4G Interference
**Scenario**: LTE Band 26 (814-849 MHz) 3rd harmonic at 2442-2547 MHz interferes with Wi-Fi 2.4G/BLE (2400-2500 MHz)
- **Risk Level**: 🔴 Critical (Severity 5)
- **Formula**: `3×Tx_low(LTE_B26) = 3×814 = 2442 MHz`
- **Impact**: ISM band interference affecting BLE and Wi-Fi 2.4G
- **Screenshot**: `lte_b26_3h_wifi24g.png`

## How to Generate Screenshots

1. **Run the application**: `streamlit run ui.py`
2. **Select relevant bands** for each scenario
3. **Configure analysis settings**: Enable appropriate IMD products
4. **Calculate interference** and navigate to results tabs
5. **Capture screenshots** of:
   - Configuration panel showing selected bands
   - Results table with highlighted critical risks
   - Frequency spectrum chart showing interference products
   - Risk analysis pie chart

## Screenshot Naming Convention

Format: `[scenario]_[bands]_[product_type]_[victim].png`

Examples:
- `gps_interference_lte_b13_2h_gnss_l1.png`
- `wifi5g_interference_lte_b4_3h_wifi5g.png`  
- `ism_interference_lte_b26_3h_wifi24g.png`
- `coexistence_multi_lte_im3_ble.png`

## Usage in Documentation

These screenshots demonstrate real-world interference scenarios for:
- README.md examples section
- Technical documentation 
- Training materials
- Regulatory compliance reports
