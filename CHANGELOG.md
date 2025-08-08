# Changelog

All notable changes to this project will be documented in this file.

## [1.4.3] - 2025-08-08
### Added
- **Visual Documentation**: Professional screenshot examples showing critical interference scenarios
- **Enhanced Screenshots**: Real-world GPS, Wi-Fi, and BLE interference examples with visual results
- **Simplified README**: Streamlined documentation focused on key features users care about
- **Interactive Examples**: Screenshot integration showing actual interference analysis results

### Fixed
- **Product Distribution Chart**: Fixed Altair chart visualization with proper risk symbol handling
- **Risk Symbol Support**: Chart now supports both new (🔴🟠🟡🔵✅) and legacy (⚠️✓) risk symbols  
- **Chart Conditions**: Resolved Altair syntax errors with dynamic risk condition handling
- **Frequency Statistics**: Enhanced risk frequency calculations and display metrics

### Improved  
- **User Experience**: Simplified interface with focus on critical interference identification
- **Visual Presentation**: Professional screenshot integration for better understanding
- **Documentation Flow**: Cleaner README structure highlighting key capabilities and examples
- **Chart Reliability**: All visualization tabs now working correctly with proper error handling

## [1.4.2] - 2025-08-08
### Added
- **Professional Documentation**: Added GitHub Copilot instructions for AI-assisted development
- **Screenshot Examples**: Created `/screenshots/` directory with real-world interference scenario documentation
- **RF Engineering Examples**: Documented critical interference cases:
  - LTE Band 13 2nd harmonic → GPS L1 interference (1574 MHz)
  - LTE Band 4 3rd harmonic → Wi-Fi 5G interference (5265 MHz)  
  - LTE Band 26 3rd harmonic → Wi-Fi 2.4G interference (2442 MHz)
  - Multi-LTE IM3 products → BLE interference scenarios
- **Enhanced Requirements**: Complete requirements.txt with optional development dependencies

### Fixed
- **Code Cleanup**: Removed debug comments and unused imports from ui.py
- **Import Organization**: Cleaned up import statements and added missing tempfile import
- **Documentation Accuracy**: Updated version references and removed outdated comments

### Improved
- **Repository Structure**: Added .github folder to gitignore for cleaner development
- **Error Handling**: Enhanced import error handling for cloud deployments
- **Professional Standards**: Code quality improvements following RF engineering best practices

## [1.4.1] - 2025-08-08
### Added
- **Coexistence Test Mode**: Analyze LTE bands individually against coexistence radios (BLE, Wi-Fi) for realistic scenarios
- **Coexistence Recommendations**: Industry-standard guidance for radio coordination
  - BLE + Wi-Fi 2.4G → Packet Transfer Arbitration (PTA) required
  - LTE + BLE → WCI-2 interface coordination recommended  
  - LTE + Wi-Fi → WCI-2 interface with LAA compliance
  - Band-specific recommendations for public safety and TDD bands
- **Individual LTE Band Testing**: Each LTE band tested separately with coexistence radios to match real-world usage
- **Enhanced UI for Coexistence**: Dedicated coexistence radio selection and scenario preview
- **Test Scenario Management**: Automatic generation of LTE+coexistence test combinations

### Improved
- **Realistic Analysis**: Reflects actual deployment where only one LTE band is typically active at a time
- **Professional Recommendations**: Industry-standard coexistence protocols and interfaces
- **Results Organization**: Coexistence mode results show test scenarios and LTE band combinations
- **User Experience**: Clear differentiation between standard analysis and coexistence testing modes

## [1.4.0] - 2025-08-08
### Added
- **IM2 Beat Terms (f₁ ± f₂)**: Added critical beat frequency calculations often higher in level than IM3 products
- **HD4 and HD5 Harmonics**: Extended harmonic analysis to include 4th and 5th harmonic products (4f, 5f)
- **Extended IM4/IM5 Terms**: Added comprehensive higher-order IMD products including 3f₁+f₂, f₁+3f₂, and 2f₁±3f₂
- **Signal Level Based Risk Prioritization**: Results now ordered by typical signal level (2H > IM2 > 3H > IM3 > 4H > IM4 > 5H > IM5 > IM7)
- **Professional RF Engineering Completeness**: Comprehensive IMD analysis matching industry-standard RF engineering practices

### Improved
- **Enhanced Analysis Coverage**: Now covers all critical intermodulation products for professional RF interference analysis
- **IM2 Beat Analysis**: Enabled by default due to critical importance in wideband systems
- **Risk Assessment**: Results prioritized by actual signal level importance rather than alphabetical order
- **UI Enhancements**: Updated tooltips and help text to reflect extended analysis capabilities

## [1.3.0] - 2025-08-08
### Added
- **Enhanced Deduplication Logic**: Implemented mathematical uniqueness detection for interference products
- **Risk-First Result Sorting**: Dangerous interference products automatically sorted to top for immediate visibility
- **Interactive Multi-Tab Visualization**: Added dedicated tabs for metrics, data tables, charts, and export
- **Configuration Validation System**: Real-time warnings and recommendations for invalid configurations
- **Advanced Export Features**: Enhanced Excel export with dedicated summary and configuration sheets
- **Guard Band Quick Presets**: Added preset configurations for common guard band scenarios
- **Frequency Range Filtering**: Ability to limit analysis to specific frequency ranges
- **Enhanced Metrics Dashboard**: 4-column professional metrics display with color-coded risk indicators

### Fixed
- **Duplicate Result Elimination**: Fixed deduplication algorithm to focus on mathematical uniqueness rather than descriptive differences
- **Import Statement Organization**: Cleaned up import order and removed unused imports
- **GNSS Band Correction**: Fixed GNSS bands to be receive-only (no transmission) to prevent incorrect aggressor calculations
- **Configuration Validation**: Updated band validation to properly handle receive-only bands (GNSS) without false warnings
- **Cloud Deployment**: Added graceful handling for missing pyperclip in cloud environments with fallback text areas
- **Data Structure Consistency**: Standardized frequency field names across all IMD calculation types

### Improved
- **Algorithm Performance**: Optimized interference calculation engine with intelligent result filtering
- **Error Handling**: Enhanced input validation with user-friendly error messages
- **Code Documentation**: Updated inline documentation and README with comprehensive feature descriptions
- **Professional UI Design**: Improved layout consistency and visual hierarchy

## [1.2.0] - 2025-08-08
### Added
- Enhanced UI layout with improved metrics display
- Additional IMD product analysis capabilities
- Improved result formatting and export options

## [1.1.0] - 2025-08-08
### Added
- Ensured all table columns always present in results table
- Added versioning to `ui.py` and README
- Improved export and UI consistency

## [1.0.0] - 2025-08-07
### Added
- Initial modular release with full band set, risk logic, and professional UI
- Modular codebase: `bands.py`, `calculator.py`, `ui.py`
- Category filtering, multi-select, and advanced IMD/harmonic analysis
