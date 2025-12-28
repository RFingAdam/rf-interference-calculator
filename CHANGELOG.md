# Changelog

All notable changes to this project will be documented in this file.

## [2.0.0] - 2025-12-28 - Professional UI Overhaul

### Major UI Enhancements
- **Professional Results Table**: Now displays P_TX (dBm), P_RX (dBm), Desense (dB),
  Margin (dB), and 3GPP Compliance status for every interference product
- **Summary Dashboard**: At-a-glance severity counts (Critical/High/Medium/Low/Safe)
  with compliance metrics (avg/max desense, min margin)
- **Compliance Report Section**: Expandable 3GPP/FCC violation report with regulatory
  references, critical isolation requirements from isolation_matrix.py
- **Monte Carlo Analysis**: Optional worst-case analysis button with P50/P95/P99
  percentile results and worst-case condition reporting

### New Functions
- `enhance_results_with_quantitative()`: Adds dBm/dBc columns to results DataFrame
- `create_compliance_summary()`: Generates compliance metrics for dashboard
- `highlight_risks()`: Professional styling for results table

### Integration
- Full integration of `regulatory_limits.py` into main results view
- Full integration of `isolation_matrix.py` into compliance checking
- Quantitative severity reasons displayed in results table

### Code Quality Fixes
- **Legacy IM3 Formula**: Fixed incorrect `2×P_in - IIP3` → correct `3×P_in - 2×IIP3`
- **Duplicate Path Loss Function**: Removed dead code from copy-paste error
- **Edge Case Guards**: Added empty list guards for max/min, division by zero protection
- **Input Validation**: Added log10() edge case guards in filter rejection calculation
- **Column Naming**: Renamed confusing `IM3_Type` → `Product_Subtype`
- **RFID/NFC Bands**: Fixed zero-width bands (now 0.12 MHz bandwidth)
- **RFID_UHF Label**: Fixed "(900 MHz)" → "(860-960 MHz)"
- **Duplicate Import**: Removed duplicate `import altair as alt`
- **Documentation Reference**: Fixed `ui_simplified.py` → `ui.py`
- **Broken Emojis**: Fixed corrupted emoji characters throughout

### Technical Notes
- Version badge updated to 2.0.0
- Professional export includes new quantitative columns
- Backward compatibility maintained for basic analysis mode

## [1.9.0] - 2025-12-28 - PhD-Level RF Analysis Overhaul

### Major Mathematical Fixes

- **HD4/HD5 Calculation**: Fixed polynomial coefficient ratios
  - HD4: Now uses -30 dB offset from HD2 (was incorrectly -20 dB)
  - HD5: Now uses -20 dB offset from HD3 (was incorrectly -15 dB)
  - Based on polynomial analysis: a4/a2 = 0.0018/0.0562 = -29.9 dB

- **Coupling-Aware Isolation Model**: Replaced simple additive model
  - Old model: Total = Antenna + PCB + Shield (overestimated by 5-15 dB)
  - New model: Worst-path + diminishing returns from parallel paths
  - Includes frequency-dependent effects (higher freq = worse isolation)

- **Harmonic Antenna Isolation**: Corrected direction of adjustment
  - Old model assumed isolation IMPROVES at harmonics (wrong)
  - New model shows isolation often DEGRADES at harmonic frequencies
  - Antenna-type specific adjustments (patch, dipole, helical)

- **IMD Scaling Formulas**: Replaced empirical HD-scaling with proper RF theory
  - IM2: P_IM2 = 2×P_in - IIP2 (standard two-tone formula)
  - IM3: P_IM3 = 3×P_in - 2×IIP3 (industry standard)
  - IM5: P_IM5 = 5×P_in - 4×IIP5 (IIP5 ≈ IIP3 + 10 dB)
  - IM7: P_IM7 = 7×P_in - 6×IIP7 (IIP7 ≈ IIP3 + 15 dB)

### New Analysis Features

- **Power-Based Severity Assessment** (`calculator.py`)
  - `assess_risk_severity_quantitative()`: Uses actual dBm levels instead of frequency matching
  - GNSS thresholds: 8 dB desense = critical, 3 dB = high, 1 dB = medium
  - Standard tech thresholds: 12 dB = critical, 6 dB = high, 3 dB = medium
  - Returns severity reason with quantitative data

- **Receiver Selectivity / Filter Rejection** (`rf_performance.py`)
  - `calculate_rx_filter_rejection()`: Models filter attenuation vs frequency offset
  - Supports Butterworth, Chebyshev, SAW, and BAW filter types
  - Realistic rolloff rates and ultimate rejection limits

- **Duty Cycle / TDM Correction** (`rf_performance.py`)
  - `apply_duty_cycle_correction()`: Reduces desensitization for intermittent interference
  - Formula: Desens_avg = Desens_cont + 10×log10(duty_cycle)
  - Technology-specific duty cycles (WiFi ~40%, BLE ~5%, TDD LTE ~50%)

