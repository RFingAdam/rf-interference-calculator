#!/usr/bin/env python3
"""
Critical RF Interference Examples Script
Demonstrates the key interference scenarios for screenshots and documentation
"""

from bands import BANDS
from calculator import calculate_all_products
import pandas as pd

def analyze_scenario(name, bands, description):
    """Analyze a specific interference scenario"""
    print(f"\n{'='*60}")
    print(f"📡 {name}")
    print(f"{'='*60}")
    print(f"Description: {description}")
    print(f"Bands: {[b.code for b in bands]}")
    
    # Run calculation
    results, alerts = calculate_all_products(bands, guard=1.0, imd2=True, imd4=False, imd5=True, imd7=False)
    df = pd.DataFrame(results)
    
    if df.empty:
        print("❌ No results generated")
        return
    
    # Filter for critical risks only
    critical_df = df[df['Severity'] >= 4].sort_values('Severity', ascending=False)
    
    print(f"📊 Total products: {len(df)}")
    print(f"🔴 Critical/High risks: {len(critical_df)}")
    
    if not critical_df.empty:
        print(f"\n🚨 CRITICAL INTERFERENCE DETECTED:")
        for idx, row in critical_df.head(10).iterrows():
            risk_emoji = row['Risk']
            severity = row['Severity'] 
            freq = row['Frequency_MHz']
            product_type = row['Type']
            formula = row['Formula']
            aggressors = row['Aggressors']
            victims = row['Victims']
            
            print(f"   {risk_emoji} {product_type} @ {freq:.1f} MHz (Sev: {severity})")
            print(f"      Formula: {formula}")
            print(f"      {aggressors} → {victims}")
    
    # Show frequency range
    freq_min = df['Frequency_MHz'].min()
    freq_max = df['Frequency_MHz'].max()
    print(f"\n📡 Frequency range: {freq_min:.1f} - {freq_max:.1f} MHz")
    
    return critical_df

def main():
    print("🧪 RF Interference Critical Scenarios Analysis")
    print("=" * 60)
    print("This script demonstrates the critical interference cases mentioned in documentation")
    print("Run with: python demo_critical_scenarios.py")
    print("Use results to configure UI for professional screenshots\n")
    
    # Scenario 1: LTE Band 13 → GPS L1 (2nd Harmonic)
    scenario1_bands = [BANDS['LTE_B13'], BANDS['GNSS_L1']]
    scenario1_critical = analyze_scenario(
        "LTE Band 13 2nd Harmonic → GPS L1 Interference",
        scenario1_bands,
        "LTE B13 (777-787 MHz) 2nd harmonic interferes with GPS L1 (1575.42 MHz)"
    )
    
    # Scenario 2: LTE Band 4 → Wi-Fi 5G (3rd Harmonic) 
    scenario2_bands = [BANDS['LTE_B4'], BANDS['WiFi_5G']]
    scenario2_critical = analyze_scenario(
        "LTE Band 4 3rd Harmonic → Wi-Fi 5G Interference",
        scenario2_bands,
        "LTE B4 (1710-1755 MHz) 3rd harmonic interferes with Wi-Fi 5G (5150-5925 MHz)"
    )
    
    # Scenario 3: LTE Band 26 → Wi-Fi 2.4G/BLE (3rd Harmonic)
    scenario3_bands = [BANDS['LTE_B26'], BANDS['WiFi_2G'], BANDS['BLE']]
    scenario3_critical = analyze_scenario(
        "LTE Band 26 3rd Harmonic → Wi-Fi 2.4G/BLE Interference", 
        scenario3_bands,
        "LTE B26 (814-849 MHz) 3rd harmonic interferes with ISM band (2400-2500 MHz)"
    )
    
    # Scenario 4: Multi-LTE IM3 → BLE (Coexistence Critical)
    scenario4_bands = [BANDS['LTE_B13'], BANDS['LTE_B26'], BANDS['BLE']]
    scenario4_critical = analyze_scenario(
        "Multi-LTE IM3 → BLE Coexistence Critical",
        scenario4_bands, 
        "Multiple LTE bands creating IM3 products hitting BLE (2402-2480 MHz)"
    )
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 SUMMARY OF CRITICAL SCENARIOS")
    print(f"{'='*60}")
    
    total_critical = 0
    if scenario1_critical is not None:
        s1_count = len(scenario1_critical)
        total_critical += s1_count
        print(f"1. GPS Interference: {s1_count} critical products (Navigation impact)")
    
    if scenario2_critical is not None:
        s2_count = len(scenario2_critical) 
        total_critical += s2_count
        print(f"2. Wi-Fi 5G Interference: {s2_count} critical products (Channel impact)")
    
    if scenario3_critical is not None:
        s3_count = len(scenario3_critical)
        total_critical += s3_count
        print(f"3. ISM Band Interference: {s3_count} critical products (Coexistence impact)")
    
    if scenario4_critical is not None:
        s4_count = len(scenario4_critical)
        total_critical += s4_count 
        print(f"4. BLE Coexistence: {s4_count} critical products (PTA/WCI-2 required)")
    
    print(f"\n🔴 TOTAL CRITICAL INTERFERENCE PRODUCTS: {total_critical}")
    print("🚨 These scenarios require immediate attention and coordination protocols")
    
    print(f"\n✅ Analysis complete! Use these scenarios for:")
    print("   • Screenshot generation in the UI (streamlit run ui.py)")
    print("   • Documentation examples")
    print("   • Training materials") 
    print("   • Regulatory compliance reports")

if __name__ == "__main__":
    main()
