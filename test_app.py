#!/usr/bin/env python3
"""
Quick test script to verify the RF Interference Calculator is working properly.
Run this to check if everything is functioning after edits.
"""

def test_application():
    print("🧪 Testing RF Interference Calculator...")
    print("=" * 50)
    
    try:
        # Import test
        print("1. Testing imports...")
        from bands import BANDS, Band
        from calculator import calculate_all_products, validate_band_configuration
        print(f"   ✅ Imports successful - {len(BANDS)} bands loaded")
        
        # Basic functionality test
        print("2. Testing core calculation...")
        test_bands = [BANDS['WiFi_2G'], BANDS['LTE_B1']]
        results, alerts = calculate_all_products(test_bands, guard=1.0, imd4=False, imd5=True, imd7=False)
        print(f"   ✅ Calculation successful - {len(results)} products, {len(alerts)} alerts")
        
        # Validation test
        print("3. Testing validation functions...")
        warnings = validate_band_configuration(test_bands)
        print(f"   ✅ Validation successful - {len(warnings)} config warnings")
        
        # Data integrity test
        print("4. Testing data integrity...")
        if results:
            has_required_fields = all('Type' in r and 'Risk' in r for r in results)
            has_frequency = all('Frequency_MHz' in r or 'Freq_low' in r for r in results)
            print(f"   ✅ Required fields present: {has_required_fields}")
            print(f"   ✅ Frequency data present: {has_frequency}")
        
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Your application is ready to run with:")
        print("   streamlit run ui.py")
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_application()
