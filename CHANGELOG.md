# Changelog

All notable changes to this project will be documented in this file.

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
- Added MIT license file

## [1.0.0] - 2025-08-07
### Added
- Initial modular release with full band set, risk logic, and professional UI
- Modular codebase: `bands.py`, `calculator.py`, `ui.py`
- Category filtering, multi-select, and advanced IMD/harmonic analysis
