"""
Tests for calculator.py — product generation, risk assessment, desensitization.
Refs GH #10, #11: technology-dependent thresholds, frequency-only risk for GNSS.
"""
import math
import pytest
from bands import Band, BANDS
from calculator import (
    calculate_all_products,
    assess_risk_severity,
    assess_risk_severity_quantitative,
    calculate_desensitization,
)


# ============================================================
# calculate_all_products
# ============================================================

class TestCalculateAllProducts:
    """Core product generation tests."""

    def test_returns_results_and_alerts(self, two_band_selection):
        results, alerts = calculate_all_products(two_band_selection)
        assert isinstance(results, list)
        assert isinstance(alerts, list)

    def test_products_have_required_keys(self, two_band_selection):
        results, _ = calculate_all_products(two_band_selection)
        required_keys = {'Type', 'Product_Subtype', 'Formula', 'Frequency_MHz',
                         'Aggressors', 'Victims', 'Risk', 'Severity', 'Details'}
        for r in results[:5]:
            assert required_keys.issubset(r.keys()), f"Missing keys: {required_keys - r.keys()}"

    def test_no_products_from_receive_only_bands(self):
        """GNSS is receive-only — should not generate TX harmonics."""
        gnss = BANDS['GNSS_L1']
        results, _ = calculate_all_products([gnss])
        tx_products = [r for r in results if r['Aggressors'] == 'GNSS_L1']
        assert len(tx_products) == 0, "GNSS should not generate TX products"

    def test_lte_b13_generates_harmonics(self):
        b13 = BANDS['LTE_B13']
        results, _ = calculate_all_products([b13, BANDS['GNSS_L1']])
        harmonics = [r for r in results if r['Type'] in ('2H', '3H', '4H', '5H')
                     and r['Aggressors'] == 'LTE_B13']
        assert len(harmonics) > 0

    def test_2h_frequency_calculation(self):
        """2H of LTE B13 TX (777-787 MHz) = 1554-1574 MHz."""
        b13 = BANDS['LTE_B13']
        results, _ = calculate_all_products([b13, BANDS['GNSS_L1']])
        h2_products = [r for r in results if r['Type'] == '2H' and r['Aggressors'] == 'LTE_B13']
        freqs = {r['Frequency_MHz'] for r in h2_products}
        assert 1554.0 in freqs  # 2 * 777
        assert 1574.0 in freqs  # 2 * 787

    def test_imd_products_generated_for_two_tx_bands(self):
        """Two TX bands should generate IM3 products."""
        lte = BANDS['LTE_B3']
        wifi = BANDS['WiFi_2G']
        results, _ = calculate_all_products([lte, wifi])
        im3_products = [r for r in results if r['Type'] == 'IM3']
        assert len(im3_products) > 0

    def test_guard_band_widens_victim_range(self):
        """Products near victim band edge should be caught with guard band."""
        b13 = BANDS['LTE_B13']
        gnss = BANDS['GNSS_L1']
        results_no_guard, _ = calculate_all_products([b13, gnss], guard=0.0)
        results_with_guard, _ = calculate_all_products([b13, gnss], guard=10.0)
        victims_no_guard = [r for r in results_no_guard if r['Victims']]
        victims_with_guard = [r for r in results_with_guard if r['Victims']]
        assert len(victims_with_guard) >= len(victims_no_guard)

    def test_imd2_can_be_disabled(self):
        lte = BANDS['LTE_B3']
        wifi = BANDS['WiFi_2G']
        results_with, _ = calculate_all_products([lte, wifi], imd2=True)
        results_without, _ = calculate_all_products([lte, wifi], imd2=False)
        im2_with = [r for r in results_with if r['Type'] == 'IM2']
        im2_without = [r for r in results_without if r['Type'] == 'IM2']
        assert len(im2_with) > 0
        assert len(im2_without) == 0

    def test_empty_band_list(self):
        results, alerts = calculate_all_products([])
        assert results == []
        assert alerts == []

    def test_single_band_no_imd(self):
        """Single band can't produce IMD products (needs pairs)."""
        results, _ = calculate_all_products([BANDS['LTE_B3']])
        imd_products = [r for r in results if r['Type'].startswith('IM')]
        assert len(imd_products) == 0


