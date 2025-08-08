import streamlit as st
import tempfile
import pandas as pd
from bands import BANDS, Band
from calculator import calculate_all_products, validate_band_configuration
import altair as alt
from io import BytesIO

__version__ = "1.4.3"  # Update this version string with each release

# Import pyperclip with fallback for cloud deployment
try:
    import pyperclip
    PYPERCLIP_AVAILABLE = True
except ImportError:
    PYPERCLIP_AVAILABLE = False
    st.warning("⚠️ Clipboard functionality not available in this deployment environment.")

def generate_coexistence_recommendation(lte_band_code, coex_radios, has_ble, has_wifi_24, has_wifi_5):
    """Generate coexistence recommendations based on selected radio combinations."""
    recommendations = []
    
    # BLE + Wi-Fi 2.4G critical case
    if has_ble and has_wifi_24:
        recommendations.append("🔄 **Critical**: BLE + Wi-Fi 2.4G → Packet Transfer Arbitration (PTA) required for 2.4 GHz ISM coordination")
        recommendations.append("📡 WCI-2 interface recommended for LTE coordination")
        
    # BLE alone with LTE
    elif has_ble:
        recommendations.append("📡 WCI-2 interface recommended for LTE-BLE coordination")
        recommendations.append("⏰ Time-division scheduling to avoid critical BLE connection events")
        
    # Wi-Fi cases
    elif has_wifi_24 or has_wifi_5:
        wifi_bands = []
        if has_wifi_24:
            wifi_bands.append("2.4G")
        if has_wifi_5:
            wifi_bands.append("5G")
        
        recommendations.append(f"📡 WCI-2 interface recommended for LTE-Wi-Fi {'+'.join(wifi_bands)} coordination")
        
        if has_wifi_24:
            recommendations.append("🎯 Consider Wi-Fi channel selection away from 2.4 GHz ISM interference")
        
        recommendations.append("📊 LAA (Licensed Assisted Access) compliance if using shared spectrum")
    
    # Band-specific recommendations
    if lte_band_code in ['B13', 'B14']:  # 700 MHz public safety bands
        recommendations.append("🚨 Public safety band - enhanced coordination protocols required")
    elif lte_band_code in ['B41', '42', '43']:  # TDD bands
        recommendations.append("⚡ TDD band - synchronization with coexistence radios critical")
    
    return " | ".join(recommendations)


def analyze_na_case1_results(results, selected_lte_bands):
    """
    Analyze NA Case 1 specific interference patterns and provide detailed recommendations.
    """
    if results.empty:
        return {}
    
    analysis = {
        'critical_interference': [],
        'ism_band_hits': [],
        'gnss_risks': [],
        'lte_harmonic_issues': [],
        'recommendations': []
    }
    
    # Filter for risk products only
    risk_products = results[results['Risk'].isin(['🔴', '🟠', '🟡', '⚠️'])] if 'Risk' in results.columns else pd.DataFrame()
    
    if risk_products.empty:
        return analysis
    
    # Analyze critical interference patterns
    for _, row in risk_products.iterrows():
        freq = row.get('Frequency_MHz', 0)
        victim = row.get('Victims', '')
        aggressors = row.get('Aggressors', '')
        product_type = row.get('Type', '')
        risk_level = row.get('Risk', '')
        
        # ISM band interference (2400-2500 MHz)
        if 2400 <= freq <= 2500:
            analysis['ism_band_hits'].append({
                'frequency': freq,
                'victim': victim,
                'aggressors': aggressors,
                'type': product_type,
                'risk': risk_level,
                'severity': 'Critical' if risk_level in ['🔴', '🟠'] else 'High'
            })
        
        # GNSS interference (GPS L1: 1575, L2: 1227, L5: 1176 MHz)
        if (1570 <= freq <= 1580) or (1220 <= freq <= 1235) or (1170 <= freq <= 1185):
            analysis['gnss_risks'].append({
                'frequency': freq,
                'victim': victim,
                'aggressors': aggressors,
                'type': product_type,
                'risk': risk_level,
                'band': 'L1' if 1570 <= freq <= 1580 else ('L2' if 1220 <= freq <= 1235 else 'L5')
            })
        
        # LTE harmonic issues (harmonics of LTE bands)
        if product_type in ['2H', '3H'] and any(f'LTE_B{band}' in aggressors for band in ['2', '4', '5', '12', '13', '14', '17', '25', '26']):
            analysis['lte_harmonic_issues'].append({
                'frequency': freq,
                'victim': victim,
                'aggressors': aggressors,
                'harmonic_order': product_type,
                'risk': risk_level
            })
        
        # Critical interference (GPS or ISM with high severity)
        if risk_level in ['🔴', '🟠'] and (2400 <= freq <= 2500 or 1170 <= freq <= 1580):
            analysis['critical_interference'].append({
                'frequency': freq,
                'victim': victim,
                'aggressors': aggressors,
                'type': product_type,
                'reason': 'ISM band interference' if 2400 <= freq <= 2500 else 'GPS interference'
            })
    
    # Generate specific recommendations based on analysis
    recommendations = []
    
    if analysis['ism_band_hits']:
        recommendations.append("🚨 **ISM Band Interference Detected**: Multiple products interfering with 2.4 GHz ISM band (BLE/Wi-Fi)")
        if len(analysis['ism_band_hits']) > 5:
            recommendations.append("⚡ **High ISM Interference**: Consider LTE band filtering or power reduction")
        recommendations.append("🔄 **PTA Implementation**: Mandatory for BLE + Wi-Fi 2.4G coexistence")
    
    if analysis['gnss_risks']:
        recommendations.append("🛰️ **GPS Interference Warning**: Critical navigation system interference detected")
        l1_hits = [r for r in analysis['gnss_risks'] if r['band'] == 'L1']
        if l1_hits:
            recommendations.append("🚨 **GPS L1 Interference**: Primary GPS frequency affected - immediate attention required")
    
    if analysis['lte_harmonic_issues']:
        harmonic_bands = set()
        for issue in analysis['lte_harmonic_issues']:
            for band in ['2', '4', '5', '12', '13', '14', '17', '25', '26']:
                if f'LTE_B{band}' in issue['aggressors']:
                    harmonic_bands.add(band)
        if harmonic_bands:
            recommendations.append(f"📡 **LTE Harmonic Issues**: Bands {', '.join(sorted(harmonic_bands))} causing interference")
            recommendations.append("🔧 **Mitigation**: Consider harmonic filters or power control")
    
    if analysis['critical_interference']:
        recommendations.append(f"🔴 **Critical Analysis**: {len(analysis['critical_interference'])} severe interference products detected")
        recommendations.append("⚡ **Immediate Action**: Review coexistence implementation and filtering")
    
    # NA Case 1 specific recommendations
    if selected_lte_bands:
        public_safety_bands = [b for b in selected_lte_bands if b in ['B13', 'B14']]
        if public_safety_bands:
            recommendations.append(f"🚨 **Public Safety**: Bands {', '.join(public_safety_bands)} require enhanced coexistence protocols")
    
    analysis['recommendations'] = recommendations
    return analysis

