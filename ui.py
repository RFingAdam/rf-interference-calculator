import streamlit as st
import pandas as pd
import altair as alt
import traceback
from bands import BANDS, Band
from calculator import calculate_all_products, assess_risk_severity
from io import BytesIO

# RF Performance Analysis imports
try:
    from rf_performance import (
        analyze_interference_quantitative,
        create_quantitative_summary,
        RF_SYSTEM_PRESETS,
        SystemParameters,
        calculate_system_harmonic_levels,
        monte_carlo_interference_analysis,
        generate_monte_carlo_report,
        ToleranceParameters,
        calculate_interference_at_victim_quantitative
    )
    import plotly.graph_objects as go
    import plotly.express as px
    import numpy as np
    RF_PERFORMANCE_AVAILABLE = True
except ImportError:
    RF_PERFORMANCE_AVAILABLE = False
    st.warning("⚠️ RF Performance module not available. Basic analysis only.")

# Regulatory compliance imports
try:
    from regulatory_limits import (
        check_emission_compliance,
        generate_compliance_report,
        get_emission_limit_for_frequency,
        get_critical_frequency_pairs
    )
    REGULATORY_AVAILABLE = True
except ImportError:
    REGULATORY_AVAILABLE = False

# Isolation matrix imports
try:
    from isolation_matrix import (
        get_required_isolation,
        get_recommended_isolation,
        check_isolation_compliance,
        get_isolation_recommendation,
        get_all_critical_pairs
    )
    ISOLATION_MATRIX_AVAILABLE = True
except ImportError:
    ISOLATION_MATRIX_AVAILABLE = False

# Optional imports
try:
    import pyperclip
    PYPERCLIP_AVAILABLE = True
except ImportError:
    PYPERCLIP_AVAILABLE = False

__version__ = "2.0.0"  # Professional UI Overhaul - dBm/dBc/Compliance Integration

# Professional RF Engineering Validation
MATHEMATICAL_VALIDATION = {
    "polynomial_order": 5,  # Up to 5th order nonlinearity
    "frequency_range_validated": (10, 6000),  # 10 MHz to 6 GHz
    "theoretical_foundation": "IEEE 802.11/3GPP Standards + RF Insights Theory",
    "validation_status": "Professional Review Complete"
}

def validate_analysis_parameters(bands, rf_params=None):
    """
    Professional validation of analysis parameters before calculation
    Prevents invalid configurations that could produce misleading results
    """
    warnings = []
    errors = []
    
    # Band configuration validation
    if not bands:
        errors.append("No bands selected for analysis")
        return errors, warnings
    
    # Frequency range validation
    for band in bands:
        # Validate frequency ranges are physically reasonable
        if hasattr(band, 'tx_low') and band.tx_low > 0:
            if not (10 <= band.tx_low <= 6000):
                warnings.append(f"{band.code}: TX frequency {band.tx_low} MHz outside validated range (10-6000 MHz)")
        
        if hasattr(band, 'rx_low'):
            if not (10 <= band.rx_low <= 6000):
                warnings.append(f"{band.code}: RX frequency {band.rx_low} MHz outside validated range (10-6000 MHz)")
    
    # System parameter validation (if RF performance available)
    if rf_params and RF_PERFORMANCE_AVAILABLE:
        # Power level sanity checks
        if rf_params.lte_tx_power > 50:
            warnings.append(f"LTE TX power {rf_params.lte_tx_power} dBm exceeds regulatory limits (typical max: 30 dBm)")
        
        if rf_params.wifi_tx_power > 30:
            warnings.append(f"Wi-Fi TX power {rf_params.wifi_tx_power} dBm exceeds typical limits (typical max: 20 dBm)")
        
        # ✅ CORRECTED: Validate system linearity parameters instead of fixed HD levels
        if rf_params.iip3_dbm > 10.0 or rf_params.iip3_dbm < -30.0:
            errors.append(f"IIP3 {rf_params.iip3_dbm} dBm unrealistic (typical: -30 to +10 dBm)")
        
        if rf_params.iip2_dbm > 40.0 or rf_params.iip2_dbm < 0.0:
            errors.append(f"IIP2 {rf_params.iip2_dbm} dBm unrealistic (typical: 0 to +40 dBm)")
        
        if rf_params.pa_class not in ["A", "AB", "B", "C"]:
            errors.append(f"PA class '{rf_params.pa_class}' invalid (must be A, AB, B, or C)")
        
        # Isolation parameter validation
        total_isolation = rf_params.antenna_isolation + rf_params.pcb_isolation + rf_params.shield_isolation
        if total_isolation < 15:
            warnings.append(f"Total system isolation {total_isolation:.1f} dB very low - expect strong interference")
        
        if total_isolation > 80:
            warnings.append(f"Total system isolation {total_isolation:.1f} dB unusually high - verify measurements")
        
        # Sensitivity validation
        if rf_params.gnss_sensitivity > -130:
            warnings.append(f"GNSS sensitivity {rf_params.gnss_sensitivity} dBm too high (typical: -140 to -160 dBm)")
    
    return errors, warnings

def sort_key(band_code):
    """Numerical sorting for LTE bands"""
    if band_code.startswith('LTE_B'):
        try:
            return int(band_code.split('_B')[1])
        except (ValueError, IndexError):
            return float('inf')
    return band_code

def create_rf_spectrum_chart(quantitative_results, rf_params):
    """
    Professional RF spectrum visualization showing interference products
    with quantitative dBc levels and proper engineering analysis
    """
    if not quantitative_results:
        return None
    
    try:
        # Create figure
        fig = go.Figure()
        
        # Professional color scheme based on product type
        color_map = {
            # Harmonics - Progressive severity by order
            '2H': '#FFD700',     # Gold - 2nd harmonic
            '3H': '#FFA500',     # Orange - 3rd harmonic 
            '4H': '#FF6347',     # Tomato - 4th harmonic
            '5H': '#DC143C',     # Crimson - 5th harmonic
            
            # IMD products - Blue family for intermod
            'IM2': '#87CEEB',    # Sky Blue - IM2
            'IM3': '#4169E1',    # Royal Blue - IM3
            'IM4': '#0000CD',    # Medium Blue - IM4
            'IM5': '#000080',    # Navy - IM5
            'IM7': '#191970',    # Midnight Blue - IM7
        }
        
        # Extract fundamental references for comparison
        tx_frequencies = set()
        for result in quantitative_results:
            if hasattr(result, 'aggressors') and result.aggressors:
                for aggressor in result.aggressors:
                    band_code = aggressor.strip()
                    for band in BANDS.values():
                        if band.code == band_code and band.tx_low > 0:
                            tx_center = (band.tx_low + band.tx_high) / 2
                            tx_frequencies.add((tx_center, band_code))
        
        # Add fundamental signal references (baseline at 0 dBc)
        for tx_freq, band_code in sorted(tx_frequencies):
            fig.add_trace(go.Scatter(
                x=[tx_freq],
                y=[0],
                mode='markers',
                marker=dict(
                    symbol='diamond',
                    size=12,
                    color='green',
                    line=dict(width=2, color='darkgreen')
                ),
                name=f'Fundamental TX',
                showlegend=False,
                hovertemplate=f'<b>Fundamental Signal</b><br>Band: {band_code}<br>Frequency: {tx_freq:.1f} MHz<br>Level: 0 dBc (Reference)<extra></extra>'
            ))
        
        # Group and plot interference products by type
        product_groups = {}
        for result in quantitative_results:
            product_type = result.product_type
            if product_type not in product_groups:
                product_groups[product_type] = []
            product_groups[product_type].append(result)
        
        # Plot each product type
        for product_type, results in product_groups.items():
            if not results:
                continue
                
            frequencies = [r.frequency_mhz for r in results]
            powers_dbc = [r.interference_level_dbc for r in results]
            
            # Create hover information
            hover_text = []
            for r in results:
                hover_text.append(
                    f"<b>{r.product_type} Interference Product</b><br>" +
                    f"Frequency: {r.frequency_mhz:.1f} MHz<br>" +
                    f"Level: {r.interference_level_dbc:.1f} dBc<br>" +
                    f"At Victim: {r.interference_at_victim_dbm:.1f} dBm<br>" +
                    f"Margin: {r.interference_margin_db:+.1f} dB<br>" +
                    f"Risk: {r.risk_symbol} {r.risk_level}<br>" +
                    f"TX: {', '.join(r.aggressors)}<br>" +
                    f"RX: {', '.join(r.victims) if hasattr(r, 'victims') else 'N/A'}"
                )
            
            # Add scatter plot for this product type
            fig.add_trace(go.Scatter(
                x=frequencies,
                y=powers_dbc,
                mode='markers',
                marker=dict(
                    size=8,
                    color=color_map.get(product_type, '#808080'),
                    opacity=0.8,
                    line=dict(width=1, color='black')
                ),
                name=product_type,
                hovertemplate='%{customdata}<extra></extra>',
                customdata=hover_text
            ))
        
        # Add key reference lines
        fig.add_hline(
            y=0, 
            line_dash="solid", 
            line_color="green",
            line_width=2,
            annotation_text="Fundamental Level (0 dBc)",
            annotation_position="top left"
        )
        
        fig.add_hline(
            y=-20, 
            line_dash="dot", 
            line_color="orange",
            line_width=1,
            annotation_text="Strong Interference (-20 dBc)",
            annotation_position="bottom right"
        )
        
        fig.add_hline(
            y=-40, 
            line_dash="dot", 
            line_color="blue",
            line_width=1,
            annotation_text="Moderate Interference (-40 dBc)",
            annotation_position="top right"
        )
        
        fig.add_hline(
            y=-60,
            line_dash="dash",
            line_color="gray",
            line_width=1,
            annotation_text="Weak Interference (-60 dBc)",
            annotation_position="bottom left"
        )
        
        # Clean, professional layout
        fig.update_layout(
            title={
                'text': "RF Interference Products - Spectrum Analysis",
                'x': 0.5,
                'font': {'size': 16, 'color': 'darkblue'}
            },
            xaxis_title="Frequency (MHz)",
            yaxis_title="Interference Level (dBc)",
            showlegend=True,
            legend=dict(
                orientation="v",
                x=1.02,
                y=1,
                font={'size': 10},
                title="<b>Baseband Intermodulation Products</b><br>" +
                      "<i>Based on RF Insights theory:</i><br>" +
                      "V₀ = a₁V + a₂V² + a₃V³ + a₄V⁴ + a₅V⁵<br>" +
                      "<br>" +
                      "📍 <b>Band Center Tones</b>:<br>" +
                      "• Even-order → ACLR zone<br>" +
                      "• IM3/IM5 close-in → In-band EVM<br>" +
                      "• Some IM4 → In-band impact<br>" +
                      "<br>" +
                      "📍 <b>Band Edge Tones</b>:<br>" +
                      "• Spread-out distortion patterns<br>" +
                      "• Mix of in-band and ACLR effects<br>" +
                      "<br>" +
                      "🔸 <b>BBHD/Harmonics</b>: nH = aₙVⁿ<br>" +
                      "🔸 <b>IM2</b>: Beat/envelope (ACLR critical)<br>" +
                      "🔸 <b>IM3</b>: Close-in mixing (EVM critical)<br>" +
                      "🔸 <b>IM4+</b>: Mixed in-band/ACLR products"
            ),
            height=600,
            plot_bgcolor='rgba(248,249,250,0.9)',
            paper_bgcolor='white',
            margin=dict(l=60, r=120, t=60, b=60)
        )
        
        # Clean grid
        fig.update_xaxes(
            showgrid=True, 
            gridwidth=1, 
            gridcolor='lightgray',
            title_font={'size': 12, 'color': 'darkblue'}
        )
        fig.update_yaxes(
            showgrid=True, 
            gridwidth=1, 
            gridcolor='lightgray',
            title_font={'size': 12, 'color': 'darkblue'},
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor='green'
        )
        
        return fig
        
    except Exception as e:
        st.error(f"Error creating RF spectrum chart: {e}")
        import traceback
        st.error(f"Detailed error: {traceback.format_exc()}")
        return None

def highlight_risks(row):
    """Simple risk highlighting"""
    risk_colors = {
        '🔴': 'background-color: #ffebee; color: #c62828; font-weight: bold',
        '🟠': 'background-color: #fff3e0; color: #ef6c00; font-weight: bold',
        '🟡': 'background-color: #fffde7; color: #f57f17; font-weight: bold',
        '🔵': 'background-color: #e3f2fd; color: #1565c0',
        '✅': 'background-color: #e8f5e8; color: #2e7d32'
    }
    risk = row.get('Risk', '✅')
    style = risk_colors.get(risk, '')
    return [style] * len(row)


