"""
Tests for constants.py — risk level consistency across all dicts.
Refs GH #8: RISK_PIE_COLOR_MAP 'Negligible' key mismatch.
"""
from constants import (
    RISK_LEVELS, RISK_EMOJI_TO_NAME, RISK_SORT_ORDER,
    RISK_STYLES, RISK_COLOR_DOMAIN, RISK_COLOR_RANGE,
    RISK_EMOJI_DOMAIN, RISK_EMOJI_COLOR_RANGE,
    RISK_PIE_COLOR_MAP, PRODUCT_TYPE_COLORS, VERSION,
)


class TestRiskLevelConsistency:
    """All risk dicts must use consistent key sets."""

    def test_risk_levels_has_five_levels(self):
        assert len(RISK_LEVELS) == 5

    def test_risk_emoji_to_name_covers_all_emojis(self):
        emojis_from_levels = {v[0] for v in RISK_LEVELS.values()}
        assert set(RISK_EMOJI_TO_NAME.keys()) == emojis_from_levels

    def test_risk_sort_order_covers_all_emojis(self):
        emojis_from_levels = {v[0] for v in RISK_LEVELS.values()}
        assert set(RISK_SORT_ORDER.keys()) == emojis_from_levels

    def test_risk_styles_covers_all_emojis(self):
        emojis_from_levels = {v[0] for v in RISK_LEVELS.values()}
        assert set(RISK_STYLES.keys()) == emojis_from_levels

    def test_risk_color_domain_matches_level_names(self):
        names_from_levels = {v[1] for v in RISK_LEVELS.values()}
        assert set(RISK_COLOR_DOMAIN) == names_from_levels

    def test_risk_color_range_length_matches_domain(self):
        assert len(RISK_COLOR_RANGE) == len(RISK_COLOR_DOMAIN)

    def test_risk_emoji_domain_matches_emojis(self):
        emojis_from_levels = {v[0] for v in RISK_LEVELS.values()}
        assert set(RISK_EMOJI_DOMAIN) == emojis_from_levels

    def test_risk_emoji_color_range_length(self):
        assert len(RISK_EMOJI_COLOR_RANGE) == len(RISK_EMOJI_DOMAIN)

    def test_risk_pie_color_map_keys_match_level_names(self):
        """GH #8: RISK_PIE_COLOR_MAP must use same names as RISK_COLOR_DOMAIN."""
        expected_names = set(RISK_COLOR_DOMAIN)
        actual_names = set(RISK_PIE_COLOR_MAP.keys())
        assert actual_names == expected_names, (
            f"RISK_PIE_COLOR_MAP keys {actual_names} don't match "
            f"RISK_COLOR_DOMAIN {expected_names}. "
            f"Missing: {expected_names - actual_names}, "
            f"Extra: {actual_names - expected_names}"
        )


class TestProductTypeColors:
    def test_has_all_harmonic_orders(self):
        for h in ['2H', '3H', '4H', '5H']:
            assert h in PRODUCT_TYPE_COLORS

    def test_has_all_imd_orders(self):
        for im in ['IM2', 'IM3', 'IM4', 'IM5', 'IM7']:
            assert im in PRODUCT_TYPE_COLORS

    def test_colors_are_valid_hex(self):
        import re
        for key, color in PRODUCT_TYPE_COLORS.items():
            assert re.match(r'^#[0-9a-fA-F]{6}$', color), f"{key}: {color} is not valid hex"


class TestTechnologyRiskThresholds:
    def test_all_technologies_have_four_levels(self):
        from constants import TECHNOLOGY_RISK_THRESHOLDS
        for tech, thresholds in TECHNOLOGY_RISK_THRESHOLDS.items():
            assert set(thresholds.keys()) == {'critical', 'high', 'medium', 'low'}, \
                f"{tech} missing threshold levels"

    def test_thresholds_are_descending(self):
        from constants import TECHNOLOGY_RISK_THRESHOLDS
        for tech, t in TECHNOLOGY_RISK_THRESHOLDS.items():
            assert t['critical'] > t['high'] > t['medium'] > t['low'], \
                f"{tech} thresholds not in descending order"

    def test_gnss_lookup(self):
        from constants import get_technology_thresholds
        t = get_technology_thresholds('GNSS_L1')
        assert t['critical'] == 8.0

    def test_wifi_lookup(self):
        from constants import get_technology_thresholds
        t = get_technology_thresholds('WiFi_2G')
        assert t['critical'] == 6.0

    def test_lora_lookup(self):
        from constants import get_technology_thresholds
        t = get_technology_thresholds('LoRa_US')
        assert t['critical'] == 3.0

    def test_default_fallback(self):
        from constants import get_technology_thresholds
        t = get_technology_thresholds('UNKNOWN_BAND')
        assert t['critical'] == 12.0


class TestVersion:
    def test_version_format(self):
        parts = VERSION.split('.')
        assert len(parts) == 3
        for p in parts:
            assert p.isdigit()
