<p align="center">
  <img src="docs/assets/logo.svg" alt="RF Interference Calculator" width="120"/>
</p>

<h1 align="center">RF Spectrum Interference Calculator</h1>

<p align="center">
  <strong>Professional RF tool for analyzing interference, harmonics, and intermodulation products</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.x-blue.svg" alt="Python"/>
  <img src="https://img.shields.io/badge/Streamlit-Web_App-FF4B4B.svg" alt="Streamlit"/>
  <img src="https://img.shields.io/badge/Bands-85-purple.svg" alt="Bands"/>
  <img src="https://img.shields.io/badge/Version-2.1.0-green.svg" alt="Version"/>
  <img src="https://img.shields.io/badge/License-AGPL--3.0-blue.svg" alt="License"/>
</p>

---

A professional RF engineering tool for analyzing interference, harmonics, and intermodulation products across 85 wireless bands -- including 5G NR FR1 -- with comprehensive RF system performance analysis, unified risk assessment, and Monte Carlo simulation.

## What's New in v2.1.0

- **5G NR FR1 support**: 14 NR bands (n1 through n79) with full power estimation, duty cycle, and sensitivity data
- **Unified risk assessment**: Bridges frequency-based and power-based analysis into a single consistent result via `calculate_unified_risk()`
- **Monte Carlo simulation fixed**: New multi-band wrapper correctly connects the UI to the analysis engine
- **Coupling factor control**: User-configurable slider with Monte Carlo variation for sensitivity analysis
- **34 isolation matrix pairs**: Added ~20 new NR-WiFi, NR-GNSS, and cross-technology coexistence pairs
- **Professional UI polish**: Removed ~80 emoji, streamlined sidebar, consolidated footer, unified chart colors
- **Centralized constants**: New `constants.py` module as single source of truth for colors, risk styles, and version

See [CHANGELOG.md](CHANGELOG.md) for the full history of changes.

## Key Features

- **85 Wireless Bands**: 2G GSM, 3G UMTS, LTE (31 bands), 5G NR FR1 (14 bands), Wi-Fi 2.4/5/6E, BLE, GNSS, ISM, IoT, LoRa, HaLow, RFID, Public Safety, and Amateur bands
- **Complete IMD Analysis**: IM2, IM3, IM4, IM5, IM7 intermodulation products plus Harmonics 2H through 5H
- **RF Performance Analysis**: Real signal levels (dBm), desensitization margins, and performance impact using industry-standard formulas
- **Unified Risk Assessment**: Combined frequency-based and power-based severity analysis with color-coded alerts
- **Monte Carlo Simulation**: Worst-case analysis with P50/P95/P99 percentiles across TX power, IIP3, isolation, and coupling tolerances
- **Regulatory Compliance**: 3GPP TS 36.101 / TS 38.101 and FCC spurious emission checks with bandwidth normalization
- **34 Isolation Pairs**: Per-band isolation requirements matrix covering critical GNSS, WiFi, and NR coexistence scenarios
- **Interactive Charts**: Frequency spectrum, risk analysis, band coverage, and product distribution visualizations
- **Professional Export**: CSV, Excel, JSON with timestamps and quantitative columns

## Professional Use Cases

- **RF System Design**: Predict interference performance before hardware development
- **Pre-hardware Validation**: Validate coexistence with quantitative signal-level analysis
- **Regulatory Analysis**: Generate interference studies with 3GPP/FCC compliance checking
- **Design Optimization**: Engineering recommendations for isolation, filtering, and layout
- **Engineering Training**: Standard RF calculations with professional methodology

## Professional RF Performance Analysis

Transform frequency conflicts into actionable engineering data.

### Signal-Level Analysis
- **P_IM3 = 3 x P_in - 2 x IIP3** calculations using industry-standard formulas
- Real interference power levels at victim inputs (dBm)
- Performance margins vs sensitivity thresholds
- PER estimates for different modulation schemes
- Unified risk scoring combining frequency overlap and power severity

### System Parameter Configuration
Choose from professional presets or customize all parameters:
- **Mobile Device**: 20 dB isolation, -12 dBm IIP3, 23 dBm LTE
- **IoT Gateway**: 35 dB isolation, -18 dBm IIP3, 20 dBm LTE
- **Automotive**: 25 dB isolation, -10 dBm IIP3, 27 dBm LTE

Configurable parameters include antenna isolation, IIP3/IIP2 linearity, coupling factor (0.0-1.0), and LTE-to-GNSS coupling loss.

### Enhanced Results

| Type | Freq | Aggressor to Victim | Power | Margin | Impact | PER |
|------|------|---------------------|-------|--------|--------|-----|
| IM3  | 2442 | LTE+BLE to WiFi     | -42 dBm | 8 dB  | Medium | 5%  |

### How to Access
1. Run standard interference analysis
2. Click "Performance Report" button
3. Configure system parameters
4. Click "Run Performance Analysis"
5. Get real signal levels and optimization recommendations

## Critical Interference Examples

### 1. GPS Safety Risk
![LTE B13 to GPS L1](screenshots/lte_b13_2h_gps_l1.png)
**LTE Band 13** (777-787 MHz) **to GPS L1** (1575 MHz)
- **Product**: 2nd Harmonic at 1574 MHz -- Critical
- **Impact**: GPS navigation interference
- **Formula**: `2 x 787 MHz = 1574 MHz` (hits GPS L1 at 1575.42 MHz)