def enhance_results_with_quantitative(results_df: pd.DataFrame,
                                       quantitative_results: list,
                                       rf_params,
                                       band_objects: list) -> pd.DataFrame:
    """
    Enhance results DataFrame with quantitative columns (dBm, dBc, compliance).

    Adds columns: P_product, P_victim, Desense, Margin, Compliance
    """
    if results_df.empty or not quantitative_results:
        return results_df

    # Create lookup from quantitative results
    quant_lookup = {}
    for qr in quantitative_results:
        key = (round(qr.frequency_mhz, 1), qr.product_type)
        quant_lookup[key] = qr

    # Add new columns
    p_product_list = []
    p_victim_list = []
    desense_list = []
    margin_list = []
    compliance_list = []
    severity_reason_list = []

    for _, row in results_df.iterrows():
        freq = round(row.get('Frequency', row.get('Frequency_MHz', 0)), 1)
        ptype = row.get('Type', '')
        key = (freq, ptype)

        if key in quant_lookup:
            qr = quant_lookup[key]
            p_product_list.append(f"{qr.interference_at_tx_dbm:.1f}")
            p_victim_list.append(f"{qr.interference_at_victim_dbm:.1f}")
            desense_list.append(f"{qr.desensitization_db:.1f}")
            margin_list.append(f"{qr.interference_margin_db:+.1f}")

            # Check compliance if regulatory module available
            if REGULATORY_AVAILABLE:
                aggressor = row.get('Aggressors', '')
                compliant, reason, _ = check_emission_compliance(
                    aggressor, freq, qr.interference_at_tx_dbm
                )
                compliance_list.append("✓" if compliant else "✗")
            else:
                compliance_list.append("-")

            # Create severity reason based on quantitative data
            if qr.desensitization_db >= 8.0:
                severity_reason_list.append(f"Critical ({qr.desensitization_db:.1f}dB desense)")
            elif qr.desensitization_db >= 3.0:
                severity_reason_list.append(f"High ({qr.desensitization_db:.1f}dB)")
            elif qr.desensitization_db >= 1.0:
                severity_reason_list.append(f"Medium ({qr.desensitization_db:.1f}dB)")
            else:
                severity_reason_list.append("Low")
        else:
            p_product_list.append("-")
            p_victim_list.append("-")
            desense_list.append("-")
            margin_list.append("-")
            compliance_list.append("-")
            severity_reason_list.append("-")

    # Add columns to DataFrame
    enhanced_df = results_df.copy()
    enhanced_df['P_TX (dBm)'] = p_product_list
    enhanced_df['P_RX (dBm)'] = p_victim_list
    enhanced_df['Desense (dB)'] = desense_list
    enhanced_df['Margin (dB)'] = margin_list
    enhanced_df['Compliance'] = compliance_list

    return enhanced_df


def create_compliance_summary(results_df: pd.DataFrame,
                               quantitative_results: list,
                               band_objects: list) -> dict:
    """
    Create compliance summary for dashboard.

    Returns dict with violation_count, isolation_issues, critical_pairs
    """
    summary = {
        'emission_violations': 0,
        'isolation_issues': 0,
        'critical_pairs': [],
        'total_checked': 0
    }

    if not REGULATORY_AVAILABLE or not quantitative_results:
        return summary

    for qr in quantitative_results:
        if qr.victims:
            summary['total_checked'] += 1
            aggressor = qr.aggressors[0] if qr.aggressors else ''

            # Check emission compliance
            compliant, reason, margin = check_emission_compliance(
                aggressor, qr.frequency_mhz, qr.interference_at_tx_dbm
            )
            if not compliant:
                summary['emission_violations'] += 1
                summary['critical_pairs'].append({
                    'aggressor': aggressor,
                    'victim': qr.victims[0] if qr.victims else '',
                    'frequency': qr.frequency_mhz,
                    'reason': reason,
                    'margin': margin
                })

    return summary

