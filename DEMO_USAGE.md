# Demo Critical Scenarios Usage Guide

## Quick Start

Run the demonstration script to see real-world interference examples:

```bash
python demo_critical_scenarios.py
```

## What the Demo Shows

The script analyzes **4 critical RF interference scenarios** with **31 total critical products**:

### 1. GPS Navigation Risk (1 critical)
- **LTE B13** (777-787 MHz) 2nd harmonic → **GPS L1** (1575.42 MHz)
- **Critical Product**: 2H @ 1574 MHz (exactly hits GPS frequency!)

### 2. Wi-Fi 5G Channel Blocking (2 critical)  
- **LTE B4** (1710-1755 MHz) 3rd harmonic → **Wi-Fi 5G** (5150-5925 MHz)
- **Critical Products**: 3H @ 5130 MHz and 5265 MHz (hits Wi-Fi channels)

### 3. ISM Band Coexistence (14 critical)
- **LTE B26** (814-849 MHz) 3rd harmonic + **Wi-Fi 2.4G** + **BLE**
- **Critical Products**: Multiple IM3/IM5 products in 2400-2500 MHz ISM band

### 4. Multi-LTE BLE Interference (14 critical)
- **LTE B13** + **LTE B26** creating IM3 products → **BLE** (2402-2480 MHz)
- **Critical Products**: Complex intermodulation hitting BLE channels

## Using Demo Results for Screenshots

1. **Run the demo first** to understand the critical scenarios
2. **Open Streamlit UI**: `streamlit run ui.py`
3. **Configure each scenario**:

### GPS Interference Screenshot
```
Bands: LTE B13, GNSS L1
Result: Shows 2H @ 1574 MHz hitting GPS
Use: Navigation safety documentation
```

### Wi-Fi 5G Interference Screenshot  
```
Bands: LTE B4, Wi-Fi 5G
Result: Shows 3H @ 5130/5265 MHz hitting Wi-Fi channels
Use: Coexistence analysis documentation
```

### ISM Band Interference Screenshot
```
Bands: LTE B26, Wi-Fi 2.4G, BLE  
Result: Shows 14 critical products in ISM band
Use: Multi-radio coexistence analysis
```

## Professional Use Cases

- **Regulatory Submissions**: Show real interference calculations
- **Product Development**: Validate RF design choices
- **Customer Support**: Demonstrate interference analysis capabilities
- **Training Materials**: Real-world RF engineering examples

## Integration with Main Application

The demo scenarios can be directly configured in the main Streamlit UI for:
- Interactive analysis
- Chart visualization  
- Export to CSV/Excel/PDF
- Detailed frequency calculations

Run `streamlit run ui.py` and select the same bands shown in each demo scenario.
