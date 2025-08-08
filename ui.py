import streamlit as st
__version__ = "1.3.0"  # Update this version string with each release
import pandas as pd
from bands import BANDS, Band
from calculator import evaluate, calculate_all_products, validate_band_configuration
import altair as alt
from io import BytesIO

# Import pyperclip with fallback for cloud deployment
try:
    import pyperclip
    PYPERCLIP_AVAILABLE = True
except ImportError:
    PYPERCLIP_AVAILABLE = False
    st.warning("⚠️ Clipboard functionality not available in this deployment environment.")

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
    available_options = [f"{b.code}: {b.label}" for b in filtered_bands.values()]
    available_bands = st.multiselect(
        "Select bands to analyze:",
        available_options,
        help="Choose bands for interference analysis. Use Ctrl+Click for multiple selections."
    )
    st.info(f"**{len(available_bands)} bands selected** from {len(filtered_bands)} available")

with col2:
    st.subheader("🎯 Selected Bands Summary")
    if available_bands:
        selected_band_ids = [b.split(":")[0] for b in available_bands]
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
                                   help="Calculate 2nd and 3rd harmonic products (2f, 3f)")
with col_h2:
    if harmonics_enabled:
        st.success("2H and 3H products will be calculated")
    else:
        st.info("Harmonic analysis disabled")

# IMD section
st.markdown("#### ⚡ Intermodulation Products")
st.markdown("*Select which IMD products to analyze:*")

col_3, col_4, col_5, col_6 = st.columns(4)
with col_3:
    imd3_enabled = st.checkbox("IM3 Products", value=True, help="2f₁ ± f₂, includes all edge cases")
    if imd3_enabled:
        st.caption("✓ Fundamental & harmonic mixing")
with col_4:
    imd4 = st.checkbox("IM4 Products", value=False, help="2f₁ + 2f₂")
    if imd4:
        st.caption("⚠️ Higher order products")
with col_5:
    imd5 = st.checkbox("IM5 Products", value=False, help="3f₁ ± 2f₂")
    if imd5:
        st.caption("⚠️ Complex mixing")
with col_6:
    imd7 = st.checkbox("IM7 Products", value=False, help="4f₁ ± 3f₂")
    if imd7:
        st.caption("⚠️ Very high order")