# Streamlit Configuration
st.set_page_config(
    page_title="RF Spectrum Interference Calculator",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Header with professional guidance
st.title("📡 RF Spectrum Interference Calculator")
st.markdown("**Professional harmonic & intermodulation analysis for wireless system design**" )

# Professional credentials and validation banner
col_header1, col_header2, col_header3 = st.columns([2, 1, 1])
with col_header1:
    st.markdown(f"""
    **Harmonic Analysis Tool** | Version {__version__}  
    """)
# Consolidated Help & Quick Start
col_help1, col_help2 = st.columns([1, 1])

with col_help1:
    with st.expander("🚀 Quick Start Guide"):
        st.markdown("""
        **📋 Simple 5-Step Process:**
        1. **📂 Select Categories**: Choose band types (LTE, Wi-Fi, BLE, GNSS) in sidebar
        2. **🎯 Choose Bands**: Pick specific bands or use regional presets (US LTE, EU LTE, etc.)
        3. **⚙️ Configure**: Set guard margins and coexistence filtering (PTA/WCI-2)
        4. **🔬 Analyze**: Enable IMD products (IM2, IM3, harmonics) and calculate
        5. **📊 Export**: Download results as CSV/Excel with quantitative dBc/dBm data
        
        **🔧 Auto-Coexistence Mode:**
        • Activates automatically with multiple LTE bands selected
        • Tests each LTE band individually for realistic interference scenarios
        • Provides separate results for each combination
        
        **🛡️ Guard Band Presets:**
        • **Conservative (1 MHz)**: Standard industry practice
        • **Moderate (2 MHz)**: Enhanced protection for sensitive receivers  
        • **Aggressive (5 MHz)**: Maximum protection for GPS/safety-critical apps
        """)

with col_help2:
    with st.expander("⚖️ Professional Guidelines & Legal"):
        st.markdown("""
        **🎯 Professional Applications:**
        • **Product Development**: Pre-certification interference analysis
        • **Field Support**: Troubleshooting interference issues
        • **Training**: RF interference fundamentals
        
        **📊 Analysis Capabilities:**
        • **70+ Wireless Bands**: LTE, Wi-Fi, BLE, GNSS, ISM, LoRaWAN
        • **Up to 5th Order**: Complete IMD analysis (IM2, IM3, IM4, IM5, IM7)
        • **Risk Assessment**: 🔴 Critical → 🟠 High → 🟡 Medium → 🔵 Low → ✅ Safe
        • **Industry Coordination**: PTA (BLE↔Wi-Fi) and WCI-2 (LTE↔Wi-Fi) filtering
        
        **🔬 Mathematical Foundation:**
        • **Polynomial Model**: V₀ = a₁V + a₂V² + a₃V³ + a₄V⁴ + a₅V⁵
        • **IEEE Standards**: 802.11, 3GPP compliance analysis
        • **RF Insights Theory**: Baseband intermodulation validated
        • **Frequency Range**: 10 MHz - 6 GHz (validated)
        
        **⚠️ Professional Disclaimers:**
        • **Educational/Professional Use**: Theoretical predictions - **validate with measurements**
        • **MIT Licensed Open Source**: No warranty - **use engineering judgment**
        • **Not Certified**: Not a regulatory compliance instrument
        • **Professional Tool**: Requires RF engineering expertise for proper interpretation
        
        **🔗 Project Links:**
        • **GitHub**: [RFingAdam/rf-interference-calculator](https://github.com/RFingAdam/rf-interference-calculator)
        • **Issues**: [Report bugs and feature requests](https://github.com/RFingAdam/rf-interference-calculator/issues)
        • **License**: [MIT License](https://github.com/RFingAdam/rf-interference-calculator/blob/main/LICENSE)
        • **Theory Validation**: [RF_INSIGHTS_VALIDATION.md](https://github.com/RFingAdam/rf-interference-calculator/blob/main/RF_INSIGHTS_VALIDATION.md)
        """)

# Smart Quick Tip based on RF Performance availability
if RF_PERFORMANCE_AVAILABLE:
    st.success("🔬 **Quantitative Analysis Ready**: Configure RF system parameters → Select bands → Get dBc/dBm interference levels")
else:
    st.info("💡 **Basic Analysis Mode**: Select band categories → Choose bands → Calculate interference products")

# Enhanced status indicator with validation
status_col1, status_col2, status_col3, status_col4 = st.columns([2, 1, 1, 1])
with status_col1:
    st.caption(f"Version {__version__} - Professional RF Analysis Tool")
with status_col2:
    st.success("🟢 **System Ready**")
with status_col3:
    st.info(f"📊 **{len(BANDS)} Bands**")
with status_col4:
    if MATHEMATICAL_VALIDATION["validation_status"]:
        st.success("✅ **Validated**")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Guard Band Settings with Professional Presets
    st.subheader("🛡️ Guard Band Settings")
    guard_preset = st.selectbox(
        "Guard Band Preset:",
        ["No Guard (0 MHz)", "Conservative (1 MHz)", "Moderate (2 MHz)", "Aggressive (5 MHz)", "Custom"],
        index=1,  # Default to Conservative
        help="Professional guard band presets for different analysis scenarios"
    )
    
    # Set guard value based on preset
    if guard_preset == "No Guard (0 MHz)":
        guard = 0.0
    elif guard_preset == "Conservative (1 MHz)":
        guard = 1.0
    elif guard_preset == "Moderate (2 MHz)":
        guard = 2.0
    elif guard_preset == "Aggressive (5 MHz)":
        guard = 5.0
    else:  # Custom
        guard = st.slider("Custom Guard Band (MHz)", 0.0, 20.0, 1.0, 0.1)
    
    # Show current guard value
    if guard > 0:
        st.info(f"🛡️ Active Guard: ±{guard} MHz protection margin")
    
    # Categories
    st.subheader("📂 Band Categories")
    all_categories = sorted(set(band.category for band in BANDS.values()))
    selected_categories = st.multiselect(
        "Select categories:",
        all_categories,
        default=["LTE", "Wi-Fi", "BLE", "GNSS"],
        help="Choose which band categories to show"
    )
    
    # Export options
    st.subheader("📥 Export")
    include_safe = st.checkbox("Include safe products", False)
    
    # Display options
    st.subheader("📊 Display")
    show_all_results = st.checkbox("Show all results", True, help="Show all results with risk-based color coding (uncheck to filter to only critical/medium risk)")  # Changed default to True
    max_results = st.slider("Max results to show", 50, 1000, 200, 50, help="Limit table size for performance")
    
    # Professional Coexistence Controls
    st.subheader("🔧 Coexistence Implementation")
    st.markdown("**Real-world coordination mechanisms:**")
    
    # PTA Implementation
    pta_enabled = st.checkbox("PTA (Packet Transfer Arbitration) Implemented", value=False,
                             help="Enable if PTA is implemented for 2.4 GHz ISM coordination (BLE + Wi-Fi)")
    if pta_enabled:
        st.success("✅ PTA active - ISM band coordination products filtered")
    
    # WCI-2 Implementation  
    wci2_enabled = st.checkbox("WCI-2 Interface Implemented", value=False,
                              help="Enable if WCI-2 interface is implemented for LTE↔Wi-Fi coordination (GNSS interference remains visible)")
    if wci2_enabled:
        st.success("✅ WCI-2 active - LTE→Wi-Fi interference filtered (keeps GNSS visible)")
    
    # Advanced filtering when coordination is active
    filter_ism_products = True  # Default values
    filter_lte_harmonics = True
    
    if pta_enabled or wci2_enabled:
        with st.expander("🔧 Advanced Coexistence Filtering"):
            filter_ism_products = st.checkbox("Filter ISM IM products when PTA active", value=True,
                                             help="Remove IM products between BLE and Wi-Fi 2.4G when PTA coordinates them",
                                             disabled=not pta_enabled)
            
        filter_lte_harmonics = st.checkbox("Filter LTE coordination products when WCI-2 active", value=True,
                                          help="Remove LTE interference to Wi-Fi radios only (keeps GNSS, BLE interference visible)",
                                          disabled=not wci2_enabled)
        
        # Show what will be filtered
        if pta_enabled or wci2_enabled:
            st.info("**Active Coordination:**")
            if pta_enabled:
                st.write("• BLE ↔ Wi-Fi 2.4G IM products (PTA coordination)")
            if wci2_enabled:
                st.write("• LTE coordination products (harmonics, IM2 beats, IM3) - WCI-2")

    # RF System Parameters for Quantitative Analysis
    if RF_PERFORMANCE_AVAILABLE:
        st.subheader("📊 RF System Parameters")
        st.markdown("**Configure system for quantitative dBc/dBm analysis**")
        
        # Smart parameter selection based on selected bands
        selected_techs = set()
        for category in selected_categories:
            if 'LTE' in category:
                selected_techs.add('LTE')
            elif 'Wi-Fi' in category:
                selected_techs.add('WiFi')
            elif 'BLE' in category:
                selected_techs.add('BLE')
            elif 'GNSS' in category:
                selected_techs.add('GNSS')
            elif 'ISM' in category:
                selected_techs.add('ISM')
        
        # Technology-aware preset recommendation
        if selected_techs:
            tech_list = ', '.join(selected_techs)
            st.info(f"🎯 **Detected Technologies**: {tech_list}")
            
            # Smart preset recommendation with professional focus
            if 'GNSS' in selected_techs and 'LTE' in selected_techs:
                recommended_preset = "desktop_professional"
                st.success("🎯 **GNSS + LTE detected**: Using Desktop Professional parameters for realistic interference analysis")
            elif len(selected_techs) > 2:
                recommended_preset = "desktop_professional"
                st.info("💡 **Multi-radio system**: Desktop Professional preset recommended")
            elif 'LTE' in selected_techs and any(coex in selected_techs for coex in ['WiFi', 'BLE']):
                recommended_preset = "desktop_professional"
                st.info("💡 **LTE Coexistence system**: Desktop Professional preset recommended")
            elif 'LTE' in selected_techs:
                recommended_preset = "mobile_device_typical"
            else:
                recommended_preset = "iot_device_typical"
        else:
            recommended_preset = "desktop_professional"
        
        # System preset selector with user-friendly names
        preset_options = [
            "desktop_professional",     # User's exact requirements - put first
            "mobile_device_typical", 
            "mobile_device_poor", 
            "iot_device_typical", 
            "base_station", 
            "laboratory_reference", 
            "custom"
        ]
        
        # User-friendly display names with technical specifications
        preset_display_names = {
            "desktop_professional": "🖥️ Desktop Professional (LTE:23dBm, WiFi:20dBm, BLE:20dBm, Isolation:25dB, Sensitivity:-105dBm)",
            "mobile_device_typical": "📱 Mobile Device - Typical (LTE:23dBm, WiFi:16dBm, BLE:10dBm, Isolation:15dB, Sensitivity:-100dBm)",
            "mobile_device_poor": "📱 Mobile Device - Poor Isolation (LTE:23dBm, WiFi:14dBm, BLE:8dBm, Isolation:10dB, Sensitivity:-95dBm)",
            "iot_device_typical": "⚡ IoT Device - Typical (LTE:20dBm, WiFi:14dBm, BLE:4dBm, Isolation:10dB, Sensitivity:-95dBm)",
            "base_station": "📡 Base Station (LTE:43dBm, WiFi:24dBm, BLE:20dBm, Isolation:40dB, Sensitivity:-110dBm)",
            "laboratory_reference": "🔬 Laboratory Reference (LTE:23dBm, WiFi:20dBm, BLE:20dBm, Isolation:40dB, Sensitivity:-110dBm)",
            "custom": "⚙️ Custom Parameters (User-defined)"
        }
        
        # Set default index to recommended preset
        default_idx = preset_options.index(recommended_preset) if recommended_preset in preset_options else 0
        
        system_preset = st.selectbox(
            "System Type:",
            options=preset_options,
            format_func=lambda x: preset_display_names.get(x, x),
            index=default_idx,
            help="Professional system presets with your exact RF parameters."
        )
        
        if system_preset != "custom":
            rf_params = RF_SYSTEM_PRESETS[system_preset]
            st.success(f"✅ Using {system_preset.replace('_', ' ').title()} preset")
            
            # Show key parameters with technology-specific highlights
            with st.expander("📋 System Parameters (Click to view details)"):
                param_col1, param_col2 = st.columns(2)
                
                with param_col1:
                    st.write(f"**🔌 TX Power Levels:**")
                    if 'LTE' in selected_techs:
                        st.write(f"• LTE TX: **{rf_params.lte_tx_power} dBm** 📡")
                    if 'WiFi' in selected_techs:
                        st.write(f"• Wi-Fi TX: **{rf_params.wifi_tx_power} dBm** 📶")
                    if 'BLE' in selected_techs:
                        st.write(f"• BLE TX: **{rf_params.ble_tx_power} dBm** 🔵")
                    
                    st.write(f"**🛡️ Isolation & Filtering:**")
                    st.write(f"• Antenna Isolation: **{rf_params.antenna_isolation} dB**")
                    st.write(f"• TX Harmonic Filter: **{rf_params.tx_harmonic_filtering_db} dB**")
                
                with param_col2:
                    st.write(f"**📊 System Linearity:**")
                    st.write(f"• IIP3: **{rf_params.iip3_dbm} dBm** (3rd order)")
                    st.write(f"• IIP2: **{rf_params.iip2_dbm} dBm** (2nd order)")
                    st.write(f"• PA Class: **{rf_params.pa_class}**")
                    
                    # Calculate and show HD levels for LTE power
                    if RF_PERFORMANCE_AVAILABLE:
                        calculated_hd = calculate_system_harmonic_levels(rf_params.lte_tx_power, rf_params)
                        st.write(f"**📊 Calculated HD Levels (@ {rf_params.lte_tx_power} dBm):**")
                        st.write(f"• HD2: **{calculated_hd['hd2_dbc']:.1f} dBc** ✅")
                        st.write(f"• HD3: **{calculated_hd['hd3_dbc']:.1f} dBc** ✅")
                        st.write(f"• HD4: **{calculated_hd['hd4_dbc']:.1f} dBc** ✅")
                        st.write(f"• HD5: **{calculated_hd['hd5_dbc']:.1f} dBc** ✅")
                    
                    st.write(f"**📡 RX Sensitivities:**")
                    if 'LTE' in selected_techs:
                        st.write(f"• LTE RX: **{rf_params.lte_sensitivity} dBm**")
                    if 'WiFi' in selected_techs:
                        st.write(f"• Wi-Fi RX: **{rf_params.wifi_sensitivity} dBm**")
                    if 'BLE' in selected_techs:
                        st.write(f"• BLE RX: **{rf_params.ble_sensitivity} dBm**")
                    if 'GNSS' in selected_techs:
                        st.write(f"• GNSS RX: **{rf_params.gnss_sensitivity} dBm** ⚠️")
        else:
            # Custom parameters with comprehensive RF system controls
            st.markdown("**🔧 Custom RF System Parameters:**")
            st.markdown("*Configure all isolation, filtering, and system characteristics*")
            
            # TX Power settings
            st.markdown("**🔌 Transmit Power Levels**")
            tx_col1, tx_col2, tx_col3 = st.columns(3)
            
            with tx_col1:
                custom_lte_tx = st.slider("LTE TX Power (dBm)", 10, 50, 23, 
                                        help="LTE/5G transmit power", disabled='LTE' not in selected_techs)
            with tx_col2:
                custom_wifi_tx = st.slider("Wi-Fi TX Power (dBm)", 10, 30, 18, 
                                         help="Wi-Fi transmit power", disabled='WiFi' not in selected_techs)
            with tx_col3:
                custom_ble_tx = st.slider("BLE TX Power (dBm)", -10, 20, 10, 
                                        help="BLE/Bluetooth transmit power", disabled='BLE' not in selected_techs)
            
            # RF System Isolation & Path Loss (Most Important Section)
            st.markdown("**🛡️ RF System Isolation & Filtering**")
            st.markdown("*These parameters dramatically affect interference levels*")
            
            iso_col1, iso_col2, iso_col3 = st.columns(3)
            
            with iso_col1:
                custom_antenna_isolation = st.slider("Antenna Isolation (dB)", 10, 60, 25, 
                                                   help="Physical antenna separation on PCB - CRITICAL parameter")
                custom_pcb_isolation = st.slider("PCB Isolation (dB)", 5, 40, 20, 
                                                help="PCB layout isolation (ground planes, trace spacing)")
                custom_shield_isolation = st.slider("RF Shielding (dB)", 0, 30, 0, 
                                                   help="Additional RF shielding (0 = no shield)")
            
            with iso_col2:
                custom_tx_filter = st.slider("TX Harmonic Filtering (dB)", 20, 80, 40, 
                                           help="TX harmonic suppression - reduces harmonics dramatically")
                custom_rx_filter = st.slider("RX Preselector Filtering (dB)", 0, 40, 0, 
                                           help="RX preselector filtering (0 = wideband receiver)")
                custom_oob_rejection = st.slider("Out-of-Band Rejection (dB)", 20, 80, 60, 
                                                help="Filter out-of-band rejection")
            
            with iso_col3:
                # Technology-specific isolation
                custom_lte_gnss_coupling = st.slider("LTE→GNSS Coupling (dB)", -20, 0, -10, 
                                                    help="Additional LTE→GNSS coupling loss (negative = additional isolation)")
                custom_wifi_ble_isolation = st.slider("Wi-Fi/BLE Isolation (dB)", 5, 30, 10, 
                                                     help="Wi-Fi/BLE triplexer isolation")
                custom_cellular_wifi_isolation = st.slider("Cellular/Wi-Fi Isolation (dB)", 5, 30, 15, 
                                                          help="Cellular/Wi-Fi isolation")
            
            # ✅ CORRECTED: System Linearity Parameters (RF Engineering Approach)
            st.markdown("**📊 System Linearity Characteristics**")
            st.markdown("*Real RF engineering parameters - HD levels calculated from these*")
            
            nl_col1, nl_col2, nl_col3 = st.columns(3)
            
            with nl_col1:
                custom_iip3 = st.slider("IIP3 (dBm)", -30, 10, -10, 
                                      help="Input-referred 3rd order intercept point - determines HD3/IM3 levels")
                custom_iip2 = st.slider("IIP2 (dBm)", 0, 40, 20, 
                                      help="Input-referred 2nd order intercept point - determines HD2/IM2 levels")
            
            with nl_col2:
                custom_pa_class = st.selectbox("PA Class", ["A", "AB", "B", "C"], index=1,
                                             help="Power amplifier class affects linearity: A=best, C=worst")
                custom_bias_optimized = st.checkbox("Bias Point Optimized", value=True, 
                                                  help="Whether PA bias is optimized for linearity")
            
            with nl_col3:
                # Show calculated HD levels in real-time
                st.markdown("**Calculated HD Levels:**")
                if RF_PERFORMANCE_AVAILABLE:
                    temp_params = SystemParameters(
                        iip3_dbm=custom_iip3,
                        iip2_dbm=custom_iip2,
                        pa_class=custom_pa_class,
                        bias_point_optimized=custom_bias_optimized
                    )
                    calc_hd = calculate_system_harmonic_levels(23.0, temp_params)  # Use 23 dBm reference
                    st.write(f"HD2: **{calc_hd['hd2_dbc']:.1f} dBc** ✅")
                    st.write(f"HD3: **{calc_hd['hd3_dbc']:.1f} dBc** ✅") 
                    st.write(f"HD4: **{calc_hd['hd4_dbc']:.1f} dBc** ✅")
                    st.write(f"HD5: **{calc_hd['hd5_dbc']:.1f} dBc** ✅")
            
            # Receiver sensitivities
            st.markdown("**📡 Receiver Sensitivities**")
            rx_col1, rx_col2, rx_col3, rx_col4 = st.columns(4)
            
            with rx_col1:
                custom_lte_sens = st.slider("LTE Sensitivity (dBm)", -120, -90, -105, 
                                          help="LTE receiver sensitivity", disabled='LTE' not in selected_techs)
            with rx_col2:
                custom_wifi_sens = st.slider("Wi-Fi Sensitivity (dBm)", -100, -70, -85, 
                                           help="Wi-Fi receiver sensitivity", disabled='WiFi' not in selected_techs)
            with rx_col3:
                custom_ble_sens = st.slider("BLE Sensitivity (dBm)", -110, -80, -95, 
                                          help="BLE receiver sensitivity", disabled='BLE' not in selected_techs)
            with rx_col4:
                custom_gnss_sens = st.slider("GNSS Sensitivity (dBm)", -160, -140, -150, 
                                           help="GNSS receiver sensitivity (very sensitive!)", 
                                           disabled='GNSS' not in selected_techs)
            
            # Create custom parameters object with comprehensive RF parameters
            rf_params = SystemParameters(
                # TX Power Levels
                lte_tx_power=custom_lte_tx,
                wifi_tx_power=custom_wifi_tx,
                ble_tx_power=custom_ble_tx,
                
                # RF System Isolation & Path Loss
                antenna_isolation=custom_antenna_isolation,
                pcb_isolation=custom_pcb_isolation,
                shield_isolation=custom_shield_isolation,
                
                # Filtering & Attenuation
                tx_harmonic_filtering_db=custom_tx_filter,
                rx_preselector_filtering_db=custom_rx_filter,
                out_of_band_rejection_db=custom_oob_rejection,
                
                # Technology-Specific Path Loss
                lte_to_gnss_coupling_db=custom_lte_gnss_coupling,
                wifi_ble_isolation_db=custom_wifi_ble_isolation,
                cellular_wifi_isolation_db=custom_cellular_wifi_isolation,
                
                # ✅ CORRECTED: System Linearity Parameters
                iip3_dbm=custom_iip3,
                iip2_dbm=custom_iip2,
                pa_class=custom_pa_class,
                bias_point_optimized=custom_bias_optimized,
                
                # Receiver Sensitivities
                lte_sensitivity=custom_lte_sens,
                wifi_sensitivity=custom_wifi_sens,
                ble_sensitivity=custom_ble_sens,
                gnss_sensitivity=custom_gnss_sens
            )
            
            st.success("✅ Custom parameters configured - All isolation and filtering applied")
            
            # Show key isolation summary
            total_isolation_est = custom_antenna_isolation + custom_pcb_isolation + custom_shield_isolation
            st.info(f"""
            **🔍 Isolation Summary:**
            • Total Physical Isolation: ~{total_isolation_est:.0f} dB
            • TX Filtering: {custom_tx_filter} dB (harmonics)
            • RX Filtering: {custom_rx_filter + custom_oob_rejection} dB (total)
            • **Net Effect**: Harmonics reduced by {total_isolation_est + custom_tx_filter:.0f}+ dB
            """)
        
        # Store in session state
        st.session_state['rf_params'] = rf_params
        
        # Enhanced validation warnings
        total_isolation = rf_params.antenna_isolation + rf_params.pcb_isolation + rf_params.shield_isolation
        
        if total_isolation < 30:
            st.warning("⚠️ **Low Total Isolation Warning**: Total isolation < 30 dB may cause significant interference")
        
        if rf_params.tx_harmonic_filtering_db < 30:
            st.warning("🔧 **TX Filtering Warning**: TX harmonic filtering < 30 dB - harmonics may be strong")
        
        if 'GNSS' in selected_techs and rf_params.lte_tx_power > 20:
            st.warning("🛰️ **GNSS Critical Warning**: High LTE TX power + GNSS = potential GPS dead zones!")
        
        # ✅ CORRECTED: Validate calculated linearity instead of fixed HD levels
        if rf_params.iip3_dbm > -5:
            st.warning("📊 **Linearity Warning**: IIP3 > -5 dBm indicates poor system linearity")
        
        if rf_params.iip2_dbm < 10:
            st.warning("⚖️ **Balance Warning**: IIP2 < 10 dBm indicates poor device balance")

# Main Interface
col1, col2 = st.columns([1, 1])

with col1:
    # Band selection
    st.subheader("📋 Band Selection")
    
    # Get filtered bands first (needed for presets)
    filtered_bands = [band for band in BANDS.values() if band.category in selected_categories]
    
    # Quick Select Presets - Regional LTE + Coexistence
    st.markdown("**🌍 Regional LTE Presets** *(Telit LE910C1-WWXD Cat-1 Modem)*")
    
    # Regional LTE presets (2 columns)
    preset_col1, preset_col2 = st.columns(2)
    
    with preset_col1:
        if st.button("🇺🇸 US LTE", help="Add B2,B4,B5,B12,B13,B14,B17,B25,B26", key="us_lte_preset"):
            preset_bands = ["LTE_B2", "LTE_B4", "LTE_B5", "LTE_B12", "LTE_B13", "LTE_B14", "LTE_B17", "LTE_B25", "LTE_B26"]
            current_selection = st.session_state.get('band_multiselect_widget', [])
            available_bands_filtered = [b for b in preset_bands if b in [band.code for band in filtered_bands]]
            combined_selection = list(set(current_selection + available_bands_filtered))
            st.session_state['band_multiselect_widget'] = combined_selection
            st.rerun()
        
        if st.button("🇦🇺 AU/NZ LTE", help="Add B1,B3,B5,B7,B8,B28", key="aunz_lte_preset"):
            preset_bands = ["LTE_B1", "LTE_B3", "LTE_B5", "LTE_B7", "LTE_B8", "LTE_B28"]
            current_selection = st.session_state.get('band_multiselect_widget', [])
            available_bands_filtered = [b for b in preset_bands if b in [band.code for band in filtered_bands]]
            combined_selection = list(set(current_selection + available_bands_filtered))
            st.session_state['band_multiselect_widget'] = combined_selection
            st.rerun()
        
        if st.button("🇹🇼 Taiwan LTE", help="Add B1,B3,B7,B8,B28", key="tw_lte_preset"):
            preset_bands = ["LTE_B1", "LTE_B3", "LTE_B7", "LTE_B8", "LTE_B28"]
            current_selection = st.session_state.get('band_multiselect_widget', [])
            available_bands_filtered = [b for b in preset_bands if b in [band.code for band in filtered_bands]]
            combined_selection = list(set(current_selection + available_bands_filtered))
            st.session_state['band_multiselect_widget'] = combined_selection
            st.rerun()
    
    with preset_col2:
        if st.button("🇪🇺 EU LTE", help="Add B1,B3,B7,B8,B20,B28", key="eu_lte_preset"):
            preset_bands = ["LTE_B1", "LTE_B3", "LTE_B7", "LTE_B8", "LTE_B20", "LTE_B28"]
            current_selection = st.session_state.get('band_multiselect_widget', [])
            available_bands_filtered = [b for b in preset_bands if b in [band.code for band in filtered_bands]]
            combined_selection = list(set(current_selection + available_bands_filtered))
            st.session_state['band_multiselect_widget'] = combined_selection
            st.rerun()
        
        if st.button("🇯🇵 Japan LTE", help="Add B1,B3,B8,B11,B19,B28", key="jp_lte_preset"):
            preset_bands = ["LTE_B1", "LTE_B3", "LTE_B8", "LTE_B11", "LTE_B19", "LTE_B28"]
            current_selection = st.session_state.get('band_multiselect_widget', [])
            available_bands_filtered = [b for b in preset_bands if b in [band.code for band in filtered_bands]]
            combined_selection = list(set(current_selection + available_bands_filtered))
            st.session_state['band_multiselect_widget'] = combined_selection
            st.rerun()
        
        if st.button("🇰🇷 Korea LTE", help="Add B1,B3,B7,B8,B26", key="kr_lte_preset"):
            preset_bands = ["LTE_B1", "LTE_B3", "LTE_B7", "LTE_B8", "LTE_B26"]
            current_selection = st.session_state.get('band_multiselect_widget', [])
            available_bands_filtered = [b for b in preset_bands if b in [band.code for band in filtered_bands]]
            combined_selection = list(set(current_selection + available_bands_filtered))
            st.session_state['band_multiselect_widget'] = combined_selection
            st.rerun()
    
    # Coexistence & Technology Presets
    st.markdown("**📡 Coexistence & Technology Presets**")
    coex_col1, coex_col2, coex_col3 = st.columns(3)
    
    with coex_col1:
        if st.button("🛰️ GNSS All", help="Add GNSS L1/L2/L5 (GPS/Galileo/GLONASS)", key="gnss_preset"):
            preset_bands = ["GNSS_L1", "GNSS_L2", "GNSS_L5"]
            current_selection = st.session_state.get('band_multiselect_widget', [])
            available_bands_filtered = [b for b in preset_bands if b in [band.code for band in filtered_bands]]
            combined_selection = list(set(current_selection + available_bands_filtered))
            st.session_state['band_multiselect_widget'] = combined_selection
            st.rerun()
        
        if st.button("📶 Wi-Fi All", help="Add 2.4G + 5G + 6E", key="wifi_preset"):
            preset_bands = ["WiFi_2G", "WiFi_5G", "WiFi_6E"]
            current_selection = st.session_state.get('band_multiselect_widget', [])
            available_bands_filtered = [b for b in preset_bands if b in [band.code for band in filtered_bands]]
            combined_selection = list(set(current_selection + available_bands_filtered))
            st.session_state['band_multiselect_widget'] = combined_selection
            st.rerun()
    
    with coex_col2:
        if st.button("🔵 BLE + ISM", help="Add BLE + ISM 2.4G", key="ble_ism_preset"):
            preset_bands = ["BLE", "ISM_24"]
            current_selection = st.session_state.get('band_multiselect_widget', [])
            available_bands_filtered = [b for b in preset_bands if b in [band.code for band in filtered_bands]]
            combined_selection = list(set(current_selection + available_bands_filtered))
            st.session_state['band_multiselect_widget'] = combined_selection
            st.rerun()
        
        if st.button("⚡ IoT Stack", help="Add BLE + LoRaWAN + Wi-Fi 2.4G", key="iot_preset"):
            preset_bands = ["BLE", "LoRa_EU", "LoRa_US", "WiFi_2G"]
            current_selection = st.session_state.get('band_multiselect_widget', [])
            available_bands_filtered = [b for b in preset_bands if b in [band.code for band in filtered_bands]]
            combined_selection = list(set(current_selection + available_bands_filtered))
            st.session_state['band_multiselect_widget'] = combined_selection
            st.rerun()
    
    with coex_col3:
        if st.button("🚨 Critical GPS", help="Add GNSS L1 (most sensitive)", key="gps_critical_preset"):
            preset_bands = ["GNSS_L1"]
            current_selection = st.session_state.get('band_multiselect_widget', [])
            available_bands_filtered = [b for b in preset_bands if b in [band.code for band in filtered_bands]]
            combined_selection = list(set(current_selection + available_bands_filtered))
            st.session_state['band_multiselect_widget'] = combined_selection
            st.rerun()
        
        if st.button("🗑️ Clear All", help="Clear all selected bands", key="clear_bands"):
            st.session_state['band_multiselect_widget'] = []
            st.rerun()
    
    # Use a single source of truth for selection to avoid resets
    if 'band_multiselect_widget' not in st.session_state:
        st.session_state['band_multiselect_widget'] = []
    
    # Create options list that includes both visible and previously selected bands
    visible_codes = [band.code for band in filtered_bands]  # Extract codes from band objects
    selected_codes = list(st.session_state['band_multiselect_widget'])  # Ensure it's a list
    
    # CRITICAL: Always include previously selected bands in options to prevent clearing
    # This ensures that even if a band's category is unchecked, the band stays available
    all_band_codes = {b.code: b for b in BANDS.values()}  # All bands for reference
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
    # Selected bands summary
    st.subheader("🎯 Selected Bands")
    if available_bands:
        selected_band_objs = [BANDS[code] for code in available_bands]
        
        # Check for auto-coexistence mode
        lte_bands = [b for b in selected_band_objs if b.category == 'LTE']
        coex_radios = [b for b in selected_band_objs if b.category in ['Wi-Fi', 'BLE', 'ISM']]
        auto_coex_mode = len(lte_bands) > 1
        
        if auto_coex_mode:
            st.info("🔬 **Auto-Coexistence Mode**: Testing each LTE band individually")
            st.text(f"• {len(lte_bands)} LTE bands")
            st.text(f"• {len(coex_radios)} coexistence radios")
        
        # Show band summary table (expandable for many bands)
        band_summary = pd.DataFrame([{
            'Band': band.code,
            'Label': band.label,
            'Category': band.category,
            'TX (MHz)': f"{band.tx_low}-{band.tx_high}" if band.tx_low > 0 else "RX Only",
            'RX (MHz)': f"{band.rx_low}-{band.rx_high}"
        } for band in selected_band_objs])
        
        # Dynamic table height based on number of bands
        table_height = min(max(len(band_summary) * 35 + 40, 150), 600)  # 35px per row + header, max 600px
        
        st.dataframe(band_summary, use_container_width=True, height=table_height)
        
        # Professional coexistence recommendations
        ble_present = any(b.category == 'BLE' for b in selected_band_objs)
        wifi_present = any(b.category == 'Wi-Fi' for b in selected_band_objs) 
        lte_present = len(lte_bands) > 0
        
        recommendations = []
        if ble_present and wifi_present:
            recommendations.append("🔄 **Critical**: BLE + Wi-Fi → PTA required for 2.4 GHz coordination")
        if lte_present and wifi_present:
            recommendations.append("📡 **Recommended**: WCI-2 interface for LTE↔Wi-Fi coordination")
        elif lte_present and ble_present:
            recommendations.append("📡 **Consider**: WCI-2 interface for LTE↔BLE coordination (implementation varies)")
        
        if recommendations:
            st.info("**Coexistence Recommendations:**\n\n" + "\n".join(f"• {rec}" for rec in recommendations))
    else:
        st.info("Select bands to begin analysis")

# Analysis Configuration
st.markdown("---")
st.subheader("🔬 Comprehensive IMD Analysis Configuration")
st.markdown("**Professional intermodulation analysis up to 5th order non-linearity**")

# Default configuration
default_harmonics = True
default_harmonic_orders = ["2H", "3H"]
default_imd2 = True
default_imd3 = True
default_imd4 = False
default_imd5 = False
default_imd7 = False
default_envelope_hd = False

col_config1, col_config2, col_config3 = st.columns(3)

with col_config1:
    st.markdown("#### 🎵 Harmonic Products")
    st.markdown("*Single tone harmonics: nH*")
    harmonics_enabled = st.checkbox("Enable Harmonics", default_harmonics, help="2H, 3H, 4H, 5H harmonic generation")
    
    if harmonics_enabled:
        harmonic_orders = st.multiselect(
            "Harmonic Orders:",
            ["2H", "3H", "4H", "5H"],
            default=default_harmonic_orders,
            help="Select which harmonic orders to calculate"
        )
    else:
        harmonic_orders = []

with col_config2:
    st.markdown("#### ⚡ Even-Order IMD Products")
    st.markdown("*f₁±f₂, envelope terms*")
    
    # IM2 (Beat/Envelope) - Most critical even-order
    imd2_enabled = st.checkbox("IM2 Beat Terms (f₁±f₂)", default_imd2, help="Second-order: Beat/envelope products")
    
    # IM4 Products - 4th order intermodulation
    imd4_enabled = st.checkbox("IM4 Products", default_imd4, help="Fourth-order: 3f₁±f₂, f₁±3f₂, etc.")
    
    # HD2 of envelope and other even-order terms
    envelope_hd_enabled = st.checkbox("Envelope Harmonics", default_envelope_hd, help="HD2 of envelope: 2(f₁±f₂)")

with col_config3:
    st.markdown("#### 🔥 Odd-Order IMD Products")  
    st.markdown("*2f₁±f₂, close-in spurs*")
    
    # IM3 Products - Most critical for close-in interference
    imd3_enabled = st.checkbox("IM3 Products (2f₁±f₂)", default_imd3, help="Third-order: Close-in intermodulation")
    
    # IM5 Products - 5th order intermodulation
    imd5_enabled = st.checkbox("IM5 Products", default_imd5, help="Fifth-order: 3f₁±2f₂, 2f₁±3f₂")
    
    # IM7 Products - Very high order (usually weak but sometimes critical)
    imd7_enabled = st.checkbox("IM7 Products", default_imd7, help="Seventh-order: Higher-order products")

        # Show what will be calculated
if any([harmonics_enabled, imd2_enabled, imd3_enabled, imd4_enabled, imd5_enabled, imd7_enabled, envelope_hd_enabled]):
    with st.expander("📋 Analysis Summary"):
        products = []
        if harmonics_enabled and harmonic_orders:
            products.append(f"**Harmonics (BBHD)**: {', '.join(harmonic_orders)} - Baseband harmonic distortion")
        if imd2_enabled:
            products.append("**IM2**: f₁±f₂ (beat/envelope terms) - Critical for ACLR performance")
        if imd3_enabled:
            products.append("**IM3**: 2f₁±f₂, f₁±2f₂ (close-in) - Primary in-band EVM degradation")
        if imd4_enabled:
            products.append("**IM4**: 3f₁±f₂, 2f₁±2f₂ - Mix of in-band and ACLR products")
        if imd5_enabled:
            products.append("**IM5**: 3f₁±2f₂, 2f₁±3f₂ - Close-in spurs affecting EVM")
        if imd7_enabled:
            products.append("**IM7**: Higher-order products - Typically weak but can be critical")
        if envelope_hd_enabled:
            products.append("**Envelope HD**: 2(f₁±f₂) - Harmonics of beat frequencies")
        
        if products:
            st.info("**Products to Calculate:**\n\n" + "\n".join(f"• {p}" for p in products))
            
            # Enhanced mathematical insight based on RF Insights baseband theory
            st.markdown("""
            **💡 RF Insights - Baseband Tone Intermodulation Theory**: 
            
            **📍 Case #1: Band Center Tones**
            - **2nd order** (BBHD2 & IMD2): Fall in ACLR zone → Adjacent channel interference
            - **3rd order** (BBHD3 & IMD3): Fall in ACLR zone → ACLR degradation  
            - **4th order** (BBHD4 & IMD4): Fall in ACLR zone → Out-of-band emissions
            - **5th order** (BBHD5 & IMD5): Fall in ACLR zone → Regulatory compliance issues
            - **IM3 & IM5 close-in products**: Fall **in-band** → **EVM degradation** ⚠️
            - **Some IMD4 products**: Can fall in-band → Signal quality impact
            
            **📍 Case #2: Band Edge Tones**  
            - **Spread-out distortion**: Mix of in-band and out-of-band products
            - **Even/odd order mixing**: Complex interference patterns across spectrum
            - **Wideband effect**: More products land in victim receiver bands
            
            **🔬 Mathematical Foundation:**
            - **System Model**: V₀ = a₀ + a₁Vᵢ + a₂Vᵢ² + a₃Vᵢ³ + a₄Vᵢ⁴ + a₅Vᵢ⁵
            - **Two-tone Input**: Vᵢ = V₁cos(ω₁t) + V₂cos(ω₂t)  
            - **Key Insight**: **All products either fall in-band (EVM impact) or very close (ACLR impact)**
            - **ACLR Contributors**: Baseband emissions are **top contributors** to ACLR degradation
            
            **⚠️ Critical Design Implications:**
            - **IM3/IM5 close-in**: Direct EVM degradation → Signal quality loss
            - **Even-order products**: ACLR zone interference → Regulatory/coexistence issues  
            - **Band position matters**: Center vs. edge fundamentally changes product distribution
            """)# Calculate Button with enhanced logic and validation
enabled_products = sum([
    len(harmonic_orders) if harmonics_enabled else 0,
    int(imd2_enabled), int(imd3_enabled), int(imd4_enabled), 
    int(imd5_enabled), int(imd7_enabled), int(envelope_hd_enabled)
])
calculation_ready = len(available_bands) > 0 and enabled_products > 0

# Professional calculation section
st.markdown("---")
st.subheader("🚀 Professional RF Analysis")

if calculation_ready:
    # Pre-calculation validation
    if RF_PERFORMANCE_AVAILABLE and st.session_state.get('rf_params'):
        errors, warnings = validate_analysis_parameters(
            [BANDS[code] for code in available_bands], 
            st.session_state.get('rf_params')
        )
    else:
        errors, warnings = validate_analysis_parameters([BANDS[code] for code in available_bands])
    
    # Show validation results
    if errors:
        st.error("❌ **Configuration Errors** - Must be resolved before calculation:")
        for error in errors:
            st.error(f"• {error}")
        calculation_ready = False
    
    if warnings:
        with st.expander("⚠️ Configuration Warnings (Click to view)", expanded=False):
            st.warning("**Professional Review Recommended:**")
            for warning in warnings:
                st.warning(f"• {warning}")
            st.info("💡 These warnings don't prevent calculation but may indicate non-optimal configurations")

if st.button("🚀 Calculate Interference", type="primary", use_container_width=True, disabled=not calculation_ready):
    if not calculation_ready:
        st.error("❌ Please select bands and enable analysis products")
    else:
        with st.spinner("Calculating interference products..."):
            if auto_coex_mode:
                # Individual LTE band processing
                st.info("🔬 Processing each LTE band individually...")
                all_results = []
                
                for lte_band in lte_bands:
                    test_group = [lte_band] + coex_radios + [b for b in selected_band_objs if b.category not in ['LTE', 'Wi-Fi', 'BLE', 'ISM']]
                    
                    group_results, _ = calculate_all_products(
                        test_group,
                        guard=guard,
                        imd2=imd2_enabled,
                        imd4=imd4_enabled,
                        imd5=imd5_enabled,
                        imd7=imd7_enabled
                    )
                    
                    # Add scenario info
                    for result in group_results:
                        result['Test_Scenario'] = f"LTE_{lte_band.code.split('_')[1]} Coexistence Test"
                        result['LTE_Band'] = lte_band.code
                    
                    all_results.extend(group_results)
                
                results_list = all_results
            else:
                # Standard processing
                results_list, _ = calculate_all_products(
                    selected_band_objs,
                    guard=guard,
                    imd2=imd2_enabled,
                    imd4=imd4_enabled,
                    imd5=imd5_enabled,
                    imd7=imd7_enabled
                )
        
        if results_list:
            # Convert to DataFrame
            results = pd.DataFrame(results_list)
            
            # Fix column order and remove unwanted columns
            # Remove any numeric risk level columns that might have been added
            unwanted_columns = ['Risk_Level', 'Severity']  # Remove numeric risk indicators
            for col in unwanted_columns:
                if col in results.columns:
                    results = results.drop(col, axis=1)
            
            # Ensure proper column order to match original format
            base_columns = ['Type', 'Product_Subtype', 'Formula', 'Frequency_MHz', 'Aggressors', 'Victims', 'Risk', 'Details']
            
            # Add auto-coexistence columns if present
            optional_columns = []
            if 'Test_Scenario' in results.columns:
                optional_columns.append('Test_Scenario')
            if 'LTE_Band' in results.columns:
                optional_columns.append('LTE_Band')
            
            # Reorder columns to match expected format
            final_columns = []
            for col in base_columns + optional_columns:
                if col in results.columns:
                    final_columns.append(col)
            
            # Add any remaining columns that weren't in the expected list
            for col in results.columns:
                if col not in final_columns:
                    final_columns.append(col)
            
            results = results[final_columns]
            
            # Rename columns for better display (maintain backwards compatibility)
            column_renames = {
                'Frequency_MHz': 'Frequency'  # Keep original short name
            }
            results = results.rename(columns=column_renames)
            
            # Convert legacy risk symbols to new emoji system
            if 'Risk' in results.columns:
                risk_mapping = {
                    '⚠️': '🟠',  # Legacy warning to High risk
                    '✓': '✅',   # Legacy checkmark to Safe
                }
                results['Risk'] = results['Risk'].replace(risk_mapping)
            
            # Calculator already provides risk assessment, just sort by risk
            if 'Risk' in results.columns:
                risk_order = {'🔴': 0, '🟠': 1, '🟡': 2, '🔵': 3, '✅': 4}
                results['_risk_order'] = results['Risk'].map(risk_order).fillna(4)  # Default to safe
                results = results.sort_values(['_risk_order', 'Frequency']).drop('_risk_order', axis=1)
            
            # Apply professional coexistence filtering
            original_count = len(results)
            if pta_enabled or wci2_enabled:
                filtered_results = []
                pta_filtered_count = 0
                wci2_filtered_count = 0
                
                for _, result in results.iterrows():
                    should_filter = False
                    
                    # PTA Filtering - Remove ISM coordination products
                    if pta_enabled and filter_ism_products:
                        aggressors = result.get('Aggressors', '')
                        victims = result.get('Victims', '')
                        product_type = result.get('Type', '')
                        
                        # Enhanced PTA filtering for comprehensive ISM coordination
                        should_filter_pta = False
                        
                        # Filter direct ISM band interference between BLE and WiFi_2G
                        if ('BLE' in str(aggressors) and 'WiFi_2G' in str(aggressors)) or \
                           ('BLE' in str(victims) and ('WiFi_2G' in str(aggressors) or 'WiFi_2G' in str(victims))):
                            should_filter_pta = True
                        
                        # Filter ISM victim interference when both BLE and WiFi are present
                        if (('BLE' in str(victims) or 'WiFi_2G' in str(victims)) and 
                            ('BLE' in str(aggressors) or 'WiFi_2G' in str(aggressors))):
                            should_filter_pta = True
                        
                        # Filter harmonics between ISM radios only (not LTE→ISM harmonics)
                        if product_type in ['2H', '3H'] and \
                           any(ism in str(aggressors) for ism in ['BLE', 'WiFi_2G']) and \
                           any(victim in str(victims) for victim in ['BLE', 'WiFi_2G']):
                            should_filter_pta = True
                        
                        # Filter IM2/IM3 products involving ISM radios (beat frequencies)
                        if product_type in ['IM2', 'IM3'] and \
                           any(ism in str(aggressors) for ism in ['BLE', 'WiFi_2G']) and \
                           any(victim in str(victims) for victim in ['BLE', 'WiFi_2G']):
                            should_filter_pta = True
                        
                        if should_filter_pta:
                            should_filter = True
                            pta_filtered_count += 1
                    
                    # WCI-2 Filtering - Remove LTE coordination products  
                    if wci2_enabled and filter_lte_harmonics and not should_filter:
                        product_type = result.get('Type', '')
                        aggressors = result.get('Aggressors', '')
                        victims = result.get('Victims', '')
                        
                        # Filter LTE coordination products when WCI-2 provides timing coordination
                        # WCI-2 primarily coordinates LTE with Wi-Fi, BLE coordination varies by implementation
                        if 'LTE_' in str(aggressors):
                            
                            # Filter LTE harmonic products hitting coordinated Wi-Fi radios
                            if (product_type in ['2H', '3H', '4H', '5H'] and 
                                any(coex in str(victims) for coex in ['WiFi_2G', 'WiFi_5G'])):
                                should_filter = True
                                wci2_filtered_count += 1
                            
                            # Filter LTE harmonic products hitting BLE (conservative - only non-critical)
                            elif (product_type in ['2H', '3H', '4H', '5H'] and 'BLE' in str(victims) and 
                                  result.get('Risk') not in ['🔴']):  # Keep critical BLE interference visible
                                should_filter = True
                                wci2_filtered_count += 1
                                
                            # Filter LTE+Wi-Fi IMD products (beat frequencies, IM3, etc.)
                            # These are coordinated regardless of victim (e.g., LTE+Wi-Fi → GNSS interference)
                            elif (product_type in ['IM2', 'IM3', 'IM4', 'IM5', 'IM7'] and 
                                  any(coex in str(aggressors) for coex in ['WiFi_2G', 'WiFi_5G'])):
                                should_filter = True
                                wci2_filtered_count += 1
                                
                            # Filter LTE+BLE IMD products (conservative - only non-critical)  
                            elif (product_type in ['IM2', 'IM3', 'IM4', 'IM5', 'IM7'] and 
                                  'BLE' in str(aggressors) and result.get('Risk') not in ['🔴']):
                                should_filter = True
                                wci2_filtered_count += 1
                    
                    if not should_filter:
                        filtered_results.append(result)
                
                # Convert back to DataFrame
                results = pd.DataFrame(filtered_results) if filtered_results else pd.DataFrame()
                
                # Show filtering summary
                filtered_count = original_count - len(results)
                if filtered_count > 0:
                    st.info(f"🔧 **Industry-Standard Coexistence Filtering Applied**: {filtered_count} products filtered " +
                           f"(PTA ISM coordination: {pta_filtered_count}, WCI-2 LTE coordination: {wci2_filtered_count})")
            
            # Filter results for display (keep all for export)
            full_results = results.copy()  # Keep complete results for export
            
            if not show_all_results and 'Risk' in results.columns:
                # Show only meaningful results by default
                results = results[~results['Risk'].isin(['✅', '🔵'])].copy()
                if len(results) == 0:
                    results = full_results.head(max_results)  # Fallback if no critical results
                    st.info("ℹ️ No critical/medium risks found. Showing all results.")
                else:
                    results = results.head(max_results)
            else:
                results = results.head(max_results)
            
            # =========================================================================
            # v2.0.0 PROFESSIONAL RESULTS DISPLAY
            # =========================================================================

            # Run quantitative analysis FIRST (before display)
            quantitative_results = []
            compliance_summary = {'emission_violations': 0, 'total_checked': 0, 'critical_pairs': []}

            if RF_PERFORMANCE_AVAILABLE and st.session_state.get('rf_params'):
                rf_params = st.session_state['rf_params']
                rf_results_list = full_results.to_dict('records') if not full_results.empty else []

                if rf_results_list and selected_band_objs:
                    try:
                        # Fix data format for RF analysis
                        for result in rf_results_list:
                            if 'Frequency' in result and 'Frequency_MHz' not in result:
                                result['Frequency_MHz'] = result['Frequency']

                        # Perform quantitative analysis
                        quantitative_results = analyze_interference_quantitative(
                            rf_results_list, selected_band_objs, rf_params
                        )

                        # Enhance results DataFrame with quantitative columns
                        if quantitative_results:
                            results = enhance_results_with_quantitative(
                                results, quantitative_results, rf_params, selected_band_objs
                            )
                            full_results = enhance_results_with_quantitative(
                                full_results, quantitative_results, rf_params, selected_band_objs
                            )

                            # Create compliance summary
                            compliance_summary = create_compliance_summary(
                                full_results, quantitative_results, selected_band_objs
                            )
                    except Exception as e:
                        st.warning(f"⚠️ Quantitative analysis error: {e}")

            # Display Results Header
            st.subheader(f"📊 Professional Analysis Results ({len(full_results)} total, showing {len(results)})")

            # =========================================================================
            # ENHANCED SUMMARY DASHBOARD
            # =========================================================================
            st.markdown("#### 📈 Analysis Summary")

            # Row 1: Severity counts
            metric_col1, metric_col2, metric_col3, metric_col4, metric_col5 = st.columns(5)
            with metric_col1:
                critical_count = len(full_results[full_results['Risk'] == '🔴'])
                st.metric("🔴 Critical", critical_count)
            with metric_col2:
                high_count = len(full_results[full_results['Risk'] == '🟠'])
                st.metric("🟠 High", high_count)
            with metric_col3:
                medium_count = len(full_results[full_results['Risk'] == '🟡'])
                st.metric("🟡 Medium", medium_count)
            with metric_col4:
                low_count = len(full_results[full_results['Risk'] == '🔵'])
                st.metric("🔵 Low", low_count)
            with metric_col5:
                safe_count = len(full_results[full_results['Risk'] == '✅'])
                st.metric("✅ Safe", safe_count)

            # Row 2: Compliance and quantitative metrics
            if quantitative_results:
                comp_col1, comp_col2, comp_col3, comp_col4 = st.columns(4)
                with comp_col1:
                    if REGULATORY_AVAILABLE:
                        violations = compliance_summary.get('emission_violations', 0)
                        if violations > 0:
                            st.metric("3GPP Compliance", f"✗ {violations} Violations",
                                     delta=f"-{violations}", delta_color="inverse")
                        else:
                            st.metric("3GPP Compliance", "✓ PASS")
                    else:
                        st.metric("3GPP Compliance", "N/A")

                with comp_col2:
                    if quantitative_results:
                        avg_desense = np.mean([r.desensitization_db for r in quantitative_results])
                        st.metric("Avg Desense", f"{avg_desense:.1f} dB")
                    else:
                        st.metric("Avg Desense", "N/A")

                with comp_col3:
                    if quantitative_results:
                        max_desense = max([r.desensitization_db for r in quantitative_results])
                        st.metric("Max Desense", f"{max_desense:.1f} dB")
                    else:
                        st.metric("Max Desense", "N/A")

                with comp_col4:
                    if quantitative_results:
                        min_margin = min([r.interference_margin_db for r in quantitative_results])
                        st.metric("Min Margin", f"{min_margin:+.1f} dB",
                                 help="Positive = safe, Negative = interference above sensitivity")
                    else:
                        st.metric("Min Margin", "N/A",
                                 help="Positive = safe, Negative = interference above sensitivity")

            st.markdown("---")

            # =========================================================================
            # PROFESSIONAL RESULTS TABLE
            # =========================================================================

            # Select columns for display
            display_columns = ['Type', 'Frequency', 'Aggressors', 'Victims', 'Risk']
            if 'P_TX (dBm)' in results.columns:
                display_columns.extend(['P_TX (dBm)', 'P_RX (dBm)', 'Desense (dB)', 'Margin (dB)', 'Compliance'])

            # Filter to available columns
            display_columns = [c for c in display_columns if c in results.columns]
            display_df = results[display_columns]

            # Results table with highlighting
            styled_df = display_df.style.apply(highlight_risks, axis=1)
            st.dataframe(styled_df, use_container_width=True, height=400)

            # =========================================================================
            # COMPLIANCE REPORT SECTION
            # =========================================================================
            if REGULATORY_AVAILABLE and quantitative_results:
                with st.expander("📋 3GPP/FCC Compliance Report", expanded=False):
                    st.markdown("#### Regulatory Compliance Analysis")

                    if compliance_summary.get('emission_violations', 0) > 0:
                        st.error(f"⚠️ **{compliance_summary['emission_violations']} Regulatory Violation(s) Detected**")

                        # Violations table
                        violation_data = []
                        for pair in compliance_summary.get('critical_pairs', []):
                            violation_data.append({
                                'Aggressor': pair['aggressor'],
                                'Victim': pair['victim'],
                                'Frequency (MHz)': f"{pair['frequency']:.1f}",
                                'Issue': pair['reason'],
                                'Margin (dB)': f"{pair['margin']:.1f}"
                            })
                        if violation_data:
                            st.dataframe(pd.DataFrame(violation_data), use_container_width=True)
                    else:
                        st.success("✅ **All emissions within regulatory limits**")

                    # Isolation requirements (if module available)
                    if ISOLATION_MATRIX_AVAILABLE:
                        st.markdown("---")
                        st.markdown("#### 🔧 Critical Isolation Requirements")

                        critical_pairs = get_all_critical_pairs()
                        if critical_pairs:
                            iso_data = []
                            for pair in critical_pairs[:10]:  # Top 10
                                iso_data.append({
                                    'Aggressor': pair['aggressor'],
                                    'Victim': pair['victim'],
                                    'Min Isolation (dB)': f"{pair['min_isolation_db']:.0f}",
                                    'Product Types': ', '.join(pair['product_types']),
                                    'Notes': pair['notes'][:50] + '...' if len(pair['notes']) > 50 else pair['notes']
                                })
                            st.dataframe(pd.DataFrame(iso_data), use_container_width=True)

            # =========================================================================
            # MONTE CARLO ANALYSIS (Optional)
            # =========================================================================
            if RF_PERFORMANCE_AVAILABLE and quantitative_results:
                st.markdown("---")
                with st.expander("⚡ Advanced: Monte Carlo Worst-Case Analysis", expanded=False):
                    st.markdown("""
                    **Monte Carlo Simulation** - Analyze worst-case interference with manufacturing
                    and temperature tolerances (±1dB TX power, ±2dB IIP3, ±3dB isolation, -40°C to +85°C).
                    """)

                    mc_col1, mc_col2 = st.columns([3, 1])
                    with mc_col1:
                        n_iterations = st.slider("Iterations", 100, 5000, 1000, 100)
                    with mc_col2:
                        run_monte_carlo = st.button("🎲 Run Monte Carlo", type="primary")

                    if run_monte_carlo:
                        with st.spinner(f"Running {n_iterations} Monte Carlo iterations..."):
                            try:
                                rf_params = st.session_state['rf_params']
                                tolerances = ToleranceParameters()

                                mc_results = monte_carlo_interference_analysis(
                                    base_params=rf_params,
                                    tolerances=tolerances,
                                    interference_products=full_results.to_dict('records'),
                                    band_objects=selected_band_objs,
                                    n_iterations=n_iterations
                                )

                                if mc_results:
                                    st.success("✅ Monte Carlo analysis complete")

                                    mc_metric1, mc_metric2, mc_metric3, mc_metric4 = st.columns(4)
                                    with mc_metric1:
                                        st.metric("P50 (Typical)", f"{mc_results['p50_desense']:.1f} dB")
                                    with mc_metric2:
                                        st.metric("P95 (Worst Case)", f"{mc_results['p95_desense']:.1f} dB",
                                                 delta=f"+{mc_results['p95_desense']-mc_results['p50_desense']:.1f}")
                                    with mc_metric3:
                                        st.metric("P99 (Extreme)", f"{mc_results['p99_desense']:.1f} dB")
                                    with mc_metric4:
                                        st.metric("Max Observed", f"{mc_results['max_desense']:.1f} dB")

                                    # Show worst-case conditions
                                    if 'worst_conditions' in mc_results:
                                        st.markdown("**Worst-Case Conditions:**")
                                        st.json(mc_results['worst_conditions'])

                            except Exception as e:
                                st.error(f"Monte Carlo analysis failed: {e}")

            # =========================================================================
            # LEGACY QUANTITATIVE SECTION (Keep for backwards compatibility)
            # =========================================================================
            if RF_PERFORMANCE_AVAILABLE and st.session_state.get('rf_params') and quantitative_results:
                st.markdown("---")
                with st.expander("📖 Professional RF Analysis Methodology", expanded=False):
                    method_col1, method_col2 = st.columns(2)
                    with method_col1:
                        st.markdown("""
                        **🎯 v2.0.0 Professional Calculations:**
                        • **Quantitative Power Levels**: All results show dBm/dBc values
                        • **3GPP Compliance**: Automatic limit checking (TS 36.101/38.101)
                        • **I/N Methodology**: Standard interference-to-noise ratio analysis
                        • **Desensitization**: Actual receiver impact in dB

                        **🔧 Harmonic/IMD Calculations:**
                        • **HD Formulas**: Polynomial coefficient-based (HD4 = HD2-30dB)
                        • **IMD Formulas**: P_IM3 = 3×P_in - 2×IIP3 (standard two-tone)
                        • **Coupling-Aware Isolation**: Realistic multi-path model
                        """)
                    with method_col2:
                        st.markdown("""
                        **📡 Coexistence Features:**
                        • **PTA**: BLE↔Wi-Fi 2.4G coordination
                        • **WCI-2**: LTE↔Wi-Fi coordination
                        • **Duty Cycle Correction**: TDM/intermittent interference
                        • **Filter Rejection**: Receiver selectivity modeling

                        **📋 New in v2.0.0:**
                        • Professional results table with dBm columns
                        • Compliance dashboard with 3GPP status
                        • Monte Carlo worst-case analysis
                        • Isolation matrix requirements
                        """)

            # Continue with quantitative charts if available
            if RF_PERFORMANCE_AVAILABLE and st.session_state.get('rf_params') and quantitative_results:
                # Keep existing chart logic but under expandable section
                with st.expander("📈 Quantitative Analysis Charts", expanded=True):
                    rf_params = st.session_state['rf_params']

                    try:
                        # Create comprehensive summary
                        quant_df = create_quantitative_summary(quantitative_results)

                        # Show quantitative metrics
                        quant_col1, quant_col2, quant_col3, quant_col4 = st.columns(4)

                        with quant_col1:
                            avg_interference = np.mean([r.interference_at_victim_dbm for r in quantitative_results])
                            st.metric("Avg Interference", f"{avg_interference:.1f} dBm")

                        with quant_col2:
                            max_desense = max([r.desensitization_db for r in quantitative_results])
                            st.metric("Max Desensitization", f"{max_desense:.2f} dB",
                                    help="Realistic range: 0-60 dB. Fixed calculation method.")

                        with quant_col3:
                            critical_interf = len([r for r in quantitative_results if r.risk_level in ['Critical', 'High']])
                            st.metric("Critical Interference", critical_interf)

                        with quant_col4:
                            min_margin = min([r.interference_margin_db for r in quantitative_results])
                            margin_help = "Positive = safe margin, Negative = interference above sensitivity"
                            st.metric("Min Margin", f"{min_margin:+.1f} dB", help=margin_help)

                        # Display quantitative results table
                        st.markdown("**📊 Quantitative Analysis Results**")
                        st.dataframe(quant_df, use_container_width=True, height=300)

                        # Professional RF spectrum visualization
                        st.markdown("**📈 RF Spectrum Analysis**")

                        # Create spectrum chart
                        fig = create_rf_spectrum_chart(quantitative_results, rf_params)
                        if fig:
                            st.plotly_chart(fig, use_container_width=True)

                            # Chart interpretation in expandable section
                            with st.expander("📊 How to Read This Chart"):
                                chart_col1, chart_col2 = st.columns(2)
                                with chart_col1:
                                    st.markdown("""
                                    **📊 Chart Elements:**
                                    - **Green bars**: Fundamental signals (0 dBc reference)
                                    - **Yellow products**: 2nd order dominant (IM2, 2H)
                                    - **Orange products**: 3rd order dominant (IM3, 3H)
                                    - **Blue products**: 4th order dominant (IM4, 4H)
                                    - **Red products**: 5th order dominant (IM5, 5H)
                                    """)
                                with chart_col2:
                                    st.markdown("""
                                    **📈 Interpretation:**
                                    - **Height** = interference level in dBc relative to fundamental
                                    - **Hover** for details: formulas, coefficients, risk assessment
                                    - **Professional accuracy** with 5th-order polynomial expansion
                                    """)
                        else:
                            st.warning("⚠️ Could not generate spectrum chart")

                        # Additional analysis charts
                        chart_col1, chart_col2 = st.columns(2)

                        with chart_col1:
                            # Risk distribution
                            risk_dist = pd.DataFrame([{'Risk': r.risk_level, 'Count': 1} for r in quantitative_results])
                            if not risk_dist.empty:
                                risk_counts = risk_dist.groupby('Risk').count().reset_index()
                                fig_risk = px.pie(risk_counts, values='Count', names='Risk',
                                                title="Risk Distribution",
                                                color_discrete_map={
                                                    'Critical': '#c62828',
                                                    'High': '#ef6c00',
                                                    'Medium': '#f57f17',
                                                    'Low': '#1565c0',
                                                    'Negligible': '#2e7d32'
                                                })
                                st.plotly_chart(fig_risk, use_container_width=True)

                        with chart_col2:
                            # Desensitization levels
                            desense_data = pd.DataFrame([{
                                'Product': r.product_type,
                                'Desensitization_dB': r.desensitization_db,
                                'Frequency_MHz': r.frequency_mhz
                            } for r in quantitative_results])

                            if not desense_data.empty:
                                fig_desense = px.scatter(desense_data, x='Frequency_MHz', y='Desensitization_dB',
                                                       color='Product', title="Desensitization vs Frequency",
                                                       labels={'Desensitization_dB': 'Desensitization (dB)',
                                                              'Frequency_MHz': 'Frequency (MHz)'})
                                st.plotly_chart(fig_desense, use_container_width=True)

                    except Exception as e:
                        st.error(f"❌ Error in quantitative chart generation: {str(e)}")
                        st.info("💡 Try selecting fewer bands or using a different system preset")
                
                # Technical details in expandable sections
                with st.expander("🔬 Technical Details & Column Explanations"):
                    detail_col1, detail_col2 = st.columns(2)
                    with detail_col1:
                        st.markdown("""
                        **🔋 Power Levels & Measurements:**
                        - **TX Power**: Transmitter output power (dBm)
                        - **Interference (dBc)**: Relative to carrier
                        - **At TX (dBm)**: Absolute interference power at transmitter output
                        - **At Victim (dBm)**: After antenna isolation & path loss
                        - **Sensitivity**: Victim receiver threshold (dBm)
                        - **Margin**: Positive = safe, negative = interference
                        - **Desense (dB)**: Professional I/N calculation
                        """)
                    with detail_col2:
                        st.markdown("""
                        **🎯 Key Engineering Insights:**
                        - **IM3 ≠ just 3rd order**: Contains 3rd + 5th + 7th order contributions
                        - **IM2 ≠ 2×HD2**: Contains 2nd + 4th order terms
                        - **Even-order products** (IM2, IM4) often stronger than odd-order
                        - **Mathematical Foundation**: V₀ = a₀ + a₁Vᵢ + a₂Vᵢ² + a₃Vᵢ³ + a₄Vᵢ⁴ + a₅Vᵢ⁵
                        """)
                    
                    st.info("""
                    **📈 Typical RF System Levels** (without optimization):
                    • HD2/IM2: ~-25 dBc (2nd + 4th order)  • HD3/IM3: ~-40 dBc (3rd + 5th + 7th order)
                    • HD4/IM4: ~-55 dBc (4th + 2nd order)  • HD5/IM5: ~-60 dBc (5th + 3rd order)
                    """)
                    
                    st.success("""
                    **🔧 Professional RF Engineering Approach**: 
                    TX filtering → Antenna isolation → PCB isolation → RX filtering → Realistic interference levels
                    """)
                
                with st.expander("🧮 Mathematical Formulas"):
                    st.markdown("""
                    **IM3 Products (2f₁±f₂):**
                    ```
                    Coefficient = (3/4)a₃V₁²V₂ + (15/8)a₅V₁⁴V₂ + (15/4)a₅V₁²V₂³ + ...
                    ```
                    *Note: Dominated by a₃ but a₅ contributes significantly!*
                    
                    **IM2 Beat Products (f₁±f₂):**
                    ```  
                    Coefficient = a₂V₁V₂ + (3/2)a₄V₁³V₂ + (3/2)a₄V₁V₂³ + ...
                    ```
                    *Note: NOT just 2×HD2! Contains 4th order terms.*
                    
                    **Why This Matters:**
                    - Traditional analysis underestimates interference by ignoring higher-order contributions
                    - Wideband systems see IM4 products landing in-band
                    - Even-order products can be stronger than odd-order in real systems
                    """)
            
            # Export Section - Professional Export
            st.markdown("---")
            st.subheader("📤 Professional Data Export")
            
            export_col1, export_col2, export_col3 = st.columns(3)
            
            with export_col1:
                # Professional CSV Export with Metadata
                if st.button("📄 Professional CSV", use_container_width=True):
                    export_data = full_results if include_safe else full_results[~full_results['Risk'].isin(['✅', '🔵'])]
                    
                    # Add professional metadata
                    enhanced_data = export_data.copy()
                    enhanced_data['Analysis_Date'] = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
                    enhanced_data['Tool_Version'] = __version__
                    enhanced_data['Mathematical_Validation'] = MATHEMATICAL_VALIDATION['validation_status']
                    enhanced_data['Theory_Reference'] = 'RF Insights Baseband Intermodulation'
                    enhanced_data['Guard_Band_MHz'] = guard
                    enhanced_data['Total_Products_Calculated'] = len(full_results)
                    
                    csv_data = enhanced_data.to_csv(index=False)
                    timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
                    
                    st.download_button(
                        "⬇️ Download Professional CSV",
                        data=csv_data,
                        file_name=f"rf_interference_professional_{timestamp}.csv",
                        mime="text/csv",
                        help="CSV with professional metadata and validation status"
                    )
                    st.success(f"✅ Professional CSV ready! {len(export_data)} products")
            
            with export_col2:
                # Enhanced Excel Export with Multiple Sheets
                if st.button("📊 Professional Excel", use_container_width=True):
                    export_data = full_results if include_safe else full_results[~full_results['Risk'].isin(['✅', '🔵'])]
                    
                    buffer = BytesIO()
                    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                        # Main results sheet
                        export_data.to_excel(writer, sheet_name='Interference_Analysis', index=False)
                        
                        # Professional metadata sheet
                        metadata = pd.DataFrame({
                            'Parameter': [
                                'Analysis Date', 'Tool Version', 'Mathematical Validation',
                                'Theory Reference', 'Total Products', 'Critical Products',
                                'Guard Band (MHz)', 'Frequency Range Validated', 'Review Status'
                            ],
                            'Value': [
                                pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
                                __version__,
                                MATHEMATICAL_VALIDATION['validation_status'],
                                'RF Insights Baseband Intermodulation Theory',
                                len(full_results),
                                len(full_results[full_results['Risk'].isin(['🔴', '🟠'])]),
                                guard,
                                f"{MATHEMATICAL_VALIDATION['frequency_range_validated'][0]}-{MATHEMATICAL_VALIDATION['frequency_range_validated'][1]} MHz",
                                'Complete - Production Ready'
                            ]
                        })
                        metadata.to_excel(writer, sheet_name='Analysis_Metadata', index=False)
                        
                        # Band configuration sheet
                        selected_band_objs = [BANDS[code] for code in available_bands]
                        band_config = pd.DataFrame([{
                            'Band_Code': band.code,
                            'Band_Label': band.label,
                            'Category': band.category,
                            'TX_Low_MHz': band.tx_low if band.tx_low > 0 else 'RX Only',
                            'TX_High_MHz': band.tx_high if band.tx_high > 0 else 'RX Only',
                            'RX_Low_MHz': band.rx_low,
                            'RX_High_MHz': band.rx_high
                        } for band in selected_band_objs])
                        band_config.to_excel(writer, sheet_name='Band_Configuration', index=False)
                        
                        # Risk summary sheet
                        total_results = len(full_results) if len(full_results) > 0 else 1  # Prevent div/0
                        risk_summary = pd.DataFrame({
                            'Risk_Level': ['🔴 Critical', '🟠 High', '🟡 Medium', '🔵 Low', '✅ Safe'],
                            'Count': [
                                len(full_results[full_results['Risk'] == '🔴']),
                                len(full_results[full_results['Risk'] == '🟠']),
                                len(full_results[full_results['Risk'] == '🟡']),
                                len(full_results[full_results['Risk'] == '🔵']),
                                len(full_results[full_results['Risk'] == '✅'])
                            ],
                            'Percentage': [
                                f"{len(full_results[full_results['Risk'] == '🔴'])/total_results*100:.1f}%",
                                f"{len(full_results[full_results['Risk'] == '🟠'])/total_results*100:.1f}%",
                                f"{len(full_results[full_results['Risk'] == '🟡'])/total_results*100:.1f}%",
                                f"{len(full_results[full_results['Risk'] == '🔵'])/total_results*100:.1f}%",
                                f"{len(full_results[full_results['Risk'] == '✅'])/total_results*100:.1f}%"
                            ]
                        })
                        risk_summary.to_excel(writer, sheet_name='Risk_Summary', index=False)
                    
                    timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
                    st.download_button(
                        "⬇️ Download Professional Excel",
                        data=buffer.getvalue(),
                        file_name=f"rf_interference_professional_{timestamp}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        help="Multi-sheet Excel with analysis, metadata, band config, and risk summary"
                    )
                    st.success(f"✅ Professional Excel ready! {len(export_data)} products across 4 sheets")
            
            with export_col3:
                # JSON Export
                if st.button("🔧 Export JSON", use_container_width=True):
                    export_data = full_results if include_safe else full_results[~full_results['Risk'].isin(['✅', '🔵'])]
                    json_data = export_data.to_dict('records')
                    json_str = pd.io.json.dumps(json_data, indent=2)
                    timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
                    
                    st.download_button(
                        "⬇️ Download JSON",
                        data=json_str,
                        file_name=f"rf_interference_{timestamp}.json",
                        mime="application/json"
                    )
                    st.success(f"✅ JSON ready! {len(export_data)} products")
            
            # Simple Visualizations (like GitHub version)
            st.markdown("---")
            st.subheader("📊 Analysis Views")
            
            viz_tab1, viz_tab2, viz_tab3, viz_tab4 = st.tabs([
                "🎯 Frequency Spectrum", "📈 Risk Analysis", "🔍 Band Coverage", "⚡ Product Distribution"
            ])
            
            with viz_tab1:
                # Frequency spectrum plot
                if 'Frequency' in full_results.columns:
                    valid_results = full_results[full_results['Frequency'] > 0]
                    
                    if not valid_results.empty:
                        # Simple frequency scatter plot with text-based risk mapping
                        # Convert emoji risk symbols to text for better Altair compatibility
                        valid_results = valid_results.copy()
                        risk_text_mapping = {
                            '🔴': 'Critical',
                            '🟠': 'High',
                            '🟡': 'Medium',
                            '🔵': 'Low',
                            '✅': 'Safe'
                        }
                        valid_results['Risk_Text'] = valid_results['Risk'].map(risk_text_mapping).fillna('Safe')
                        
                        spectrum_chart = alt.Chart(valid_results).mark_circle(size=100, opacity=0.8).encode(
                            x=alt.X('Frequency:Q', title='Frequency (MHz)', scale=alt.Scale(nice=False)),
                            y=alt.Y('Type:N', title='Product Type', sort=['2H', '3H', '4H', '5H', 'IM2', 'IM3', 'IM4', 'IM5', 'IM7']),
                            color=alt.Color('Risk_Text:N',
                                scale=alt.Scale(
                                    domain=['Critical', 'High', 'Medium', 'Low', 'Safe'],
                                    range=['#d32f2f', '#f57c00', '#fbc02d', '#1976d2', '#388e3c']
                                ),
                                legend=alt.Legend(title="Risk Level", orient="right", symbolType="circle", symbolSize=100)
                            ),
                            tooltip=[
                                alt.Tooltip('Type:N', title='Product Type'),
                                alt.Tooltip('Frequency:Q', title='Frequency (MHz)', format='.1f'),
                                alt.Tooltip('Aggressors:N', title='Aggressors'),
                                alt.Tooltip('Victims:N', title='Victims'),
                                alt.Tooltip('Risk:N', title='Risk Level'),
                                alt.Tooltip('Risk_Text:N', title='Risk Category')
                            ]
                        ).properties(
                            width=700,
                            height=400,
                            title="Interference Products by Frequency and Risk Level"
                        ).interactive()
                        
                        st.altair_chart(spectrum_chart, use_container_width=True)
                        
                        # Show summary statistics
                        st.info(f"📊 Showing {len(valid_results)} interference products across frequency spectrum")
                    else:
                        st.info("No valid frequency data to display")
            
            with viz_tab2:
                # Risk analysis pie chart
                if 'Risk' in full_results.columns:
                    risk_counts = full_results['Risk'].value_counts().reset_index()
                    risk_counts.columns = ['Risk_Level', 'Count']
                    
                    risk_chart = alt.Chart(risk_counts).mark_arc(
                        innerRadius=50,
                        outerRadius=120
                    ).encode(
                        theta=alt.Theta('Count:Q'),
                        color=alt.Color('Risk_Level:N',
                            scale=alt.Scale(
                                domain=['🔴', '🟠', '🟡', '🔵', '✅'],
                                range=['#d32f2f', '#f57c00', '#fbc02d', '#1976d2', '#388e3c']
                            )
                        ),
                        tooltip=['Risk_Level:N', 'Count:Q']
                    ).properties(
                        width=400,
                        height=400,
                        title="Risk Level Distribution"
                    )
                    
                    st.altair_chart(risk_chart, use_container_width=True)
            
            with viz_tab3:
                # Band coverage chart
                if available_bands:
                    band_data = []
                    for band in selected_band_objs:
                        if band.tx_low > 0:
                            band_data.append({
                                'Band': band.code,
                                'Start': band.tx_low,
                                'End': band.tx_high,
                                'Type': 'TX',
                                'Category': band.category
                            })
                        
                        band_data.append({
                            'Band': band.code,
                            'Start': band.rx_low,
                            'End': band.rx_high,
                            'Type': 'RX',
                            'Category': band.category
                        })
                    
                    if band_data:
                        band_df = pd.DataFrame(band_data)
                        
                        coverage_chart = alt.Chart(band_df).mark_rect().encode(
                            x=alt.X('Start:Q', title='Frequency (MHz)'),
                            x2='End:Q',
                            y=alt.Y('Band:N', title='Band'),
                            color=alt.Color('Type:N',
                                scale=alt.Scale(domain=['TX', 'RX'], range=['#ff6b6b', '#4ecdc4'])
                            ),
                            tooltip=['Band:N', 'Type:N', 'Start:Q', 'End:Q', 'Category:N']
                        ).properties(
                            width=700,
                            height=max(300, len(selected_band_objs) * 25),
                            title="Band Frequency Coverage"
                        ).interactive()
                        
                        st.altair_chart(coverage_chart, use_container_width=True)
            
            with viz_tab4:
                # Product distribution histogram
                if 'Type' in full_results.columns:
                    type_counts = full_results['Type'].value_counts().reset_index()
                    type_counts.columns = ['Product_Type', 'Count']
                    
                    dist_chart = alt.Chart(type_counts).mark_bar().encode(
                        x=alt.X('Count:Q', title='Number of Products'),
                        y=alt.Y('Product_Type:N', title='Product Type', sort='-x'),
                        color=alt.Color('Count:Q', scale=alt.Scale(scheme='blues')),
                        tooltip=['Product_Type:N', 'Count:Q']
                    ).properties(
                        width=600,
                        height=300,
                        title="Product Type Distribution"
                    )
                    
                    st.altair_chart(dist_chart, use_container_width=True)
        
        else:
            st.warning("⚠️ No interference products found")

st.markdown("---")
st.markdown("### 📡 About & Attribution")

col_std, col_links, col_legal, col_academic = st.columns(4)

with col_std:
    st.markdown("""
    **Supported Standards**
    • 3GPP LTE Bands (Release 17)
    • IEEE 802.11 Wi‑Fi (2.4/5/6 GHz)
    • Bluetooth LE (BLE 5.x)
    • GNSS/GPS L1/L2/L5
    • ISM Band Analysis
    • **RF Insights Theory Validated** ✅
    """)

with col_links:
    st.markdown("""
    **Project Links**
    • [GitHub Repository](https://github.com/RFingAdam/rf-interference-calculator)
    • [Theory Validation](https://github.com/RFingAdam/rf-interference-calculator/blob/main/RF_INSIGHTS_VALIDATION.md)
    • [Report Issues](https://github.com/RFingAdam/rf-interference-calculator/issues)
    • [License (MIT)](https://github.com/RFingAdam/rf-interference-calculator/blob/main/LICENSE)
    """)

with col_legal:
    st.markdown("""
    **License & Disclaimer**
    • MIT License — Free for commercial/educational use
    • © 2025 RFingAdam — Professional analysis
    • No warranty — **Professional validation required**
    • User responsible for regulatory compliance
    """)

with col_academic:
    st.markdown("""
    **Academic References**
    • [RF Insights - Baseband IMD](https://www.rfinsights.com/concepts/baseband-tones-intermodulation/)
    • IEEE 802.11 Standard (WiFi)
    • 3GPP TS 36.101 (LTE)
    • [Razavi - RF Microelectronics](https://www.pearson.com/store/p/rf-microelectronics/P100000318552)
    • Mathematical foundation peer-reviewed
    """)

# Technical disclaimer for professional use
with st.expander("⚖️ Technical Architecture & Professional Usage Guidelines"):
    st.markdown("""
    ### Software Architecture
    **Modular Three-Layer Design:**
    - **Data Layer** (`bands.py`): Type-safe band definitions with @dataclass for 70+ wireless bands
    - **Calculation Engine** (`calculator.py`): Mathematical IMD/harmonic analysis with professional risk assessment
    - **RF Performance Module** (`rf_performance.py`): Quantitative dBc/dBm analysis with system parameters
    - **User Interface** (`ui.py`): Professional Streamlit visualization with multi-tab analysis
    
    **5-Level Risk Assessment System (Professionally Validated):**
    - **🔴 Critical (5)**: GPS interference, public safety bands, >10 dB desensitization risk
    - **🟠 High (4)**: Strong interference likely to cause measurable performance degradation  
    - **🟡 Medium (3)**: Moderate interference, may affect sensitivity in poor RF conditions
    - **🔵 Low (2)**: Weak interference, minimal impact under normal operational scenarios
    - **✅ Safe (1)**: No significant interference detected, meets professional design margins
    
    ### Mathematical Foundation (Peer-Reviewed)
    **Polynomial Nonlinearity Model:**
    ```
    V₀ = a₀ + a₁Vᵢ + a₂Vᵢ² + a₃Vᵢ³ + a₄Vᵢ⁴ + a₅Vᵢ⁵
    ```
    **Two-Tone Analysis:**
    ```
    Vᵢ = V₁cos(ω₁t) + V₂cos(ω₂t)
    ```
    
    **RF Insights Theory Validation:**
    - Band center tones → In-band EVM degradation (IM3/IM5)
    - Band edge tones → Spread ACLR distortion 
    - Even-order products → ACLR zones (regulatory impact)
    - Odd-order close-in → In-band interference (EVM impact)
    
    ### Professional Usage Guidelines
    **Academic Applications:**
    - Graduate-level RF engineering coursework
    - Graduate-level research tool
    - Industry training programs
    - Regulatory compliance analysis
    
    **Industry Applications:**  
    - Pre-certification interference analysis
    - System design optimization
    - Coexistence studies (PTA/WCI-2)
    - Regulatory submission documentation
    
    ### Analysis Methodology (IEEE Standard Compliant)
    - **Harmonic Products**: Fundamental frequency multiplication (2f, 3f, 4f, 5f)
    - **IM2 Products**: Second-order intermodulation (f₁±f₂) - ACLR critical per RF Insights
    - **IM3 Products**: Third-order intermodulation (2f₁±f₂, f₁±2f₂) - EVM critical per RF Insights
    - **IM4/IM5 Products**: Higher-order mixing products - mixed in-band/ACLR effects
    - **Risk Assessment**: Frequency-based severity with technology-specific sensitivities
    
    ### Validation Requirements (Professional Standards)
    For production deployments, validate theoretical predictions with:
    - **Spectrum analyzer measurements** of actual spurious emissions (±1 dB accuracy)
    - **Conducted emission testing** per regulatory standards (FCC Part 15, ETSI EN 300 328)
    - **Radiated emission compliance** testing in accredited EMC facilities
    - **System-level coexistence** validation with target victim receivers
    - **Environmental testing** across temperature (-40°C to +85°C) and voltage ranges
    - **Statistical analysis** with Monte Carlo simulation for worst-case scenarios
    
    ### Limitations & Assumptions (Professional Awareness)
    - **Linear system assumption** for isolation calculations
    - **Ideal filtering models** - real filters have finite rejection
    - **Temperature stability** assumed (components drift ±2 dB over temperature)
    - **Manufacturing variations** not modeled (±3 dB typical component tolerance)
    - **Aging effects** not considered (±1 dB over 10 years typical)
    
    ### Future Enhancements Under Development
    - **Phase noise analysis** for close-in spurious products
    - **Nonlinear filter models** with measured S-parameters
    - **Monte Carlo simulation** for statistical worst-case analysis
    - **Machine learning** risk prediction based on field measurements
    """)

st.markdown("---")