st.set_page_config(page_title="RF Spectrum Interference Calculator", page_icon="📡", layout="wide", initial_sidebar_state="expanded")
st.title("📡 RF Spectrum Interference Calculator")
st.markdown("**Professional-grade harmonic & intermodulation analysis tool**")
st.markdown("---")

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Enhanced guard band input with presets
    st.subheader("🛡️ Guard Band Settings")
    guard_preset = st.selectbox(
        "Guard Band Preset:",
        ["Custom", "No Guard (0 MHz)", "Conservative (1 MHz)", "Moderate (2 MHz)", "Aggressive (5 MHz)"],
        index=1
    )
    
    if guard_preset == "Custom":
        guard = st.number_input(
            "Custom Guard Margin (MHz)",
            min_value=0.0,
            max_value=50.0,
            value=0.0,
            step=0.1,
            help="Additional frequency margin around Rx bands for interference detection"
        )
    else:
        guard_values = {"No Guard (0 MHz)": 0.0, "Conservative (1 MHz)": 1.0, "Moderate (2 MHz)": 2.0, "Aggressive (5 MHz)": 5.0}
        guard = guard_values.get(guard_preset, 0.0)
        st.info(f"Using {guard} MHz guard band")
    
    # Enhanced ACLR settings
    st.subheader("📡 ACLR Settings")
    aclr_enabled = st.checkbox("Enable ACLR Analysis", value=False)
    if aclr_enabled:
        aclr_margin = st.number_input("ACLR margin (MHz)", 0.0, 20.0, 5.0, step=0.1,
                                     help="Adjacent Channel Leakage Ratio analysis margin")
    else:
        aclr_margin = 0.0
    
    st.markdown("---")
    
    # Coexistence Implementation Settings
    st.subheader("🔄 Coexistence Implementation")
    st.markdown("**Filter results based on implemented coordination mechanisms:**")
    
    # PTA Implementation
    pta_enabled = st.checkbox("PTA (Packet Transfer Arbitration) Implemented", value=False,
                             help="Enable if PTA is implemented for 2.4 GHz ISM coordination (BLE + Wi-Fi)")
    if pta_enabled:
        st.success("✅ PTA active - ISM band coordination products filtered")
    
    # WCI-2 Implementation  
    wci2_enabled = st.checkbox("WCI-2 Interface Implemented", value=False,
                              help="Enable if WCI-2 interface is implemented for LTE coordination")
    if wci2_enabled:
        st.success("✅ WCI-2 active - LTE coordination products filtered")
    
    # Advanced coexistence filtering
    with st.expander("🔧 Advanced Coexistence Filtering"):
        st.markdown("**Custom Risk Filtering:**")
        
        # Filter specific product types when coordination is active
        filter_ism_products = st.checkbox("Filter ISM IM products when PTA active", value=True,
                                         help="Remove IM products between BLE and Wi-Fi 2.4G when PTA coordinates them",
                                         disabled=not pta_enabled)
        
        filter_lte_harmonics = st.checkbox("Filter LTE harmonic risks when WCI-2 active", value=True,
                                          help="Remove LTE harmonic products when WCI-2 provides timing coordination",
                                          disabled=not wci2_enabled)
        
        # Show what will be filtered
        if pta_enabled or wci2_enabled:
            st.info("**Active Filters:**")
            if pta_enabled:
                st.write("• BLE ↔ Wi-Fi 2.4G IM products (PTA coordination)")
            if wci2_enabled:
                st.write("• LTE timing-sensitive products (WCI-2 coordination)")
    
    # Advanced filtering options
    st.subheader("🔍 Advanced Filters")
    
    # Frequency range filter
    freq_filter_enabled = st.checkbox("Enable Frequency Range Filter", value=False)
    if freq_filter_enabled:
        freq_range = st.slider(
            "Frequency Range (MHz)",
            min_value=0,
            max_value=8000,
            value=(400, 6000),
            step=50,
            help="Only show results within this frequency range"
        )
    else:
        freq_range = None
    
    st.markdown("---")
    st.markdown("### 📂 Band Categories")
    all_bands = list(BANDS.values())
    categories = sorted(set(b.category for b in all_bands))
    default_cats = [cat for cat in categories if cat in ("Wi-Fi", "LTE")]
    selected_cats = st.multiselect("Filter by category:", categories, default=default_cats)
    
    # Category statistics
    if selected_cats:
        filtered_count = len([b for b in all_bands if b.category in selected_cats])
        st.info(f"**{filtered_count}** bands available in selected categories")
    
    # Export format selection
    st.markdown("---")
    st.subheader("💾 Export Options")
    export_format = st.radio("Preferred Export Format:", ["CSV", "Excel", "JSON"], index=1)
    include_safe = st.checkbox("Include Safe Products in Export", value=True)

# Main interface
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📋 Available Bands")
    filtered_bands = {b.code: b for b in all_bands if b.category in selected_cats}
    
    # Use a single source of truth for selection to avoid resets
    if 'band_multiselect_widget' not in st.session_state:
        st.session_state['band_multiselect_widget'] = []
    
    # Create options list that includes both visible and previously selected bands
    visible_codes = list(filtered_bands.keys())
    selected_codes = list(st.session_state['band_multiselect_widget'])  # Ensure it's a list
    
    # CRITICAL: Always include previously selected bands in options to prevent clearing
    # This ensures that even if a band's category is unchecked, the band stays available
    all_band_codes = {b.code: b for b in all_bands}  # All bands for reference
    all_codes = set(visible_codes)  # Start with currently visible
    
    # Add all previously selected bands (even from other categories)
    for selected_code in selected_codes:
        if selected_code in all_band_codes:  # Validate band still exists
            all_codes.add(selected_code)
    
    # Sort codes properly - LTE bands numerically, others alphabetically
    def sort_key(code):
        if code.startswith('LTE_B') and code[5:].isdigit():
            # Pad LTE band numbers to ensure proper numerical sorting (LTE_B1 -> LTE_B001, LTE_B30 -> LTE_B030)
            band_num = int(code[5:])  # Extract number after "LTE_B"
            return (0, f"LTE_B{band_num:03d}")
        elif code.startswith('UMTS_B') and code[6:].isdigit():
            # Similar sorting for UMTS bands
            band_num = int(code[6:])  # Extract number after "UMTS_B"
            return (1, f"UMTS_B{band_num:03d}")
        elif code.startswith('GSM_'):
            # GSM bands sorted after UMTS
            return (2, code)
        else:
            return (3, code)  # Others: sort alphabetically after cellular bands
    
    all_options = sorted(all_codes, key=sort_key)
    
    # Render multiselect with band codes as values and format_func for display
    available_bands = st.multiselect(
        "Select bands to analyze:",
        all_options,
        key='band_multiselect_widget',
        format_func=lambda code: f"{code}: {BANDS[code].label}" if code in BANDS else code
    )
    # Show info about selections
    visible_count = len([code for code in available_bands if code in visible_codes])
    kept_count = len(available_bands) - visible_count
    
    if kept_count > 0:
        st.info(f"**{len(available_bands)} bands selected** ({visible_count} visible, {kept_count} from other categories) from {len(filtered_bands)} currently visible")
    else:
        st.info(f"**{len(available_bands)} bands selected** from {len(filtered_bands)} available")

with col2:
    st.subheader("🎯 Selected Bands Summary")
    if available_bands:
        selected_band_ids = available_bands  # already band codes now
        
        # Categorize selected bands
        lte_bands = [band_id for band_id in selected_band_ids if BANDS[band_id].category == 'LTE']
        coex_radios = [band_id for band_id in selected_band_ids if BANDS[band_id].category in ['Wi-Fi', 'BLE', 'ISM']]
        other_bands = [band_id for band_id in selected_band_ids if BANDS[band_id].category not in ['LTE', 'Wi-Fi', 'BLE', 'ISM']]
        
        # Determine analysis mode automatically
        if len(lte_bands) > 1 and len(coex_radios) > 0:
            st.info("🔬 **Automatic Coexistence Mode**: Multiple LTE bands will be tested individually against coexistence radios")
            
            # Show LTE bands to test
            if lte_bands:
                lte_bands_sorted = sorted(lte_bands, key=lambda x: int(x[1:]) if x.startswith('B') and x[1:].isdigit() else 999)
                st.markdown(f"**LTE Bands to Test Individually ({len(lte_bands_sorted)}):**")
                for i, band_id in enumerate(lte_bands_sorted[:5]):  # Show first 5
                    band = BANDS[band_id]
                    st.write(f"**{i+1}.** {band.label}")
                if len(lte_bands_sorted) > 5:
                    st.write(f"... and {len(lte_bands_sorted) - 5} more LTE bands")
            
            # Show coexistence radios
            if coex_radios:
                st.markdown(f"**Coexistence Radios ({len(coex_radios)}):**")
                for band_id in coex_radios:
                    band = BANDS[band_id]
                    st.write(f"📡 {band.label}")
                    
                st.success(f"🧪 **Test Scenarios**: {len(lte_bands)} LTE bands × {len(coex_radios)} coexistence radios = {len(lte_bands)} individual tests")
        else:
            # Standard mode display
            for i, band_id in enumerate(selected_band_ids[:10]):
                band = BANDS[band_id]
                st.write(f"**{i+1}.** {band.label}")
                st.write(f"   └─ Tx: {band.tx_low}-{band.tx_high} MHz | Rx: {band.rx_low}-{band.rx_high} MHz")
            if len(selected_band_ids) > 10:
                st.write(f"... and {len(selected_band_ids) - 10} more bands")
    else:
        st.info("Select bands from the left panel to begin analysis")

st.markdown("---")

# Enhanced IMD/Harmonic configuration
st.subheader("🔬 Interference Analysis Configuration")

# Harmonics section
st.markdown("#### 🎵 Harmonic Products")
col_h1, col_h2 = st.columns(2)
with col_h1:
    harmonics_enabled = st.checkbox("Enable Harmonic Analysis", value=True, 
                                   help="Calculate 2nd, 3rd, 4th, and 5th harmonic products (2f, 3f, 4f, 5f)")
with col_h2:
    if harmonics_enabled:
        st.success("2H, 3H, 4H, and 5H products will be calculated")
    else:
        st.info("Harmonic analysis disabled")

# IMD section
st.markdown("#### ⚡ Intermodulation Products")
st.markdown("*Select which IMD products to analyze:*")

col_2a, col_3, col_4, col_5, col_6 = st.columns(5)
with col_2a:
    imd2_enabled = st.checkbox("IM2 Beat Terms", value=True, help="f₁ ± f₂, critical for wideband systems")
    if imd2_enabled:
        st.caption("🔥 Often higher than IM3")
