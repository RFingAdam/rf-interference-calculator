# RF Spectrum Interference Calculator

A professional-grade tool for analyzing RF spectrum interference, harmonics, and intermodulation products across global wireless bands.

## 🚀 Features
- **Comprehensive Band Support**: 76+ bands including 3GPP LTE 1-71, Wi-Fi 2.4G/5G/6E, Bluetooth LE, ISM, HaLow, LoRaWAN, GNSS
- **Advanced IMD Analysis**: Exhaustive IM3, IM4, IM5, IM7 calculations with all edge cases
- **Harmonic Products**: 2nd and 3rd harmonic analysis
- **Risk Assessment**: Multi-level risk categorization (High/Med/Low/Minimal) with frequency proximity
- **Smart Deduplication**: Eliminates mathematical duplicates for concise results
- **Overlap Detection**: Real-time Tx/Rx overlap warnings and alerts
- **Interactive Visualizations**: 4-tab chart system with frequency spectrum plots, risk analysis, band coverage, and product distribution
- **Professional Export**: CSV, Excel (multi-sheet), JSON formats with timestamped filenames
- **Advanced Filtering**: Category-based filtering, frequency range limits, risk-based sorting
- **Modern UI**: Streamlit interface with enhanced configuration options and presets
- **Modular Architecture**: Clean separation (`bands.py`, `calculator.py`, `ui.py`)

## 🔬 Analysis Types
- **Harmonics (2H, 3H)**: 2nd and 3rd harmonic products
- **IM3**: Third-order intermodulation with fundamental and harmonic mixing
- **IM4**: Fourth-order intermodulation products (2f₁ + 2f₂)
- **IM5**: Fifth-order intermodulation products (3f₁ ± 2f₂)
- **IM7**: Seventh-order intermodulation products (4f₁ ± 3f₂)
- **ACLR**: Adjacent Channel Leakage Ratio analysis

## 🚀 Quick Start
1. **Install dependencies:**
   ```bash
   pip install streamlit pandas altair openpyxl pyperclip
   ```
2. **Run the application:**
   ```bash
   streamlit run ui.py
   ```
3. **Use the interface:**
   - Select band categories in the sidebar
   - Choose specific bands for analysis
   - Configure guard margins and IMD products
   - Click "Calculate Interference" to analyze
   - Review results in interactive tables and charts
   - Export results in your preferred format

## 📊 What's New in v1.3.0
- **Enhanced Deduplication**: Eliminates mathematical duplicates for cleaner results
- **Risk-First Sorting**: Dangerous products automatically sorted to top
- **Advanced UI**: Multi-tab visualizations with interactive charts
- **Configuration Validation**: Real-time warnings and recommendations
- **Professional Export**: Enhanced Excel export with summary and configuration sheets
- **Guard Band Presets**: Quick configuration options for common scenarios
- **Frequency Filtering**: Limit analysis to specific frequency ranges

## 🔧 Technical Details
- **Algorithm**: Exhaustive IMD3 edge-case analysis including harmonic mixing
- **Performance**: Optimized calculation engine with intelligent result filtering
- **Architecture**: Modular design for maintainability and extensibility
- **Validation**: Comprehensive input validation and error handling

## 📈 Versioning
Current version: **v1.3.0**
- Version string located in `ui.py` (`__version__` variable)
- Update version and add changes to [CHANGELOG.md](CHANGELOG.md) with each release

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for full release history.

## Authors
Adam Engelbrecht

## 📄 License

This project is licensed under the **GNU General Public License v3.0 (GPL-3.0)**.

### What this means:
- ✅ **Free and open source**: Anyone can use, modify, and distribute
- ✅ **Attribution required**: Must credit Adam Engelbrecht (RFingAdam)
- ✅ **Copyleft protection**: Derivative works must remain open source under GPL-3.0
- ✅ **Commercial use allowed**: Companies can use and profit from this software
- ⚠️ **Source code must be shared**: Any modifications must be made available under GPL-3.0
- ⚠️ **Patent protection**: Contributors grant patent licenses for their contributions

### Perfect for:
- **Personal and educational use**
- **Corporate RF engineering teams**
- **Research institutions**
- **Open source projects**
- **Commercial products** (with GPL-3.0 compliance)

### GPL-3.0 Benefits:
The GPL-3.0 ensures this tool remains free and open while allowing commercial use. It protects against proprietary forks that would lock users out of improvements. If you build upon this work, you must share your enhancements with the community.

---
*This tool is provided for educational and research purposes. Users are responsible for validating results against regulatory requirements and industry standards.*