### 2. Wi-Fi 5G Performance Impact
![LTE B4 to Wi-Fi 5G Overview](screenshots/lte_b4_3h_wifi5g.png)
**LTE Band 4** (1710-1755 MHz) **to Wi-Fi 5G** (5150-5925 MHz)
- **Product**: 3rd Harmonic at 5265 MHz -- High
- **Impact**: Wi-Fi channel blocking
- **Formula**: `3 x 1755 MHz = 5265 MHz` (hits Wi-Fi 5G channels)

#### Detailed Analysis Views
![Frequency Spectrum Analysis](screenshots/lte_b4_3h_wifi5g_FrequencySpectrum.png)
**Frequency Spectrum**: Interactive scatter plot showing interference products across frequency bands

![Risk Analysis Distribution](screenshots/lte_b4_3h_wifi5g_RiskAnalysis.png)
**Risk Analysis**: Severity breakdown and critical product identification with color-coded alerts

![Band Coverage Visualization](screenshots/lte_b4_3h_wifi5g_BandCoverage.png)
**Band Coverage**: Visual frequency allocation showing transmit/receive band relationships

![Product Distribution Histogram](screenshots/lte_b4_3h_wifi5g_ProductDistribution.png)
**Product Distribution**: Frequency histogram of all interference products with risk-based coloring

### 3. ISM Band Conflicts
![LTE B26 to Wi-Fi 2.4G](screenshots/lte_b26_3h_wifi24g.png)
**LTE Band 26** (814-849 MHz) **to Wi-Fi 2.4G/BLE** (2400-2500 MHz)
- **Product**: 3rd Harmonic at 2442 MHz -- Critical
- **Impact**: BLE and Wi-Fi 2.4G interference
- **Formula**: `3 x 814 MHz = 2442 MHz` (hits ISM band center)

> Complete screenshot documentation is available in [screenshots/README.md](screenshots/README.md) for detailed scenario explanations and configuration instructions.

## Quick Start

```bash
# Install dependencies
pip install streamlit pandas altair openpyxl plotly

# Run the application
streamlit run ui.py
```

**Basic Usage:**
1. Select band categories and specific bands
2. Configure guard margins and analysis products
3. Click "Calculate Interference"
4. Review critical results and export data

**Performance Analysis Workflow:**
1. Complete basic interference analysis (above)
2. Click "Performance Report" button
3. Configure system parameters (presets available)
4. Click "Run Performance Analysis"
5. Get real signal levels, margins, and optimization recommendations

## Interactive Analysis Features

The application provides four comprehensive analysis views:

### Four Analysis Views
- **Frequency Spectrum**: Interactive scatter plot showing all interference products positioned by frequency and risk level
- **Risk Analysis**: Pie chart showing severity distribution with color-coded risk categories and critical product counts
- **Band Coverage**: Visual frequency allocation chart displaying transmit/receive band relationships and overlaps
- **Product Distribution**: Histogram showing frequency distribution of interference products with risk-based coloring

Each view provides different insights:
- **Spectrum view**: Identifies exact interference frequencies and victim bands
- **Risk view**: Prioritizes critical products requiring immediate attention
- **Coverage view**: Shows band relationships and potential conflicts
- **Distribution view**: Reveals interference concentration across frequency ranges

## Project Architecture

```
rf-interference-calculator/
  ui.py                  # Streamlit web application
  calculator.py          # Core interference calculations and unified risk assessment
  rf_performance.py      # RF performance analysis and Monte Carlo simulation
  bands.py               # 85 wireless band definitions (2G through 5G NR)
  constants.py           # Centralized version, colors, risk styles, sort orders
  regulatory_limits.py   # 3GPP/FCC spurious emission database
  isolation_matrix.py    # 34 per-band isolation requirement pairs
  .streamlit/config.toml # Professional blue theme configuration
```

## Band Coverage Summary

| Category | Bands | Examples |
|----------|------:|---------|
| LTE | 31 | B1-B71 (FDD, TDD, SDL) |
| 5G NR FR1 | 14 | n1, n3, n41, n77, n78, n79 |
| 3G UMTS/WCDMA | 6 | B1-B8 |
| 2G GSM | 3 | 850, 1800, 1900 |
| Wi-Fi | 3 | 2.4G, 5G, 6E |
| HaLow | 6 | NA, EU, AUS, JP, TW, KR |
| ISM | 5 | 433, 450, 902, 2400, 5800 MHz |
| IoT | 3 | Zigbee, Thread, Matter |
| GNSS | 3 | L1/E1, L2, L5/E5 |
| Public Safety | 3 | TETRA, P25 VHF/UHF |
| Other | 8 | BLE, LoRa, RFID, Amateur |
| **Total** | **85** | |

## Versioning

Current version: **v2.1.0** -- 5G NR support, unified risk assessment, Monte Carlo fixes, and professional UI polish.

Previous releases: [CHANGELOG.md](CHANGELOG.md)

## Authors

Adam Engelbrecht (RFingAdam)

## License

GNU Affero General Public License v3.0 (AGPL-3.0) -- Free for personal, educational, and commercial use with source sharing requirements.

---
*Professional RF interference analysis tool for engineering and regulatory compliance.*