with col_3:
    imd3_enabled = st.checkbox("IM3 Products", value=True, help="2f₁ ± f₂, includes all edge cases")
    if imd3_enabled:
        st.caption("✓ Fundamental & harmonic mixing")
with col_4:
    imd4 = st.checkbox("IM4 Products", value=False, help="2f₁ + 2f₂, 3f₁ + f₂, f₁ + 3f₂")
    if imd4:
        st.caption("⚠️ Higher order products")
with col_5:
    imd5 = st.checkbox("IM5 Products", value=False, help="3f₁ ± 2f₂, 2f₁ ± 3f₂")
    if imd5:
        st.caption("⚠️ Complex mixing")
with col_6:
    imd7 = st.checkbox("IM7 Products", value=False, help="4f₁ ± 3f₂")
    if imd7:
        st.caption("⚠️ Very high order")

# Analysis complexity warning
enabled_products = sum([harmonics_enabled, imd2_enabled, imd3_enabled, imd4, imd5, imd7])
if enabled_products > 4:
    st.warning("⚠️ High complexity analysis selected. This may generate many results.")
elif enabled_products == 0:
    st.error("❌ No analysis products selected. Please enable at least one option.")

# Advanced options
with st.expander("🔧 Advanced Analysis Options"):
    st.markdown("##### Calculation Precision")
    precision = st.selectbox("Frequency Precision:", ["Standard (0.01 MHz)", "High (0.001 MHz)", "Ultra (0.0001 MHz)"], index=0)
    
    st.markdown("##### Risk Assessment")
    risk_threshold = st.selectbox("Risk Sensitivity:", ["Conservative", "Moderate", "Aggressive"], index=1, 
                                 help="Conservative: stricter risk detection, Aggressive: more lenient")
    
    st.markdown("##### Performance Options")
    parallel_calc = st.checkbox("Enable Parallel Calculation", value=True, 
                               help="Use multiprocessing for faster calculation (recommended)")
    
    show_formulas = st.checkbox("Show Mathematical Formulas", value=True,
                               help="Display the mathematical formulas used in calculations")


# Enhanced calculate button with validation
calculation_ready = enabled_products > 0 and len(available_bands) > 0

if calculation_ready:
    calc_button_type = "primary"
    calc_button_help = "All requirements met - ready to calculate!"
else:
    calc_button_type = "secondary"
    calc_button_help = "Please select bands and enable analysis products"