# ============================================================
# assess_risk_severity (frequency-only)
# ============================================================

class TestAssessRiskSeverity:
    """Frequency-only risk assessment."""

    def test_gnss_victim_gets_high_severity(self):
        """GH #11: GNSS victims should get severity >= 3 for in-band products."""
        symbol, severity = assess_risk_severity(
            frequency=1575.42,  # GPS L1 center
            victim_code='GNSS_L1',
            aggressors='LTE_B13',
            product_type='2H'
        )
        assert severity >= 3, f"GNSS in-band product should be severity >= 3, got {severity}"

    def test_gnss_l1_is_critical(self):
        """GPS L1 interference should be critical (severity 5)."""
        symbol, severity = assess_risk_severity(
            frequency=1575.42,
            victim_code='GNSS_L1',
            aggressors='LTE_B3',
            product_type='3H'
        )
        assert severity == 5
        assert symbol == '🔴'

    def test_lte_victim_lower_severity_than_gnss(self):
        """LTE victims should generally have lower severity than GNSS."""
        _, gnss_sev = assess_risk_severity(1575.42, 'GNSS_L1', 'LTE_B3', '2H')
        _, lte_sev = assess_risk_severity(2140.0, 'LTE_B1', 'LTE_B3', '2H')
        assert gnss_sev >= lte_sev

    def test_severity_range(self):
        """Severity should always be 1-5."""
        for freq, vic, agg, pt in [
            (1575.42, 'GNSS_L1', 'LTE_B13', '2H'),
            (2450.0, 'WiFi_2G', 'LTE_B3', 'IM3'),
            (900.0, 'LTE_B8', 'WiFi_2G', '3H'),
        ]:
            _, severity = assess_risk_severity(freq, vic, agg, pt)
            assert 1 <= severity <= 5, f"Severity {severity} out of range for {vic}"

    def test_risk_symbol_matches_severity(self):
        """Symbol should correspond to severity level."""
        symbol_map = {5: '🔴', 4: '🟠', 3: '🟡', 2: '🔵', 1: '✅'}
        for freq, vic, agg, pt in [
            (1575.42, 'GNSS_L1', 'LTE_B13', '2H'),
            (2450.0, 'WiFi_2G', 'LTE_B3', 'IM5'),
        ]:
            symbol, severity = assess_risk_severity(freq, vic, agg, pt)
            if severity in symbol_map:
                assert symbol == symbol_map[severity], (
                    f"Symbol {symbol} doesn't match severity {severity}"
                )

    def test_public_safety_bands_elevated(self):
        """LTE B13/B14 aggressors should boost severity."""
        _, sev_b13 = assess_risk_severity(750.0, 'LTE_B13', 'LTE_B13', '2H')
        assert sev_b13 >= 4


# ============================================================
# assess_risk_severity_quantitative
# ============================================================

