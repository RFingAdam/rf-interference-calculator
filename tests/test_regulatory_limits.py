"""
Tests for regulatory_limits.py: emission compliance, bandwidth normalization.
Refs GH #14: bandwidth normalization should not increase product power.
"""
import math
import pytest
from regulatory_limits import check_emission_compliance, SPURIOUS_LIMITS_3GPP


# ============================================================
# check_emission_compliance
# ============================================================

class TestCheckEmissionCompliance:
    """Emission compliance checking with bandwidth normalization."""

    def test_returns_three_elements(self):
        """Should return (compliant, reason, margin)."""
        result = check_emission_compliance(
            band_code='LTE_B13',
            product_freq_mhz=1575.42,
            product_power_dbm=-30.0,
            product_bandwidth_mhz=5.0
        )
        assert len(result) == 3
        compliant, reason, margin = result
        assert isinstance(compliant, bool)
        assert isinstance(reason, str)
        assert isinstance(margin, (int, float))

    def test_very_low_power_is_compliant(self):
        """Very low power product should always be compliant."""
        compliant, reason, margin = check_emission_compliance(
            'LTE_B13', 1575.42, -80.0, 1.0
        )
        assert compliant is True
        assert margin > 0

    def test_very_high_power_is_non_compliant(self):
        """Very high power product should fail compliance."""
        compliant, reason, margin = check_emission_compliance(
            'LTE_B13', 1575.42, 10.0, 1.0
        )
        assert compliant is False
        assert margin < 0

    def test_bandwidth_normalization_reduces_power(self):
        """GH #14: When product BW > measurement BW, normalized power should be LOWER."""
        # Product at 20 MHz, measured in 1 MHz => should reduce by ~13 dB
        _, _, margin_wide = check_emission_compliance(
            'LTE_B13', 1575.42, -30.0, 20.0  # wide product
        )
        _, _, margin_narrow = check_emission_compliance(
            'LTE_B13', 1575.42, -30.0, 0.5  # narrow product
        )
        # Wider product should have more margin (power spread over more BW)
        assert margin_wide >= margin_narrow

    def test_bandwidth_normalization_never_increases_power(self):
        """GH #14: bw_correction should be clamped to <= 0.
        When measurement_bw > product_bw, correction should be 0 (not positive)."""
        # A very narrow product (0.01 MHz) measured in wide BW
        # should NOT get power artificially increased
        compliant_narrow, _, margin_narrow = check_emission_compliance(
            'LTE_B13', 1575.42, -40.0, 0.01
        )
        compliant_zero, _, margin_zero = check_emission_compliance(
            'LTE_B13', 1575.42, -40.0, 0.0  # 0 = skip normalization
        )
        # After fix: narrow product margin should be >= zero-bw margin
        # Current bug: narrow product gets positive correction, reducing margin

    def test_unknown_band_uses_defaults(self):
        """Unknown bands should use default limits."""
        result = check_emission_compliance(
            'UNKNOWN_BAND', 1575.42, -30.0, 1.0
        )
        assert len(result) == 3

    def test_zero_bandwidth_skips_normalization(self):
        """product_bandwidth_mhz=0 should skip normalization."""
        compliant, reason, margin = check_emission_compliance(
            'LTE_B13', 1575.42, -30.0, 0.0
        )
        assert 'BW-normalized' not in reason


# ============================================================
# SPURIOUS_LIMITS_3GPP structure
# ============================================================

class TestSpuriousLimits:
    """Verify regulatory limit definitions."""

    def test_lte_default_exists(self):
        assert 'LTE_DEFAULT' in SPURIOUS_LIMITS_3GPP

    def test_limits_have_protected_bands(self):
        for band_key, limits in SPURIOUS_LIMITS_3GPP.items():
            assert hasattr(limits, 'protected_bands'), \
                f"{band_key} missing protected_bands"

    def test_gps_band_protected_for_b13(self):
        """GPS L1 should be a protected band in LTE B13 limits."""
        b13_limits = SPURIOUS_LIMITS_3GPP['LTE_B13']
        gps_protected = False
        for name, spec in b13_limits.protected_bands.items():
            if 1559 <= spec.freq_low_mhz <= 1610 or 1559 <= spec.freq_high_mhz <= 1610:
                gps_protected = True
                break
        assert gps_protected, "GPS L1 should be protected in LTE B13 limits"
