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
  <img src="https://img.shields.io/badge/Bands-70+-purple.svg" alt="Bands"/>
  <img src="https://img.shields.io/badge/License-AGPL--3.0-blue.svg" alt="License"/>
</p>

---

A professional RF tool for analyzing interference, harmonics, and intermodulation products across 70+ wireless bands.

## 🚀 Key Features
- **70+ Wireless Bands**: LTE, Wi-Fi, BLE, GNSS, ISM and more
- **Complete IMD Analysis**: IM2, IM3, IM4, IM5, IM7 + Harmonics (2H-5H)
- **Risk Assessment**: Automatic severity analysis with color-coded alerts
- **Interactive Charts**: Frequency spectrum, risk analysis, band coverage
- **Professional Export**: CSV, Excel, JSON with timestamps
- **Real-time Analysis**: Instant interference calculations and warnings

## 🔍 Critical Interference Examples

### 1. GPS Safety Risk
![LTE B13 → GPS L1](screenshots/lte_b13_2h_gps_l1.png)
**LTE Band 13** (777-787 MHz) **→ GPS L1** (1575 MHz)  
- **Product**: 2nd Harmonic @ 1574 MHz 🔴  
- **Impact**: GPS navigation interference
- **Formula**: `2×787 MHz = 1574 MHz` (exactly hits GPS L1 at 1575.42 MHz)

### 2. Wi-Fi 5G Performance Impact
![LTE B4 → Wi-Fi 5G Overview](screenshots/lte_b4_3h_wifi5g.png)
**LTE Band 4** (1710-1755 MHz) **→ Wi-Fi 5G** (5150-5925 MHz)
- **Product**: 3rd Harmonic @ 5265 MHz 🟠
- **Impact**: Wi-Fi channel blocking
- **Formula**: `3×1755 MHz = 5265 MHz` (hits Wi-Fi 5G channels)

#### Detailed Analysis Views:
![Frequency Spectrum Analysis](screenshots/lte_b4_3h_wifi5g_FrequencySpectrum.png)
**Frequency Spectrum**: Interactive scatter plot showing interference products across frequency bands

![Risk Analysis Distribution](screenshots/lte_b4_3h_wifi5g_RiskAnalysis.png) 
**Risk Analysis**: Severity breakdown and critical product identification with color-coded alerts

![Band Coverage Visualization](screenshots/lte_b4_3h_wifi5g_BandCoverage.png)
**Band Coverage**: Visual frequency allocation showing transmit/receive band relationships

![Product Distribution Histogram](screenshots/lte_b4_3h_wifi5g_ProductDistribution.png)
**Product Distribution**: Frequency histogram of all interference products with risk-based coloring

### 3. ISM Band Conflicts
![LTE B26 → Wi-Fi 2.4G](screenshots/lte_b26_3h_wifi24g.png) 
**LTE Band 26** (814-849 MHz) **→ Wi-Fi 2.4G/BLE** (2400-2500 MHz)
- **Product**: 3rd Harmonic @ 2442 MHz 🔴
- **Impact**: BLE and Wi-Fi 2.4G interference
- **Formula**: `3×814 MHz = 2442 MHz` (hits ISM band center)

> 📖 **Complete screenshot documentation**: See [screenshots/README.md](screenshots/README.md) for detailed scenario explanations and configuration instructions.

## 🚀 Quick Start
```bash
# Install dependencies
pip install streamlit pandas altair openpyxl

# Run the application  
streamlit run ui.py
```

**Usage:**
1. Select band categories and specific bands
2. Configure guard margins and analysis products
3. Click "Calculate Interference" 
4. Review critical results and export data

## 📊 Interactive Analysis Features

The application provides four comprehensive analysis views (shown above for LTE B4 → Wi-Fi 5G scenario):

### Four Analysis Views:
- **🎯 Frequency Spectrum**: Interactive scatter plot showing all interference products positioned by frequency and risk level
- **📈 Risk Analysis**: Pie chart showing severity distribution with color-coded risk categories and critical product counts  
- **🔍 Band Coverage**: Visual frequency allocation chart displaying transmit/receive band relationships and overlaps
- **⚡ Product Distribution**: Histogram showing frequency distribution of interference products with risk-based coloring

Each view provides different insights:
- **Spectrum view**: Identifies exact interference frequencies and victim bands
- **Risk view**: Prioritizes critical products requiring immediate attention  
- **Coverage view**: Shows band relationships and potential conflicts
- **Distribution view**: Reveals interference concentration across frequency ranges

## � What's New in v1.4.3
- **Enhanced Screenshots**: Added professional example scenarios with visual documentation
- **Simplified UI**: Streamlined interface with clearer critical risk identification
- **Improved Charts**: Fixed Product Distribution visualization with proper risk symbol handling
- **Professional Examples**: Real-world GPS, Wi-Fi, and BLE interference scenarios
- **Code Quality**: Cleaned debug code, optimized imports, enhanced error handling

## 🔧 Professional Use Cases
- **Product Development**: Validate RF design choices and coexistence
- **Regulatory Submissions**: Generate interference analysis reports  
- **Customer Support**: Demonstrate and troubleshoot interference issues
- **Training**: Real-world RF engineering examples and calculations

## 📈 Versioning
Current version: **v1.4.3** - Enhanced visual documentation and simplified interface

Previous releases: [CHANGELOG.md](CHANGELOG.md)

## Authors
Adam Engelbrecht (RFingAdam)

## 📄 License
GNU General Public License v3.0 (GPL-3.0) - Free for personal, educational, and commercial use with source sharing requirements.

---
*Professional RF interference analysis tool for engineering and regulatory compliance.*