- **Monte Carlo Analysis** (`rf_performance.py`)
  - `monte_carlo_interference_analysis()`: Worst-case analysis with tolerances
  - Varies TX power, IIP3, isolation, temperature within tolerances
  - Returns P50, P95, P99 percentiles and worst-case conditions
  - `generate_monte_carlo_report()`: Human-readable analysis report

### New Modules

- **regulatory_limits.py**: 3GPP/FCC Spurious Emission Database
  - Band-specific limits from TS 36.101 / TS 38.101
  - GPS L1 protection limits for LTE B13/B14
  - `check_emission_compliance()`: Verify against regulatory limits
  - `generate_compliance_report()`: Full compliance analysis

- **isolation_matrix.py**: Per-Band Isolation Requirements
  - 20+ critical band pairs with required isolation
  - LTE B13 → GNSS L1: 50 dB minimum, 60 dB recommended
  - `get_required_isolation()`: Lookup isolation requirements
  - `check_isolation_compliance()`: Verify actual vs required isolation

### Technical Improvements

- Added duty cycle parameters to `SystemParameters` dataclass
- Added `ToleranceParameters` dataclass for Monte Carlo analysis
- Enhanced `calculate_interference_at_victim_quantitative()` with new isolation model
- All harmonic/IMD calculations now use coupling-aware isolation
- Added `get_technology_duty_cycle()` for band-specific duty cycles

### Reference Formulas

```
# Correct HD Calculations (polynomial coefficients)
HD4_dBc = HD2_dBc - 30.0 dB
HD5_dBc = HD3_dBc - 20.0 dB

# Standard IMD Formulas
IM2 = 2×P_in - IIP2
IM3 = 3×P_in - 2×IIP3
IM5 = 5×P_in - 4×(IIP3 + 10)

# Desensitization (unchanged - was correct)
Desens_dB = 10×log10(1 + I/N)

# Duty Cycle Correction
Desens_adjusted = Desens_continuous + 10×log10(duty_cycle)
```

## [1.8.1] - 2025-12-28 - Bug Fixes & Documentation Sync

### Bug Fixes
- **IMD Product Classification**: Fixed mislabeled intermodulation products
  - `4A±B` products (order 5) now correctly classified as IM5 instead of IM3
  - `2A±2B` products (order 4) now correctly classified as IM4 instead of IM3
- **Severity Assessment**: Added proper risk severity assessment to all IMD calculation blocks (IM4, IM5, IM7, ACLR) - previously used legacy symbols without quantitative analysis
- **LTE B32 Band Definition**: Fixed from TDD-style to SDL (Supplemental Downlink) - B32 is receive-only, UE does not transmit on this band
- **Risk Symbol Consistency**: Consolidated all legacy `⚠️`/`✓` symbols to unified severity-based emoji system (🔴🟠🟡🔵✅)

### Documentation & Assets
- **Professional Logo**: Added purple SVG logo with RF wave design (`docs/assets/logo.svg`)
- **README Header**: Added professional header with logo and status badges
- **Dev Container**: Added GitHub Codespaces support (`.devcontainer/devcontainer.json`)
- **Demo Scripts**: Added `demo_critical_scenarios.py` with 4 critical interference examples
- **Demo Documentation**: Added `DEMO_USAGE.md` with usage instructions
- **License**: Upgraded to AGPL-3.0

### Technical Notes
- IMD order calculation: Order = sum of coefficient magnitudes (e.g., 4A+B = |4|+|1| = 5)
- LTE B32 SDL bands have no UE uplink allocation per 3GPP specifications

## [1.8.0] - 2025-08-10 - Production Ready RF Analysis
### Major Features
- **🔬 Professional RF Performance Analysis**: Complete signal-level interference calculations using industry-standard formulas (P_IM3 = 3×P_in - 2×IIP3)
- **🛠️ System Parameter Modeling**: Comprehensive RF system configuration with antenna isolation, IIP3/IIP2 linearity, and realistic power levels
- **📡 Industry Presets**: Mobile Device, IoT Gateway, Automotive, Base Station, and Laboratory configurations
- **📊 Engineering Metrics**: Real interference power levels (dBm), performance margins, desensitization analysis, and risk assessment
- **🎯 Professional Export**: Word reports with embedded charts, comprehensive analysis tables, and design recommendations

### Enhanced Analysis
- **Complete IMD Coverage**: IM2 beat terms, IM3, higher-order products (IM4/IM5/IM7) + harmonics (2H-5H)
- **70+ Wireless Bands**: LTE, Wi-Fi, BLE, GNSS, ISM with accurate frequency assignments
- **Risk-Based Results**: Automatic severity assessment with color-coded alerts prioritized by signal level
- **Interactive Visualizations**: Frequency spectrum, risk distribution, band coverage analysis

## [1.0.0] - 2025-08-07 - Initial Release
### Core Features
- Professional RF interference calculator with modular architecture
- Band-based analysis with category filtering and multi-select capability
- Advanced IMD and harmonic calculations with risk assessment
- Export functionality (CSV, Excel, JSON) with professional formatting