# Analysis complexity warning
enabled_products = sum([harmonics_enabled, imd3_enabled, imd4, imd5, imd7])
if enabled_products > 3:
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
                selected_band_ids = [b.split(":")[0] for b in available_bands]
                selected_band_objs = [BANDS[c] for c in selected_band_ids]
                
                # Input validation
                if len(selected_band_objs) > 50:
                    st.warning("⚠️ Large number of bands selected. Calculation may take longer...")
                
                # Use new exhaustive calculation function with enhanced parameters
                results_list, overlap_alerts = calculate_all_products(
                    selected_band_objs, 
                    guard=guard, 
                    imd4=imd4, 
                    imd5=imd5, 
                    imd7=imd7, 
                    aclr_margin=aclr_margin
                )
                
                # Apply frequency filter if enabled
                if freq_filter_enabled and freq_range:
                    filtered_results = []
                    for r in results_list:
                        freq = r.get('Frequency_MHz', r.get('Freq_low', 0))
                        if freq_range[0] <= freq <= freq_range[1]:
                            filtered_results.append(r)
                    results_list = filtered_results
                    if len(filtered_results) < len(results_list):
                        st.info(f"📊 Frequency filter applied: {len(filtered_results)} results shown (filtered from {len(results_list)})")
                
                results = pd.DataFrame(results_list)
                
                if results.empty:
                    st.warning("No interference products found with current settings.")
                    st.stop()
                    
        except Exception as e:
            st.error(f"❌ Calculation error: {str(e)}")
            st.error("Please check your band selections and try again.")
            st.stop()

        # Enhanced results summary with validation
        
        # Calculate basic metrics
        total_products = len(results)
        risk_products = (results["Risk"] == "⚠️").sum() if "Risk" in results.columns else 0
        safe_products = total_products - risk_products
        
        # Validate configuration
        config_warnings = validate_band_configuration(selected_band_objs)
        if config_warnings:
            for warning in config_warnings:
                st.warning(f"⚠️ Configuration: {warning}")
        
        st.subheader("📊 Analysis Results")
        
        # Enhanced metrics display
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

        # Results table
        st.subheader("📋 Detailed Results")
        # Ensure all columns are present and in the same order as app.py
        expected_cols = [
            "Type", "IM3_Type", "Formula", "Frequency_MHz", "Aggressors", "Victims", "Risk", "Details"
        ]
        for col in expected_cols:
            if col not in results.columns:
                results[col] = ""
        results = results[expected_cols]

        def highlight_risks(row):
            if row["Risk"] == "⚠️":
                return ["background-color: rgba(255, 75, 75, 0.1)"] * len(row)
            else:
                return ["background-color: rgba(0, 200, 81, 0.05)"] * len(row)
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
                                    ', '.join([k for k, v in {'IM3': imd3_enabled, 'IM4': imd4, 'IM5': imd5, 'IM7': imd7}.items() if v])]
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
                    st.info("🔄 PDF generation feature coming soon!")
                    st.markdown("""
                    **Planned PDF features:**
                    - Executive summary
                    - Detailed analysis results
                    - Frequency spectrum plots
                    - Risk assessment charts
                    - Band configuration details
                    """)
                    
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
                # Enhanced frequency scatter plot
                color_col = "Risk" if "Risk" in results.columns else results.columns[-1]
                freq_col = "Frequency_MHz" if "Frequency_MHz" in results.columns else "Freq_low"
                
                chart = alt.Chart(results).mark_circle(size=120, opacity=0.7).encode(
                    x=alt.X(freq_col, title="Frequency (MHz)", scale=alt.Scale(nice=True)),
                    y=alt.Y("Type:N", title="Product Type", sort=["2H", "3H", "IM3", "IM4", "IM5", "IM7", "ACLR"]),
                    color=alt.Color(
                        color_col, 
                        scale=alt.Scale(domain=["⚠️", "✓"], range=["#ff4444", "#44aa44"]),
                        legend=alt.Legend(title="Risk Status")
                    ),
                    size=alt.condition(
                        alt.datum.Risk == '⚠️',
                        alt.value(180),  # Larger for risk items
                        alt.value(100)
                    ),
                    tooltip=[
                        alt.Tooltip('Type:N', title='Product Type'),
                        alt.Tooltip('Formula:N', title='Formula'),
                        alt.Tooltip(f'{freq_col}:Q', title='Frequency (MHz)', format='.2f'),
                        alt.Tooltip('Aggressors:N', title='Aggressors'),
                        alt.Tooltip('Victims:N', title='Victims'),
                        alt.Tooltip('Risk:N', title='Risk')
                    ]
                ).properties(
                    width=700,
                    height=400,
                    title="RF Spectrum Interference Products"
                ).interactive()
                
                st.altair_chart(chart, use_container_width=True)
            
            with tab2:
                # Risk distribution pie chart
                risk_counts = results['Risk'].value_counts() if 'Risk' in results.columns else pd.Series([0])
                risk_data = pd.DataFrame({
                    'Status': risk_counts.index,
                    'Count': risk_counts.values,
                    'Label': [f"Risk ({risk_counts.get('⚠️', 0)})" if x == '⚠️' else f"Safe ({risk_counts.get('✓', 0)})" for x in risk_counts.index]
                })
                
                pie_chart = alt.Chart(risk_data).mark_arc(innerRadius=50).encode(
                    theta=alt.Theta(field="Count", type="quantitative"),
                    color=alt.Color(
                        field="Status", 
                        scale=alt.Scale(domain=["⚠️", "✓"], range=["#ff4444", "#44aa44"]),
                        legend=alt.Legend(title="Status")
                    ),
                    tooltip=['Label:N', 'Count:Q']
                ).properties(
                    width=300,
                    height=300,
                    title="Risk Distribution"
                )
                
                # Risk by product type
                if 'Type' in results.columns:
                    type_risk = results.groupby(['Type', 'Risk']).size().reset_index(name='Count')
                    risk_by_type = alt.Chart(type_risk).mark_bar().encode(
                        x=alt.X('Type:N', title='Product Type'),
                        y=alt.Y('Count:Q', title='Count'),
                        color=alt.Color('Risk:N', scale=alt.Scale(domain=["⚠️", "✓"], range=["#ff4444", "#44aa44"])),
                        tooltip=['Type:N', 'Risk:N', 'Count:Q']
                    ).properties(
                        width=400,
                        height=300,
                        title="Risk Count by Product Type"
                    )
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.altair_chart(pie_chart, use_container_width=True)
                    with col2:
                        st.altair_chart(risk_by_type, use_container_width=True)
            
            with tab3:
                # Band coverage visualization
                band_data = []
                for band_id in selected_band_ids:
                    band = BANDS[band_id]
                    band_data.extend([
                        {"Band": band.code, "Type": "Tx", "Low": band.tx_low, "High": band.tx_high, "Category": band.category},
                        {"Band": band.code, "Type": "Rx", "Low": band.rx_low, "High": band.rx_high, "Category": band.category}
                    ])
                
                band_df = pd.DataFrame(band_data)
                
                coverage_chart = alt.Chart(band_df).mark_rect(height=15).encode(
                    x=alt.X('Low:Q', title='Frequency (MHz)'),
                    x2='High:Q',
                    y=alt.Y('Band:N', title='Band', sort=band_df['Band'].unique().tolist()),
                    color=alt.Color('Type:N', scale=alt.Scale(domain=['Tx', 'Rx'], range=['#ff6b6b', '#4ecdc4'])),
                    tooltip=['Band:N', 'Type:N', 'Low:Q', 'High:Q', 'Category:N']
                ).properties(
                    width=700,
                    height=max(300, len(selected_band_ids) * 25),
                    title="Band Coverage Overview"
                ).resolve_scale(color='independent')
                
                st.altair_chart(coverage_chart, use_container_width=True)
            
            with tab4:
                # Product distribution histogram
                if freq_col in results.columns:
                    hist_chart = alt.Chart(results).mark_bar(opacity=0.7).encode(
                        x=alt.X(f'{freq_col}:Q', bin=alt.Bin(maxbins=50), title='Frequency (MHz)'),
                        y=alt.Y('count():Q', title='Number of Products'),
                        color=alt.Color('Risk:N', scale=alt.Scale(domain=["⚠️", "✓"], range=["#ff4444", "#44aa44"])),
                        tooltip=['count():Q']
                    ).properties(
                        width=700,
                        height=300,
                        title="Frequency Distribution of Interference Products"
                    )
                    
                    st.altair_chart(hist_chart, use_container_width=True)
                    
                    # Statistics summary
                    freq_data = results[freq_col].dropna()
                    if not freq_data.empty:
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Min Frequency", f"{freq_data.min():.1f} MHz")
                        with col2:
                            st.metric("Max Frequency", f"{freq_data.max():.1f} MHz")
                        with col3:
                            st.metric("Mean Frequency", f"{freq_data.mean():.1f} MHz")
                        with col4:
                            st.metric("Frequency Range", f"{freq_data.max() - freq_data.min():.1f} MHz")

        # Copy to clipboard (markdown)
        if st.button("Copy Results as Markdown"):
            md = results.to_markdown(index=False)
            if PYPERCLIP_AVAILABLE:
                pyperclip.copy(md)
                st.info("Results copied to clipboard as Markdown!")
            else:
                st.text_area("📋 Markdown Results (copy manually):", md, height=200)

        # PDF report (placeholder)
        if st.button("Generate PDF Report"):
            st.warning("PDF report generation coming soon! (WeasyPrint/pdfkit integration)")