class TestAssessRiskSeverityQuantitative:
    """Power-based risk assessment with technology-dependent thresholds."""

    def test_gnss_8db_is_critical(self):
        """GNSS: >= 8 dB desensitization should be critical."""
        symbol, severity, reason = assess_risk_severity_quantitative(
            interference_power_dbm=-140.0,
            victim_sensitivity_dbm=-150.0,
            desensitization_db=8.0,
            victim_code='GNSS_L1',
            product_type='2H'
        )
        assert symbol == '🔴'
        assert severity == 5

    def test_gnss_3db_is_high(self):
        """GNSS: >= 3 dB desensitization should be high."""
        symbol, severity, reason = assess_risk_severity_quantitative(
            interference_power_dbm=-145.0,
            victim_sensitivity_dbm=-150.0,
            desensitization_db=3.0,
            victim_code='GNSS_L1',
            product_type='2H'
        )
        assert symbol == '🟠'
        assert severity == 4

    def test_gnss_1db_is_medium(self):
        symbol, severity, _ = assess_risk_severity_quantitative(
            -148.0, -150.0, 1.0, 'GNSS_L1', '2H')
        assert symbol == '🟡'
        assert severity == 3

    def test_gnss_below_half_db_is_safe(self):
        symbol, severity, _ = assess_risk_severity_quantitative(
            -160.0, -150.0, 0.1, 'GNSS_L1', '2H')
        assert symbol == '✅'
        assert severity == 1

    def test_standard_wireless_12db_is_critical(self):
        """Standard wireless: >= 12 dB should be critical."""
        symbol, severity, _ = assess_risk_severity_quantitative(
            -80.0, -105.0, 12.0, 'LTE_B3', 'IM3')
        assert symbol == '🔴'
        assert severity == 5

    def test_standard_wireless_6db_is_high(self):
        symbol, severity, _ = assess_risk_severity_quantitative(
            -90.0, -105.0, 6.0, 'LTE_B3', 'IM3')
        assert symbol == '🟠'
        assert severity == 4

    def test_standard_wireless_below_1db_is_safe(self):
        symbol, severity, _ = assess_risk_severity_quantitative(
            -115.0, -105.0, 0.5, 'LTE_B3', 'IM3')
        assert symbol == '✅'
        assert severity == 1

    def test_public_safety_6db_is_critical(self):
        """Public safety bands have stricter thresholds."""
        symbol, severity, _ = assess_risk_severity_quantitative(
            -80.0, -105.0, 6.0, 'LTE_B13', 'IM3')
        assert symbol == '🔴'
        assert severity == 5

    def test_reason_string_contains_desense(self):
        """Reason should mention desensitization value."""
        _, _, reason = assess_risk_severity_quantitative(
            -80.0, -105.0, 10.0, 'LTE_B3', 'IM3')
        assert '10.0' in reason

    def test_returns_three_elements(self):
        result = assess_risk_severity_quantitative(-100.0, -105.0, 1.0, 'LTE_B1', '2H')
        assert len(result) == 3


# ============================================================
# calculate_desensitization
# ============================================================

class TestCalculateDesensitization:
    """I/N method desensitization calculation."""

    def test_equal_interference_and_noise(self):
        """I = N => desense = 10*log10(2) = 3.01 dB."""
        desens = calculate_desensitization(-100.0, -100.0)
        assert abs(desens - 3.01) < 0.1

    def test_interference_10db_above_noise(self):
        """I = N + 10 dB => desense = 10*log10(1 + 10) = 10.41 dB."""
        desens = calculate_desensitization(-90.0, -100.0)
        assert abs(desens - 10.41) < 0.1

    def test_interference_20db_below_noise_is_negligible(self):
        """I <= N - 20 dB => negligible (0.0 dB)."""
        desens = calculate_desensitization(-120.0, -100.0)
        assert desens == 0.0

    def test_interference_just_above_negligible_threshold(self):
        """I = N - 19 dB => small but non-zero desensitization."""
        desens = calculate_desensitization(-119.0, -100.0)
        assert desens > 0.0

    def test_very_strong_interference(self):
        """Very strong interference should give large desensitization."""
        desens = calculate_desensitization(-70.0, -100.0)
        assert desens > 25.0  # ~30 dB

    def test_desensitization_is_non_negative(self):
        """Desensitization should never be negative."""
        for intf in [-200, -150, -120, -100, -80, -50]:
            desens = calculate_desensitization(float(intf), -100.0)
            assert desens >= 0.0, f"Negative desens at interference={intf}"

    def test_monotonically_increasing(self):
        """Higher interference should give higher desensitization."""
        prev = 0.0
        for intf in [-119, -110, -100, -90, -80]:
            desens = calculate_desensitization(float(intf), -100.0)
            assert desens >= prev, f"Not monotonic at {intf}"
            prev = desens