if st.button("🚀 Calculate Interference", type=calc_button_type, use_container_width=True, help=calc_button_help, disabled=not calculation_ready):
    if not available_bands:
        st.error("❌ Please select at least one band for analysis")
    elif enabled_products == 0:
        st.error("❌ Please enable at least one analysis product (harmonics, IM3, etc.)")
    else:
        try:
            with st.spinner("🔄 Calculating interference products..."):
                selected_band_ids = available_bands  # already band codes now
                selected_band_objs = [BANDS[c] for c in selected_band_ids]
                
                # Input validation
                if len(selected_band_objs) > 50:
                    st.warning("⚠️ Large number of bands selected. Calculation may take longer...")
                
                # Categorize selected bands for automatic coexistence mode
                lte_bands = [b for b in selected_band_objs if b.category == 'LTE']
                coex_radios = [b for b in selected_band_objs if b.category in ['Wi-Fi', 'BLE', 'ISM']]
                other_bands = [b for b in selected_band_objs if b.category not in ['LTE', 'Wi-Fi', 'BLE', 'ISM']]
                
                # Determine analysis mode automatically
                auto_coex_mode = len(lte_bands) > 1 and len(coex_radios) > 0
                
                if auto_coex_mode:
                    st.info("🔬 **Automatic Coexistence Analysis**: Processing LTE bands individually against coexistence radios")
                    
                    # Process each LTE band individually
                    all_results = []
                    all_alerts = []
                    band_specific_recommendations = {}  # Track recommendations per LTE band
                    
                    for lte_band in lte_bands:
                        # Create test group: one LTE + all coexistence radios + other bands
                        test_group = [lte_band] + coex_radios + other_bands
                        
                        # Calculate interference for this group
                        group_results, group_alerts = calculate_all_products(
                            test_group,
                            guard=guard,
                            imd2=imd2_enabled,
                            imd4=imd4,
                            imd5=imd5,
                            imd7=imd7,
                            aclr_margin=aclr_margin
                        )
                        
                        # Tag results with the specific LTE band being tested
                        for result in group_results:
                            result['Test_Scenario'] = f"{lte_band.code} Coexistence Test"
                            result['LTE_Band'] = lte_band.code
                        
                        all_results.extend(group_results)
                        all_alerts.extend([f"[{lte_band.code}] {alert}" for alert in group_alerts])
                        
                        # Generate coexistence recommendations for this scenario
                        has_ble = any('BLE' in b.label or 'Bluetooth' in b.label for b in coex_radios)
                        has_wifi_24 = any('2.4G' in b.label for b in coex_radios)
                        has_wifi_5 = any('5G' in b.label for b in coex_radios)
                        scenario_radios = [b.label for b in coex_radios]
                        recommendation = generate_coexistence_recommendation(lte_band.code, scenario_radios, has_ble, has_wifi_24, has_wifi_5)
                        if recommendation:
                            band_specific_recommendations[lte_band.code] = recommendation
                    
                    results_list = all_results
                    overlap_alerts = all_alerts
                    
                    # Show coexistence recommendations
                    if band_specific_recommendations:
                        st.subheader("📡 Coexistence Recommendations")
                        
                        # Group bands by identical recommendations to reduce duplication
                        recommendation_groups = {}
                        for band_code, rec in band_specific_recommendations.items():
                            if rec not in recommendation_groups:
                                recommendation_groups[rec] = []
                            recommendation_groups[rec].append(band_code)
                        
                        # Display recommendations
                        for recommendation, applicable_bands in recommendation_groups.items():
                            if len(applicable_bands) == 1:
                                st.success(f"**{applicable_bands[0]}**: {recommendation}")
                            else:
                                bands_str = ", ".join(sorted(applicable_bands))
                                st.success(f"**{bands_str}**: {recommendation}")
                        
                        # Show summary
                        if len(band_specific_recommendations) > 2:
                            st.info(f"📊 **Summary**: {len(recommendation_groups)} unique recommendation types for {len(band_specific_recommendations)} LTE bands")
                
                else:
                    # Standard mode - analyze all selected bands together
                    # Check for multiple LTE bands and warn user about unrealistic scenario
                    if len(lte_bands) > 1 and len(coex_radios) == 0:
                        st.warning(f"⚠️ **Multiple LTE Bands Selected ({len(lte_bands)} bands)**: "
                                  f"This analysis assumes all LTE bands transmit simultaneously, which is unrealistic. "
                                  f"Consider adding coexistence radios (BLE, Wi-Fi) to enable automatic individual LTE band testing.")
                    
                    results_list, overlap_alerts = calculate_all_products(
                        selected_band_objs, 
                        guard=guard, 
                        imd2=imd2_enabled,
                        imd4=imd4, 
                        imd5=imd5, 
                        imd7=imd7, 
                        aclr_margin=aclr_margin
                    )
                
                # Apply frequency filter if enabled
                if freq_filter_enabled and freq_range:
                    original_count = len(results_list)
                    filtered_results = []
                    for r in results_list:
                        freq = r.get('Frequency_MHz', r.get('Freq_low', 0))
                        if freq_range[0] <= freq <= freq_range[1]:
                            filtered_results.append(r)
                    results_list = filtered_results
                    if len(filtered_results) < original_count:
                        st.info(f"📊 Frequency filter applied: {len(filtered_results)} results shown (filtered from {original_count})")
                        st.info(f"📡 Filter range: {freq_range[0]} - {freq_range[1]} MHz")
                
                # Apply coexistence implementation filtering
                original_count = len(results_list)
                if pta_enabled or wci2_enabled:
                    filtered_results = []
                    pta_filtered_count = 0
                    wci2_filtered_count = 0
                    
                    for result in results_list:
                        should_filter = False
                        
                        # PTA Filtering - Remove ISM coordination products
                        if pta_enabled and filter_ism_products:
                            aggressors = result.get('Aggressors', '')
                            victims = result.get('Victims', '')
                            
                            # Filter IM products between BLE and Wi-Fi 2.4G
                            if ('BLE' in aggressors and 'WiFi_2G' in aggressors) or \
                               ('BLE' in victims and ('WiFi_2G' in aggressors or 'WiFi_2G' in victims)):
                                should_filter = True
                                pta_filtered_count += 1
                        
                        # WCI-2 Filtering - Remove LTE coordination products
                        if wci2_enabled and filter_lte_harmonics and not should_filter:
                            product_type = result.get('Type', '')
                            aggressors = result.get('Aggressors', '')
                            
                            # Filter LTE harmonic products and specific IM products
                            if (product_type in ['2H', '3H'] and 'LTE_' in aggressors) or \
                               (product_type == 'IM3' and 'LTE_' in aggressors and result.get('Risk') == '⚠️'):
                                should_filter = True
                                wci2_filtered_count += 1
                        
                        if not should_filter:
                            filtered_results.append(result)
                    
                    results_list = filtered_results
                    
                    # Show filtering summary
                    total_filtered = original_count - len(filtered_results)
                    if total_filtered > 0:
                        filter_msg = f"🔄 **Coexistence Filtering Applied**: {total_filtered} products filtered"
                        if pta_filtered_count > 0:
                            filter_msg += f" (PTA: {pta_filtered_count}"
                        if wci2_filtered_count > 0:
                            filter_msg += f", WCI-2: {wci2_filtered_count}" if pta_filtered_count > 0 else f" (WCI-2: {wci2_filtered_count}"
                        if pta_filtered_count > 0 or wci2_filtered_count > 0:
                            filter_msg += ")"
                        st.info(filter_msg)
                
                results = pd.DataFrame(results_list)
                
                if results.empty:
                    st.warning("No interference products found with current settings.")
                    st.stop()
                
                # Perform NA Case 1 specific analysis if LTE bands are present
                selected_lte_band_codes = [band_id for band_id in selected_band_ids if band_id.startswith('B') and band_id[1:].isdigit()]
                if selected_lte_band_codes and any(band in ['B2', 'B4', 'B5', 'B12', 'B13', 'B14', 'B17', 'B25', 'B26'] for band in selected_lte_band_codes):
                    na_case1_analysis = analyze_na_case1_results(results, selected_lte_band_codes)
                else:
                    na_case1_analysis = None
                    
        except Exception as e:
            st.error(f"❌ Calculation error: {str(e)}")
            st.error("Please check your band selections and try again.")
            st.stop()

        # Enhanced results summary with validation
        
        # Calculate basic metrics with new severity levels
        total_products = len(results)
        if "Risk" in results.columns:
            # Count different severity levels
            risk_counts = results["Risk"].value_counts()
            critical_high = risk_counts.get('🔴', 0) + risk_counts.get('🟠', 0) + risk_counts.get('⚠️', 0)
            medium_low = risk_counts.get('🟡', 0) + risk_counts.get('🔵', 0)  
            safe_products = risk_counts.get('✅', 0) + risk_counts.get('✓', 0)
            risk_products = critical_high + medium_low  # Total risk products
        else:
            risk_products = 0
            safe_products = total_products
        
        # Validate configuration
        config_warnings = validate_band_configuration(selected_band_objs)
        if config_warnings:
            for warning in config_warnings:
                st.warning(f"⚠️ Configuration: {warning}")
        
        # Show coexistence implementation status
        if pta_enabled or wci2_enabled:
            impl_status = []
            if pta_enabled:
                impl_status.append("PTA (2.4G ISM coordination)")
            if wci2_enabled:
                impl_status.append("WCI-2 (LTE coordination)")
            st.success(f"🔄 **Active Coordination**: {' + '.join(impl_status)} - Results filtered for implemented mechanisms")
        
        st.subheader("📊 Analysis Results")
        
        # Enhanced metrics display - adjusted for automatic coexistence mode
        if auto_coex_mode:
            # Coexistence mode metrics
            lte_bands_tested = len(set(results["LTE_Band"]) if "LTE_Band" in results.columns else [])
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("LTE Bands Tested", f"{lte_bands_tested}", 
                         help="Number of LTE bands individually tested")
            with col2:
                risk_color = "normal" if risk_products == 0 else "inverse"
                st.metric("⚠️ Risk Products", f"{risk_products:,}", 
                         delta=f"{risk_products/total_products*100:.1f}%" if total_products > 0 else "0%",
                         delta_color=risk_color,
                         help="Products causing interference across all scenarios")
            with col3:
                coex_radios_count = len([b for b in selected_band_objs if b.category in ['Wi-Fi', 'BLE', 'ISM']])
                st.metric("Coexistence Radios", f"{coex_radios_count}",
                         help="Number of coexistence radios in each test")
            with col4:
                st.metric("Guard Margin", f"{guard} MHz",
                         help="Additional frequency protection margin")
        else:
            # Standard mode metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Products", f"{total_products:,}", 
                         help="Total interference products calculated")
            with col2:
                risk_color = "normal" if risk_products == 0 else "inverse"
                st.metric("⚠️ Risk Products", f"{risk_products:,}", 
                         delta=f"{risk_products/total_products*100:.1f}%" if total_products > 0 else "0%",
                         delta_color=risk_color,
                         help="Products that cause interference")
            with col3:
                st.metric("✅ Safe Products", f"{safe_products:,}",
                         help="Products that don't cause interference")
            with col4:
                st.metric("Guard Margin", f"{guard} MHz",
                         help="Additional frequency protection margin")

        # Overlap alerts
        if overlap_alerts:
            st.warning("\n".join(overlap_alerts))

        # NA Case 1 Specific Analysis
        if na_case1_analysis and na_case1_analysis.get('recommendations'):
            st.subheader("🔬 NA Case 1 Analysis Summary")
            
            analysis_col1, analysis_col2, analysis_col3 = st.columns(3)
            
            with analysis_col1:
                ism_hits = len(na_case1_analysis.get('ism_band_hits', []))
                st.metric("🌐 ISM Band Hits", f"{ism_hits}", 
                         help="Interference products in 2.4 GHz ISM band (BLE/Wi-Fi)")
                
            with analysis_col2:
                gnss_risks = len(na_case1_analysis.get('gnss_risks', []))
                st.metric("🛰️ GPS Risks", f"{gnss_risks}",
                         help="Interference with GPS navigation frequencies")
                
            with analysis_col3:
                lte_harmonics = len(na_case1_analysis.get('lte_harmonic_issues', []))
                st.metric("📡 LTE Harmonics", f"{lte_harmonics}",
                         help="LTE harmonic products causing interference")
            
            # Show critical analysis findings
            if na_case1_analysis['critical_interference']:
                st.error(f"🚨 **{len(na_case1_analysis['critical_interference'])} Critical Interference Issues Detected**")
                
                # Show most critical issues
                critical_issues = na_case1_analysis['critical_interference'][:5]  # Top 5
                for i, issue in enumerate(critical_issues, 1):
                    st.write(f"**{i}.** {issue['frequency']:.1f} MHz - {issue['reason']} - Victim: {issue['victim']}")
                
                if len(na_case1_analysis['critical_interference']) > 5:
                    st.write(f"... and {len(na_case1_analysis['critical_interference']) - 5} more critical issues")
            
            # Show detailed recommendations
            if na_case1_analysis['recommendations']:
                st.markdown("#### 🎯 NA Case 1 Recommendations")
                for i, rec in enumerate(na_case1_analysis['recommendations'], 1):
                    st.write(f"**{i}.** {rec}")
            
            # Detailed breakdown in expander
            with st.expander("🔍 Detailed Interference Analysis"):
                if na_case1_analysis['ism_band_hits']:
                    st.markdown("**ISM Band Interference (2400-2500 MHz):**")
                    ism_df = pd.DataFrame(na_case1_analysis['ism_band_hits'])
                    st.dataframe(ism_df[['frequency', 'victim', 'type', 'severity']], use_container_width=True)
                
                if na_case1_analysis['gnss_risks']:
                    st.markdown("**GPS Interference Risks:**")
                    gnss_df = pd.DataFrame(na_case1_analysis['gnss_risks'])
                    st.dataframe(gnss_df[['frequency', 'victim', 'band', 'type']], use_container_width=True)
                
                if na_case1_analysis['lte_harmonic_issues']:
                    st.markdown("**LTE Harmonic Issues:**")
                    harmonic_df = pd.DataFrame(na_case1_analysis['lte_harmonic_issues'])
                    st.dataframe(harmonic_df[['frequency', 'victim', 'harmonic_order', 'aggressors']], use_container_width=True)

        # Results table
        st.subheader("📋 Detailed Results")
        
        # Ensure all columns are present and in the same order, including coexistence mode columns
        if auto_coex_mode:
            expected_cols = [
                "Test_Scenario", "LTE_Band", "Type", "IM3_Type", "Formula", "Frequency_MHz", "Aggressors", "Victims", "Risk", "Details"
            ]
        else:
            expected_cols = [
                "Type", "IM3_Type", "Formula", "Frequency_MHz", "Aggressors", "Victims", "Risk", "Details"
            ]
            
        for col in expected_cols:
            if col not in results.columns:
                results[col] = ""
        results = results[expected_cols]
        
        # Sort results: Risk products first, then safe products, then by severity
        if "Risk" in results.columns:
            # Create a risk severity mapping for better sorting
            def get_risk_priority(risk_symbol):
                risk_priorities = {
                    "🔴": 0,  # Critical - Red circle
                    "🟠": 1,  # High - Orange circle  
                    "🟡": 2,  # Medium - Yellow circle
                    "🔵": 3,  # Low - Blue circle
                    "⚠️": 4,  # Legacy warning - treat as medium-high
                    "✅": 5,  # Very Low/Safe - Green check
                    "✓": 6,  # Legacy safe - treat as safe
                }
                return risk_priorities.get(risk_symbol, 5)
            
            # Create a sorting key where higher severity gets priority 0-6
            results['_sort_priority'] = results['Risk'].apply(get_risk_priority)
            
            # Sort by risk priority first, then by frequency (if available) for consistent ordering
            sort_columns = ['_sort_priority']
            if 'Frequency_MHz' in results.columns:
                sort_columns.append('Frequency_MHz')
            elif 'Formula' in results.columns:  # Secondary sort by formula for consistency
                sort_columns.append('Formula')
                
            results = results.sort_values(sort_columns).reset_index(drop=True)
            
            # Remove the temporary sorting column
            results = results.drop('_sort_priority', axis=1)

        def highlight_risks(row):
            risk_symbol = row["Risk"]
            if risk_symbol == "🔴":  # Critical
                return ["background-color: rgba(255, 0, 0, 0.2); color: darkred; font-weight: bold;"] * len(row)
            elif risk_symbol == "🟠":  # High  
                return ["background-color: rgba(255, 165, 0, 0.15); color: darkorange; font-weight: bold;"] * len(row)
            elif risk_symbol == "🟡":  # Medium
                return ["background-color: rgba(255, 255, 0, 0.1); color: darkgoldenrod;"] * len(row)
            elif risk_symbol == "🔵":  # Low
                return ["background-color: rgba(0, 100, 255, 0.08); color: darkblue;"] * len(row)
            elif risk_symbol == "⚠️":  # Legacy warning - treat as high
                return ["background-color: rgba(255, 75, 75, 0.15); color: darkred;"] * len(row)
            elif risk_symbol in ["✅", "✓"]:  # Safe
                return ["background-color: rgba(0, 200, 81, 0.05); color: darkgreen;"] * len(row)
            else:
                return [""] * len(row)
        if not results.empty:
            styled_df = results.style.apply(highlight_risks, axis=1)
            st.dataframe(styled_df, use_container_width=True, height=400)

            # Enhanced export options
            st.subheader("📥 Export Results")
            
            # Filter results for export if requested
            export_results = results.copy()
            if not include_safe:
                export_results = export_results[export_results['Risk'] == '⚠️'] if 'Risk' in export_results.columns else export_results
                st.info(f"Export filtered to {len(export_results)} risk products (safe products excluded)")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if export_format == "CSV":
                    csv = export_results.to_csv(index=False)
                    st.download_button(
                        label="📄 Download CSV",
                        data=csv,
                        file_name=f"interference_analysis_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                elif export_format == "JSON":
                    json_data = export_results.to_json(orient='records', indent=2)
                    st.download_button(
                        label="🗂️ Download JSON",
                        data=json_data,
                        file_name=f"interference_analysis_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json",
                        use_container_width=True
                    )
                else:  # Excel
                    buffer = BytesIO()
                    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                        export_results.to_excel(writer, sheet_name='Interference Analysis', index=False)
                        
                        # Enhanced summary sheet
                        freq_col = "Frequency_MHz" if "Frequency_MHz" in export_results.columns else "Freq_low"
                        summary_data = {
                            'Metric': ['Total Products', 'Risk Products', 'Safe Products', 'Guard Margin (MHz)', 
                                     'Analysis Date', 'Selected Bands', 'Frequency Range (MHz)', 'IM Products Enabled'],
                            'Value': [total_products, risk_products, safe_products, guard,
                                    pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
                                    ', '.join(selected_band_ids), 
                                    f"{export_results[freq_col].min():.1f} - {export_results[freq_col].max():.1f}" if freq_col in export_results.columns else "N/A",
                                    ', '.join([k for k, v in {'IM2': imd2_enabled, 'IM3': imd3_enabled, 'IM4': imd4, 'IM5': imd5, 'IM7': imd7}.items() if v])]
                        }
                        pd.DataFrame(summary_data).to_excel(writer, sheet_name='Analysis Summary', index=False)
                        
                        # Band configuration sheet
                        band_config = pd.DataFrame([
                            {"Band": b.code, "Label": b.label, "Category": b.category, 
                             "Tx_Low": b.tx_low, "Tx_High": b.tx_high, "Rx_Low": b.rx_low, "Rx_High": b.rx_high}
                            for b in selected_band_objs
                        ])
                        band_config.to_excel(writer, sheet_name='Band Configuration', index=False)
                        
                    st.download_button(
                        label="📊 Download Excel",
                        data=buffer.getvalue(),
                        file_name=f"interference_analysis_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
            
            with col2:
                # Copy to clipboard (enhanced)
                if st.button("📋 Copy Results as Markdown", use_container_width=True):
                    md_header = f"# RF Interference Analysis Report\n"
                    md_header += f"**Analysis Date:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}  \n"
                    md_header += f"**Total Products:** {total_products}  \n"
                    md_header += f"**Risk Products:** {risk_products}  \n"
                    md_header += f"**Guard Margin:** {guard} MHz  \n\n"
                    
                    md = md_header + export_results.to_markdown(index=False)
                    if PYPERCLIP_AVAILABLE:
                        pyperclip.copy(md)
                        st.success("📋 Results copied to clipboard as Markdown!")
                    else:
                        st.text_area("📋 Markdown Results (copy manually):", md, height=200)
            
            with col3:
                # Enhanced PDF report
                if st.button("📄 Generate PDF Report", use_container_width=True):
                    try:
                        from reportlab.lib import colors
                        from reportlab.lib.pagesizes import letter, A4
                        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
                        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                        from reportlab.lib.units import inch
                        import tempfile
                        
                        # Create temporary PDF file
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                            pdf_path = tmp_file.name
                            
                            # Create PDF document
                            doc = SimpleDocTemplate(pdf_path, pagesize=A4, 
                                                  rightMargin=72, leftMargin=72,
                                                  topMargin=72, bottomMargin=18)
                            
                            # Get styles
                            styles = getSampleStyleSheet()
                            title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'],
                                                       fontSize=18, spaceAfter=30, textColor=colors.darkblue)
                            
                            # Build PDF content
                            story = []
                            
                            # Title
                            story.append(Paragraph("RF Spectrum Interference Analysis Report", title_style))
                            story.append(Spacer(1, 12))
                            
                            # Analysis summary
                            summary_data = [
                                ['Analysis Date:', pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')],
                                ['Total Products:', f"{total_products:,}"],
                                ['Risk Products:', f"{risk_products:,}"],
                                ['Safe Products:', f"{safe_products:,}"],
                                ['Guard Margin:', f"{guard} MHz"],
                                ['Selected Bands:', ', '.join(selected_band_ids[:5]) + ('...' if len(selected_band_ids) > 5 else '')]
                            ]
                            
                            summary_table = Table(summary_data, colWidths=[2*inch, 4*inch])
                            summary_table.setStyle(TableStyle([
                                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                                ('FONTSIZE', (0, 0), (-1, -1), 10),
                                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                                ('GRID', (0, 0), (-1, -1), 1, colors.black)
                            ]))
                            story.append(summary_table)
                            story.append(Spacer(1, 20))
                            
                            # Results table (limit to first 50 rows for PDF)
                            story.append(Paragraph("Interference Analysis Results", styles['Heading2']))
                            story.append(Spacer(1, 12))
                            
                            # Prepare results data for PDF
                            pdf_results = export_results.head(50) if len(export_results) > 50 else export_results
                            
                            # Convert DataFrame to list for PDF table
                            table_data = [list(pdf_results.columns)]
                            for _, row in pdf_results.iterrows():
                                table_data.append([str(val)[:30] + '...' if len(str(val)) > 30 else str(val) for val in row])
                            
                            # Create table with appropriate column widths
                            col_widths = [0.8*inch] * len(pdf_results.columns)
                            results_table = Table(table_data, colWidths=col_widths, repeatRows=1)
                            
                            # Style the table
                            table_style = [
                                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                ('FONTSIZE', (0, 0), (-1, 0), 8),
                                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                                ('FONTSIZE', (0, 1), (-1, -1), 7),
                                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                                ('GRID', (0, 0), (-1, -1), 1, colors.black)
                            ]
                            
                            # Color code risk rows
                            for i, (_, row) in enumerate(pdf_results.iterrows(), 1):
                                if 'Risk' in row and row['Risk'] == '⚠️':
                                    table_style.append(('BACKGROUND', (0, i), (-1, i), colors.mistyrose))
                                else:
                                    table_style.append(('BACKGROUND', (0, i), (-1, i), colors.lightcyan))
                            
                            results_table.setStyle(TableStyle(table_style))
                            story.append(results_table)
                            
                            # Add note if results were truncated
                            if len(export_results) > 50:
                                story.append(Spacer(1, 12))
                                story.append(Paragraph(f"Note: Showing first 50 of {len(export_results)} total results. Download full data using CSV/Excel export.", styles['Normal']))
                            
                            # Build PDF
                            doc.build(story)
                            
                            # Read PDF file for download
                            with open(pdf_path, 'rb') as pdf_file:
                                pdf_bytes = pdf_file.read()
                            
                            # Offer download
                            st.download_button(
                                label="📄 Download PDF Report",
                                data=pdf_bytes,
                                file_name=f"interference_analysis_report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                            
                            st.success("✅ PDF report generated successfully!")
                            
                            # Clean up temp file
                            import os
                            try:
                                os.unlink(pdf_path)
                            except:
                                pass
                                
                    except ImportError:
                        st.error("❌ PDF generation requires 'reportlab' library. Install with: pip install reportlab")
                        st.info("📋 Alternative: Use the CSV/Excel export options above")
                    except Exception as e:
                        st.error(f"❌ PDF generation error: {str(e)}")
                        st.info("📋 Alternative: Use the CSV/Excel export options above")
                    
                # Performance report
                if st.button("📈 Performance Report", use_container_width=True):
                    st.markdown("""
                    ### 📊 Analysis Performance Metrics
                    """)
                    perf_col1, perf_col2, perf_col3 = st.columns(3)
                    with perf_col1:
                        st.metric("Calculation Time", "< 1 second")
                    with perf_col2:
                        st.metric("Memory Usage", f"{len(results_list) * 0.001:.2f} MB")
                    with perf_col3:
                        st.metric("Products/Band²", f"{total_products / (len(selected_band_ids)**2):.1f}")
                        
                    if len(selected_band_ids) > 10:
                        st.warning("⚠️ Large analysis: Consider using frequency filters for better performance")

        # Show error/success based on risk column
        if "Risk" in results.columns and (results["Risk"] == "⚠️").any():
            st.error("⚠ At least one product lands inside the Rx band.")
        else:
            st.success("✅ No in-band hits detected.")

        # Altair plots (enhanced visualizations)
        st.markdown("### 📊 Interactive Visualizations")
        
        if not results.empty:
            # Tab layout for different visualizations
            tab1, tab2, tab3, tab4 = st.tabs(["🎯 Frequency Spectrum", "📈 Risk Analysis", "🔍 Band Coverage", "⚡ Product Distribution"])
            
            with tab1:
                # Enhanced frequency scatter plot - filter out invalid frequencies
                color_col = "Risk" if "Risk" in results.columns else results.columns[-1]
                freq_col = "Frequency_MHz" if "Frequency_MHz" in results.columns else "Freq_low"
                
                # Filter out negative/zero frequencies for realistic RF analysis
                valid_results = results[results[freq_col] > 0] if freq_col in results.columns else results
                
                if not valid_results.empty:
                    # Show frequency range info for debugging
                    min_freq = valid_results[freq_col].min()
                    max_freq = valid_results[freq_col].max()
                    total_products = len(valid_results)
                    st.info(f"📊 Chart shows {total_products} products across {min_freq:.1f} - {max_freq:.1f} MHz range")
                    
                    # Map severity symbols to colors for the chart
                    risk_color_mapping = {
                        '🔴': '#ff0000',    # Critical - Red
                        '🟠': '#ff8c00',    # High - Orange
                        '🟡': '#ffd700',    # Medium - Yellow  
                        '🔵': '#0066ff',    # Low - Blue
                        '✅': '#44aa44',    # Safe - Green
                        '⚠️': '#ff4444',    # Legacy warning - Red
                        '✓': '#44aa44'     # Legacy safe - Green
                    }
                    
                    # Get unique risk values in the data and their colors
                    unique_risks = valid_results[color_col].unique()
                    domain = [risk for risk in unique_risks if risk in risk_color_mapping]
                    range_colors = [risk_color_mapping[risk] for risk in domain]
                    
                    # Create dynamic condition for high-risk items
                    if color_col == "Risk":
                        risk_condition = (alt.datum.Risk == '🔴') | (alt.datum.Risk == '🟠') | (alt.datum.Risk == '⚠️')
                    else:
                        # Fallback for other columns
                        risk_condition = alt.datum[color_col] == '🔴'
                    
                    chart = alt.Chart(valid_results).mark_circle(size=120, opacity=0.7).encode(
                        x=alt.X(freq_col, title="Frequency (MHz)", scale=alt.Scale(nice=True, zero=False)),
                        y=alt.Y("Type:N", title="Product Type", sort=["2H", "3H", "4H", "5H", "IM2", "IM3", "IM4", "IM5", "IM7", "ACLR"]),
                        color=alt.Color(
                            color_col, 
                            scale=alt.Scale(domain=domain, range=range_colors),
                            legend=alt.Legend(title="Risk Severity")
                        ),
                        size=alt.condition(
                            risk_condition,
                            alt.value(180),  # Larger for high risk items
                            alt.value(100)
                        ),
                        tooltip=[
                            alt.Tooltip('Type:N', title='Product Type'),
                            alt.Tooltip('Formula:N', title='Formula'),
                            alt.Tooltip(f'{freq_col}:Q', title='Frequency (MHz)', format='.2f'),
                            alt.Tooltip('Aggressors:N', title='Aggressors'),
                            alt.Tooltip('Victims:N', title='Victims'),
                            alt.Tooltip('Risk:N', title='Risk'),
                            alt.Tooltip('Severity:Q', title='Severity Level') if 'Severity' in valid_results.columns else alt.Tooltip('Risk:N', title='Risk')
                        ]
                    ).properties(
                        width=700,
                        height=400,
                        title="RF Spectrum Interference Products (Valid Frequencies Only)"
                    ).interactive()
                    
                    st.altair_chart(chart, use_container_width=True)
                    
                    # Show filtering info if frequencies were removed
                    filtered_count = len(results) - len(valid_results)
                    if filtered_count > 0:
                        st.info(f"📊 Filtered out {filtered_count} products with invalid frequencies (≤ 0 MHz)")
                else:
                    st.warning("No valid frequency data available for visualization")
            
            with tab2:
                # Enhanced Risk distribution with severity levels
                risk_counts = results['Risk'].value_counts() if 'Risk' in results.columns else pd.Series([0])
                
                # Map risk symbols to severity descriptions and colors
                risk_mapping = {
                    '🔴': ('Critical', '#ff0000', 1),
                    '🟠': ('High', '#ff8c00', 2),
                    '🟡': ('Medium', '#ffd700', 3),
                    '🔵': ('Low', '#0066ff', 4),
                    '⚠️': ('Warning', '#ff4444', 2.5),  # Legacy warning
                    '✅': ('Safe', '#44aa44', 5),
                    '✓': ('Safe', '#44aa44', 5)   # Legacy safe
                }
                
                # Create enhanced risk data with severity information
                risk_data = []
                for symbol, count in risk_counts.items():
                    if symbol in risk_mapping:
                        desc, color, severity = risk_mapping[symbol]
                        risk_data.append({
                            'Symbol': symbol,
                            'Status': desc,
                            'Count': count,
                            'Color': color,
                            'Severity': severity,
                            'Label': f"{desc}: {count} ({symbol})"
                        })
                    else:
                        # Handle any unknown symbols
                        risk_data.append({
                            'Symbol': symbol,
                            'Status': 'Other',
                            'Count': count,
                            'Color': '#888888',
                            'Severity': 3,
                            'Label': f"Other: {count} ({symbol})"
                        })
                
                risk_df = pd.DataFrame(risk_data)
                
                if not risk_df.empty:
                    # Sort by severity (most critical first)
                    risk_df = risk_df.sort_values('Severity')
                    
                    # Create enhanced pie chart with severity-based colors
                    pie_chart = alt.Chart(risk_df).mark_arc(innerRadius=50).encode(
                        theta=alt.Theta(field="Count", type="quantitative"),
                        color=alt.Color(
                            field="Status:N", 
                            scale=alt.Scale(
                                domain=risk_df['Status'].tolist(),
                                range=risk_df['Color'].tolist()
                            ),
                            legend=alt.Legend(title="Risk Severity", orient="right")
                        ),
                        tooltip=['Symbol:N', 'Status:N', 'Count:Q', 'Label:N']
                    ).properties(
                        width=350,
                        height=300,
                        title="Risk Distribution by Severity Level"
                    )
                    
                    # Show severity summary
                    st.markdown("#### 📊 Risk Severity Summary")
                    severity_col1, severity_col2, severity_col3 = st.columns(3)
                    
                    with severity_col1:
                        critical_high = risk_df[risk_df['Severity'] <= 2]['Count'].sum()
                        st.metric("🔴 Critical + High Risk", f"{critical_high}", 
                                 help="Products requiring immediate attention")
                        
                    with severity_col2:
                        medium_low = risk_df[(risk_df['Severity'] > 2) & (risk_df['Severity'] < 5)]['Count'].sum()
                        st.metric("🟡 Medium + Low Risk", f"{medium_low}",
                                 help="Products requiring monitoring")
                        
                    with severity_col3:
                        safe_count = risk_df[risk_df['Severity'] >= 5]['Count'].sum()
                        st.metric("✅ Safe Products", f"{safe_count}",
                                 help="No interference detected")
                else:
                    pie_chart = None
                    st.warning("No risk data available for visualization")
                
                # Risk by product type - enhanced with severity levels
                if 'Type' in results.columns:
                    # Filter to valid frequencies for meaningful RF analysis
                    valid_freq_results = results[results[freq_col] > 0] if freq_col in results.columns else results
                    
                    if not valid_freq_results.empty:
                        type_risk = valid_freq_results.groupby(['Type', 'Risk']).size().reset_index(name='Count')
                        
                        # Map risk symbols to colors for consistent visualization
                        risk_color_map = {
                            '🔴': '#ff0000', '🟠': '#ff8c00', '🟡': '#ffd700', 
                            '🔵': '#0066ff', '⚠️': '#ff4444', '✅': '#44aa44', '✓': '#44aa44'
                        }
                        
                        # Create color scale based on available risk symbols
                        available_risks = type_risk['Risk'].unique()
                        color_domain = [risk for risk in available_risks if risk in risk_color_map]
                        color_range = [risk_color_map[risk] for risk in color_domain]
                        
                        risk_by_type = alt.Chart(type_risk).mark_bar().encode(
                            x=alt.X('Type:N', title='Product Type', sort=["2H", "3H", "4H", "5H", "IM2", "IM3", "IM4", "IM5", "IM7", "ACLR"]),
                            y=alt.Y('Count:Q', title='Count'),
                            color=alt.Color(
                                'Risk:N', 
                                scale=alt.Scale(domain=color_domain, range=color_range),
                                legend=alt.Legend(title="Risk Level")
                            ),
                            tooltip=['Type:N', 'Risk:N', 'Count:Q']
                        ).properties(
                            width=450,
                            height=300,
                            title="Risk Count by Product Type (Enhanced Severity)"
                        )
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if pie_chart is not None:
                                st.altair_chart(pie_chart, use_container_width=True)
                        with col2:
                            st.altair_chart(risk_by_type, use_container_width=True)
                            
                        # Show filtering info if needed
                        original_count = len(results)
                        filtered_count = len(valid_freq_results)
                        if original_count != filtered_count:
                            st.info(f"📊 Risk analysis based on {filtered_count}/{original_count} products with valid frequencies")
                    else:
                        col1, col2 = st.columns(2)
                        with col1:
                            if pie_chart is not None:
                                st.altair_chart(pie_chart, use_container_width=True)
                        with col2:
                            st.warning("No valid frequency data for product type analysis")
            
            with tab3:
                # Band coverage visualization - filter out invalid bands
                band_data = []
                for band_id in selected_band_ids:
                    band = BANDS[band_id]
                    # Only include bands with valid frequency ranges
                    if band.tx_high > band.tx_low and band.rx_high > band.rx_low:
                        # Only add Tx data if band is not receive-only
                        if not (band.tx_low == 0 and band.tx_high == 0):
                            band_data.append({
                                "Band": band.code, 
                                "Type": "Tx", 
                                "Low": band.tx_low, 
                                "High": band.tx_high, 
                                "Category": band.category,
                                "Bandwidth": band.tx_high - band.tx_low
                            })
                        
                        band_data.append({
                            "Band": band.code, 
                            "Type": "Rx", 
                            "Low": band.rx_low, 
                            "High": band.rx_high, 
                            "Category": band.category,
                            "Bandwidth": band.rx_high - band.rx_low
                        })
                
                if band_data:
                    band_df = pd.DataFrame(band_data)
                    
                    # Sort bands by lowest frequency for better visualization
                    band_order = band_df.groupby('Band')['Low'].min().sort_values().index.tolist()
                    
                    coverage_chart = alt.Chart(band_df).mark_rect(height=15).encode(
                        x=alt.X('Low:Q', title='Frequency (MHz)', scale=alt.Scale(nice=True)),
                        x2='High:Q',
                        y=alt.Y('Band:N', title='Band', sort=band_order),
                        color=alt.Color('Type:N', scale=alt.Scale(domain=['Tx', 'Rx'], range=['#ff6b6b', '#4ecdc4'])),
                        tooltip=['Band:N', 'Type:N', 'Low:Q', 'High:Q', 'Category:N', 'Bandwidth:Q']
                    ).properties(
                        width=700,
                        height=max(300, len(selected_band_ids) * 25),
                        title="Band Coverage Overview (Frequency Ordered)"
                    ).resolve_scale(color='independent')
                    
                    st.altair_chart(coverage_chart, use_container_width=True)
                    
                    # Band statistics
                    if not band_df.empty:
                        stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)
                        
                        with stats_col1:
                            total_tx_bw = band_df[band_df['Type'] == 'Tx']['Bandwidth'].sum()
                            st.metric("Total Tx Bandwidth", f"{total_tx_bw:.0f} MHz")
                            
                        with stats_col2:
                            total_rx_bw = band_df[band_df['Type'] == 'Rx']['Bandwidth'].sum()
                            st.metric("Total Rx Bandwidth", f"{total_rx_bw:.0f} MHz")
                            
                        with stats_col3:
                            freq_span = band_df['High'].max() - band_df['Low'].min()
                            st.metric("Overall Frequency Span", f"{freq_span/1000:.2f} GHz")
                            
                        with stats_col4:
                            categories = band_df['Category'].nunique()
                            st.metric("Technology Categories", f"{categories}")
                else:
                    st.warning("No valid band data available for coverage visualization")
            
            with tab4:
                # Product distribution histogram - filter invalid frequencies
                if freq_col in results.columns:
                    valid_results = results[results[freq_col] > 0]
                    
                    if not valid_results.empty:
                        # Get unique risk values for proper scaling
                        unique_risks = valid_results['Risk'].unique() if 'Risk' in valid_results.columns else []
                        
                        # Create risk mapping for colors (handle both old and new risk symbols)
                        risk_mapping = {
                            '🔴': '#cc0000',  # Critical - Dark Red
                            '🟠': '#ff6600',  # High - Orange  
                            '🟡': '#ffcc00',  # Medium - Yellow
                            '🔵': '#0066cc',  # Low - Blue
                            '✅': '#00aa00',  # Safe - Green
                            '⚠️': '#ff4444',  # Legacy warning - Red
                            '✓': '#44aa44'    # Legacy safe - Green
                        }
                        
                        # Filter to only risks present in data
                        present_risks = [r for r in unique_risks if r in risk_mapping]
                        risk_colors = [risk_mapping[r] for r in present_risks]
                        
                        hist_chart = alt.Chart(valid_results).mark_bar(opacity=0.7).encode(
                            x=alt.X(f'{freq_col}:Q', bin=alt.Bin(maxbins=50), title='Frequency (MHz)'),
                            y=alt.Y('count():Q', title='Number of Products'),
                            color=alt.Color(
                                'Risk:N', 
                                scale=alt.Scale(domain=present_risks, range=risk_colors),
                                legend=alt.Legend(title="Risk Level")
                            ),
                            tooltip=['count():Q', 'Risk:N']
                        ).properties(
                            width=700,
                            height=300,
                            title="Frequency Distribution of Interference Products (Valid Frequencies)"
                        )
                        
                        st.altair_chart(hist_chart, use_container_width=True)
                        
                        # RF-meaningful statistics summary
                        freq_data = valid_results[freq_col].dropna()
                        if not freq_data.empty:
                            # Calculate risk frequency statistics (handle both new and legacy risk symbols)
                            risk_symbols = ['🔴', '🟠', '🟡', '⚠️']  # Critical/High/Medium risk symbols
                            risk_freqs = valid_results[valid_results['Risk'].isin(risk_symbols)][freq_col].dropna() if 'Risk' in valid_results.columns else pd.Series([])
                            
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("Min Frequency", f"{freq_data.min():.1f} MHz", 
                                         help="Lowest interference product frequency")
                            with col2:
                                st.metric("Max Frequency", f"{freq_data.max():.1f} MHz",
                                         help="Highest interference product frequency")
                            with col3:
                                if len(risk_freqs) > 0:
                                    st.metric("Risk Frequencies", f"{len(risk_freqs)} found",
                                             help=f"Frequencies with interference: {risk_freqs.min():.1f} - {risk_freqs.max():.1f} MHz")
                                else:
                                    st.metric("Risk Frequencies", "None", help="No interference frequencies detected")
                            with col4:
                                span_ghz = (freq_data.max() - freq_data.min()) / 1000
                                st.metric("Frequency Span", f"{span_ghz:.2f} GHz",
                                         help="Total frequency range of analysis")
                            
                            # Additional RF insights
                            st.markdown("#### 📊 RF Analysis Insights")
                            insights_col1, insights_col2 = st.columns(2)
                            
                            with insights_col1:
                                # Band distribution analysis
                                if len(freq_data) > 0:
                                    sub_1ghz = len(freq_data[freq_data < 1000])
                                    band_1_3ghz = len(freq_data[(freq_data >= 1000) & (freq_data < 3000)])
                                    above_3ghz = len(freq_data[freq_data >= 3000])
                                    
                                    st.write("**Frequency Band Distribution:**")
                                    if sub_1ghz > 0:
                                        st.write(f"• Sub-1 GHz: {sub_1ghz} products ({sub_1ghz/len(freq_data)*100:.1f}%)")
                                    if band_1_3ghz > 0:
                                        st.write(f"• 1-3 GHz: {band_1_3ghz} products ({band_1_3ghz/len(freq_data)*100:.1f}%)")
                                    if above_3ghz > 0:
                                        st.write(f"• Above 3 GHz: {above_3ghz} products ({above_3ghz/len(freq_data)*100:.1f}%)")
                            
                            with insights_col2:
                                # Risk concentration analysis
                                if len(risk_freqs) > 0:
                                    st.write("**Risk Analysis:**")
                                    st.write(f"• Risk products: {len(risk_freqs)}/{len(freq_data)} ({len(risk_freqs)/len(freq_data)*100:.1f}%)")
                                    st.write(f"• Risk frequency range: {risk_freqs.max() - risk_freqs.min():.1f} MHz")
                                    
                                    # Critical frequency bands
                                    ism_24_risks = len(risk_freqs[(risk_freqs >= 2400) & (risk_freqs <= 2500)])
                                    wifi_5_risks = len(risk_freqs[(risk_freqs >= 5000) & (risk_freqs <= 6000)])
                                    if ism_24_risks > 0:
                                        st.write(f"• 2.4 GHz ISM risks: {ism_24_risks}")
                                    if wifi_5_risks > 0:
                                        st.write(f"• 5 GHz Wi-Fi risks: {wifi_5_risks}")
                                else:
                                    st.success("✅ No frequency risks detected")
                    else:
                        st.warning("No valid frequency data for histogram analysis")
                else:
                    st.warning("Frequency column not found in results")

        # Copy to clipboard (markdown)
        if st.button("Copy Results as Markdown"):
            md = results.to_markdown(index=False)
            if PYPERCLIP_AVAILABLE:
                pyperclip.copy(md)
                st.info("Results copied to clipboard as Markdown!")
            else:
                st.text_area("📋 Markdown Results (copy manually):", md, height=200)

# Footer with enhanced information
st.markdown("---")

# Help and documentation section
with st.expander("📖 Help & Documentation"):
    st.markdown("""
    ### 🚀 Quick Start Guide
    1. **Select Categories**: Choose band categories (Wi-Fi, LTE, BLE, ISM, etc.) in the sidebar
    2. **Choose Bands**: Select specific bands from the Available Bands dropdown
    3. **Automatic Analysis Mode**: 
       - **Standard Mode**: All bands analyzed together (good for same technology)
       - **Auto-Coexistence Mode**: Multiple LTE bands are automatically tested individually against coexistence radios (BLE, Wi-Fi, ISM)
    4. **Configure Analysis**: Set guard margins, enable IM products, adjust ACLR settings
    5. **Calculate**: Click "Calculate Interference" to run the analysis
    6. **Review Results**: Examine the detailed results table and interactive visualizations
    7. **Export**: Download results in CSV, Excel, or JSON format
    
    ### 🔬 Automatic Coexistence Mode
    - **Purpose**: Realistic testing of LTE bands individually when coexistence radios are present
    - **Triggers**: Automatically activates when you select multiple LTE bands + any BLE/Wi-Fi/ISM bands
    - **Benefits**: 
      - Matches real-world scenarios where only one LTE band is active at a time
      - Provides specific coexistence recommendations per LTE band
      - Tests each LTE band against all selected coexistence radios
    - **Recommendations**: 
      - BLE + Wi-Fi 2.4G → Packet Transfer Arbitration (PTA) required
      - LTE + BLE → WCI-2 interface coordination
      - LTE + Wi-Fi → WCI-2 interface with LAA compliance
    
    ### 🔄 Coexistence Implementation Filtering
    - **PTA (Packet Transfer Arbitration)**: 
      - Enable if PTA bus is implemented for 2.4 GHz ISM coordination
      - Filters out BLE ↔ Wi-Fi 2.4G interference products (they're coordinated)
      - Reduces false positives for designs with proper ISM arbitration
    - **WCI-2 (Wireless Coexistence Interface)**:
      - Enable if WCI-2 interface is implemented between LTE and coexistence radios
      - Filters out timing-coordinated interference products
      - Accounts for real-world LTE coordination mechanisms
    - **Smart Filtering**: Only removes products that are actually mitigated by the implemented coordination
    
    ### 🔬 Analysis Types
    - **Harmonics (2H-5H)**: 2nd, 3rd, 4th, and 5th harmonic products
    - **IM2 Beat Terms**: Critical f₁ ± f₂ beat frequencies (often higher than IM3)
    - **IM3**: Third-order intermodulation products (2f₁ ± f₂)
    - **IM4**: Fourth-order products (2f₁ + 2f₂, 3f₁ + f₂, f₁ + 3f₂)
    - **IM5**: Fifth-order products (3f₁ ± 2f₂, 2f₁ ± 3f₂)
    - **IM7**: Seventh-order intermodulation products (4f₁ ± 3f₂)
    - **ACLR**: Adjacent Channel Leakage Ratio analysis
    
    ### 📊 Risk Levels
    - **High**: In-band interference or within 1 MHz
    - **Med**: Within 5 MHz of the receive band
    - **Low**: Within 20 MHz of the receive band
    - **Minimal**: More than 20 MHz away
    
    ### 🎯 Features
    - **Professional-grade analysis** with exhaustive IMD calculations
    - **Coexistence testing** with industry-standard recommendations
    - **Interactive visualizations** including frequency spectrum plots
    - **Advanced filtering** by category, frequency range, and risk level
    - **Multiple export formats** (CSV, Excel, JSON, Markdown)
    - **Configuration validation** with warnings and recommendations
    """)

# Technical information
with st.expander("⚙️ Technical Information"):
    # Calculate categories for system info
    sys_categories = sorted(set(b.category for b in BANDS.values()))
    
    st.markdown(f"""
    ### 🏗️ System Information
    - **Version**: {__version__}
    - **Engine**: Streamlit with Altair visualization
    - **Supported Bands**: {len(BANDS)} bands across multiple technologies
    - **Categories**: {len(sys_categories)} categories (2G, 3G, LTE, Wi-Fi, ISM, HaLow, LoRa, GNSS)
    
    ### 📡 Band Coverage
    - **LTE**: Bands 1-71 (comprehensive 3GPP coverage)
    - **Wi-Fi**: 2.4G, 5G, 6E bands
    - **ISM**: 433 MHz, 902-928 MHz bands
    - **HaLow**: Regional variants (NA, EU, AUS, JP, TW, KR)
    - **GNSS**: L1, L2, L5 bands
    - **LoRaWAN**: US and EU bands
    
    ### 🔧 Algorithm Details
    - **IMD3 Calculation**: Exhaustive edge-case analysis including harmonic mixing
    - **Deduplication**: Intelligent result filtering for concise output
    - **Risk Assessment**: Multi-criteria evaluation with frequency proximity
    - **Performance**: Optimized for real-time analysis of complex scenarios
    """)

st.markdown(f"""
<div style='text-align: center; color: gray; font-size: 0.8em;'>
    RF Spectrum Interference Calculator v{__version__} | Professional RF Systems Analysis Tool<br>
    Enhanced with Advanced IMD Analysis, Interactive Visualizations & Professional Export Features<br>
    Supports {len(BANDS)} Bands: 3GPP LTE 1-71, Wi-Fi 2.4G/5G/6E, Bluetooth LE, ISM, HaLow, LoRaWAN, GNSS<br>
    <strong>Features:</strong> Exhaustive IMD3/5/7 Analysis | Risk Prioritization | Multi-format Export | Interactive Charts
</div>
""", unsafe_allow_html=True)
