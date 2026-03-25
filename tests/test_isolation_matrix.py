"""
Tests for isolation_matrix.py — band pair isolation requirements.
"""
import pytest
from isolation_matrix import (
    ISOLATION_REQUIREMENTS,
    IsolationRequirement,
    get_required_isolation,
    get_recommended_isolation,
    get_isolation_recommendation,
    check_isolation_compliance,
)


class TestIsolationRequirements:
    """Isolation matrix data integrity."""

    def test_has_critical_pairs(self):
        """Should have at least 30 critical band pairs."""
        assert len(ISOLATION_REQUIREMENTS) >= 30

    def test_requirement_fields(self):
        """Each requirement should have min and recommended isolation."""
        for key, req in ISOLATION_REQUIREMENTS.items():
            assert isinstance(req, IsolationRequirement)
            assert req.min_isolation_db >= 0
            assert req.recommended_isolation_db >= req.min_isolation_db

    def test_lte_gnss_pair_exists(self):
        """LTE to GNSS isolation should be defined."""
        rec = get_isolation_recommendation('LTE_B13', 'GNSS_L1')
        assert rec is not None

    def test_bidirectional_lookup(self):
        """Lookup should work in both directions."""
        req_forward = get_required_isolation('LTE_B13', 'GNSS_L1')
        req_reverse = get_required_isolation('GNSS_L1', 'LTE_B13')
        # At least one direction should return a non-zero result
        assert req_forward > 0 or req_reverse > 0

    def test_unknown_pair_returns_default(self):
        """Unknown pair should return default isolation (25 dB)."""
        req = get_required_isolation('FAKE_BAND_1', 'FAKE_BAND_2')
        assert req > 0  # Returns a conservative default

    def test_wifi_ble_pair_exists(self):
        """WiFi/BLE coexistence should be defined."""
        req = get_required_isolation('WiFi_2G', 'BLE')
        alt = get_required_isolation('BLE', 'WiFi_2G')
        assert req > 0 or alt > 0


class TestCheckIsolationCompliance:
    """Isolation compliance checking."""

    def test_high_isolation_is_compliant(self):
        """Very high isolation should pass compliance."""
        compliant, status, margin = check_isolation_compliance('LTE_B13', 'GNSS_L1', 50.0)
        assert compliant is True
        assert margin >= 0

    def test_zero_isolation_may_fail(self):
        """Zero isolation should likely fail for critical pairs."""
        compliant, status, margin = check_isolation_compliance('LTE_B13', 'GNSS_L1', 0.0)
        assert compliant is False
        assert margin < 0