# ============================================================
# Technology-dependent thresholds (GH #10)
# ============================================================

class TestTechnologyThresholds:
    """GH #10: Technology-dependent thresholds."""

    def test_wifi_6db_is_critical(self):
        """WiFi should use stricter thresholds than LTE."""
        symbol, severity, _ = assess_risk_severity_quantitative(
            -80.0, -85.0, 6.0, 'WiFi_2G', 'IM3')
        assert symbol == '🔴', f"WiFi 6dB desense should be Critical, got {symbol}"

    def test_ble_6db_is_critical(self):
        symbol, severity, _ = assess_risk_severity_quantitative(
            -80.0, -95.0, 6.0, 'BLE', 'IM3')
        assert symbol == '🔴'

    def test_lora_3db_is_critical(self):
        """LoRa has very strict thresholds."""
        symbol, severity, _ = assess_risk_severity_quantitative(
            -80.0, -140.0, 3.0, 'LoRa_US', 'IM3')
        assert symbol == '🔴'

    def test_lte_6db_is_still_high_not_critical(self):
        """LTE should keep 12/6/3/1 thresholds."""
        symbol, severity, _ = assess_risk_severity_quantitative(
            -80.0, -105.0, 6.0, 'LTE_B3', 'IM3')
        assert symbol == '🟠'  # High, not Critical

    def test_nr_uses_same_thresholds_as_lte(self):
        symbol, severity, _ = assess_risk_severity_quantitative(
            -80.0, -105.0, 6.0, 'NR_n77', 'IM3')
        assert symbol == '🟠'


# ============================================================
# GH #29: 3-tone IMD products
# ============================================================

class TestThreeToneIMD:
    """GH #29: 3-tone IMD products."""

    def test_3tone_disabled_by_default(self):
        results, _ = calculate_all_products([BANDS['LTE_B3'], BANDS['WiFi_2G'], BANDS['BLE']])
        im3_3t = [r for r in results if r['Type'] == 'IM3-3T']
        assert len(im3_3t) == 0

    def test_3tone_enabled_generates_products(self):
        results, _ = calculate_all_products(
            [BANDS['LTE_B3'], BANDS['WiFi_2G'], BANDS['BLE']],
            include_3tone=True
        )
        im3_3t = [r for r in results if r['Type'] == 'IM3-3T']
        assert len(im3_3t) > 0, "Should generate 3-tone IM3 products"

    def test_3tone_product_has_three_aggressors(self):
        results, _ = calculate_all_products(
            [BANDS['LTE_B3'], BANDS['WiFi_2G'], BANDS['BLE']],
            include_3tone=True
        )
        im3_3t = [r for r in results if r['Type'] == 'IM3-3T']
        if im3_3t:
            aggressors = im3_3t[0]['Aggressors']
            assert aggressors.count(',') == 2, "Should have 3 aggressors"

    def test_3tone_skipped_for_many_bands(self):
        """More than 6 bands should skip 3-tone to avoid combinatorial explosion."""
        bands = [BANDS['LTE_B1'], BANDS['LTE_B3'], BANDS['LTE_B7'],
                 BANDS['LTE_B13'], BANDS['WiFi_2G'], BANDS['BLE'], BANDS['GNSS_L1']]
        results, _ = calculate_all_products(bands, include_3tone=True)
        im3_3t = [r for r in results if r['Type'] == 'IM3-3T']
        assert len(im3_3t) == 0, "Should skip 3-tone when > 6 bands"

    def test_3tone_positive_frequency_only(self):
        """All 3-tone products should have positive frequency."""
        results, _ = calculate_all_products(
            [BANDS['LTE_B3'], BANDS['WiFi_2G'], BANDS['BLE']],
            include_3tone=True
        )
        im3_3t = [r for r in results if r['Type'] == 'IM3-3T']
        for p in im3_3t:
            assert p['Frequency_MHz'] > 0