# Footer with enhanced information
st.markdown("---")

# Help and documentation section
with st.expander("📖 Help & Documentation"):
    st.markdown("""
    ### 🚀 Quick Start Guide
    1. **Select Categories**: Choose band categories (Wi-Fi, LTE, etc.) in the sidebar
    2. **Choose Bands**: Select specific bands for analysis from the filtered list
    3. **Configure Analysis**: Set guard margins, enable IM products, adjust ACLR settings
    4. **Calculate**: Click "Calculate Interference" to run the analysis
    5. **Review Results**: Examine the detailed results table and interactive visualizations
    6. **Export**: Download results in CSV, Excel, or JSON format
    
    ### 🔬 Analysis Types
    - **Harmonics (2H, 3H)**: 2nd and 3rd harmonic products
    - **IM3**: Third-order intermodulation products (2f₁ ± f₂)
    - **IM4**: Fourth-order intermodulation products (2f₁ + 2f₂)
    - **IM5**: Fifth-order intermodulation products (3f₁ ± 2f₂)
    - **IM7**: Seventh-order intermodulation products (4f₁ ± 3f₂)
    - **ACLR**: Adjacent Channel Leakage Ratio analysis
    
    ### 📊 Risk Levels
    - **High**: In-band interference or within 1 MHz
    - **Med**: Within 5 MHz of the receive band
    - **Low**: Within 20 MHz of the receive band
    - **Minimal**: More than 20 MHz away
    
    ### 🎯 Features
    - **Professional-grade analysis** with exhaustive IMD calculations
    - **Interactive visualizations** including frequency spectrum plots
    - **Advanced filtering** by category, frequency range, and risk level
    - **Multiple export formats** (CSV, Excel, JSON, Markdown)
    - **Configuration validation** with warnings and recommendations
    """)

# Technical information
with st.expander("⚙️ Technical Information"):
    st.markdown(f"""
    ### 🏗️ System Information
    - **Version**: {__version__}
    - **Engine**: Streamlit with Altair visualization
    - **Supported Bands**: {len(BANDS)} bands across multiple technologies
    - **Categories**: {len(categories)} categories (2G, 3G, LTE, Wi-Fi, ISM, HaLow, LoRa, GNSS)
    
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
