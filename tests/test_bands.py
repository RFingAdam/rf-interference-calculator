"""
Tests for bands.py: band definitions, frequency accuracy.
"""
import pytest
from bands import Band, BAND_LIST, BANDS


class TestBandDefinitions:
    """Verify band data integrity."""

    def test_band_count(self):
        """Should have 85 bands per project spec."""
        assert len(BAND_LIST) == 85

    def test_bands_dict_matches_list(self):
        assert len(BANDS) == len(BAND_LIST)
        for b in BAND_LIST:
            assert b.code in BANDS
            assert BANDS[b.code] is b

    def test_all_bands_have_required_fields(self):
        for b in BAND_LIST:
            assert isinstance(b.code, str) and len(b.code) > 0
            assert isinstance(b.tx_low, (int, float))
            assert isinstance(b.tx_high, (int, float))
            assert isinstance(b.rx_low, (int, float))
            assert isinstance(b.rx_high, (int, float))
            assert isinstance(b.label, str)
            assert isinstance(b.category, str)

    def test_rx_range_valid(self):
        """RX low should be <= RX high for all bands."""
        for b in BAND_LIST:
            assert b.rx_low <= b.rx_high, f"{b.code}: rx_low {b.rx_low} > rx_high {b.rx_high}"

    def test_tx_range_valid(self):
        """TX low should be <= TX high (or both 0 for receive-only)."""
        for b in BAND_LIST:
            if b.tx_low == 0 and b.tx_high == 0:
                continue  # receive-only
            assert b.tx_low <= b.tx_high, f"{b.code}: tx_low {b.tx_low} > tx_high {b.tx_high}"

    def test_gnss_bands_are_receive_only(self):
        """GNSS bands should have tx_low = tx_high = 0."""
        for code in ['GNSS_L1', 'GNSS_L2', 'GNSS_L5']:
            b = BANDS[code]
            assert b.tx_low == 0 and b.tx_high == 0, f"{code} should be receive-only"

    def test_tdd_bands_have_same_tx_rx(self):
        """TDD bands should have tx == rx ranges."""
        tdd_bands = [b for b in BAND_LIST if 'TDD' in b.label]
        for b in tdd_bands:
            assert b.tx_low == b.rx_low, f"{b.code}: TDD tx_low != rx_low"
            assert b.tx_high == b.rx_high, f"{b.code}: TDD tx_high != rx_high"

    def test_unique_codes(self):
        """All band codes should be unique."""
        codes = [b.code for b in BAND_LIST]
        assert len(codes) == len(set(codes))

    def test_known_lte_b13_frequencies(self):
        """LTE B13: TX 777-787, RX 746-756."""
        b13 = BANDS['LTE_B13']
        assert b13.tx_low == 777
        assert b13.tx_high == 787
        assert b13.rx_low == 746
        assert b13.rx_high == 756

    def test_known_gnss_l1_frequencies(self):
        """GNSS L1: RX 1559-1606 MHz."""
        gnss = BANDS['GNSS_L1']
        assert gnss.rx_low == 1559
        assert gnss.rx_high == 1606

    def test_category_coverage(self):
        """Should cover all expected technology categories."""
        categories = {b.category for b in BAND_LIST}
        expected = {'LTE', '5G NR', 'Wi-Fi', 'BLE', 'GNSS', 'LoRa', 'HaLow'}
        for cat in expected:
            assert cat in categories, f"Missing category: {cat}"

    def test_nr_bands_have_correct_prefix(self):
        """5G NR bands should have NR_n prefix."""
        nr_bands = [b for b in BAND_LIST if b.category == '5G NR']
        for b in nr_bands:
            assert b.code.startswith('NR_n'), f"{b.code} should start with NR_n"
        assert len(nr_bands) == 14

    def test_sdl_band_is_receive_only(self):
        """LTE B29 and B32 are SDL (downlink-only)."""
        b29 = BANDS['LTE_B29']
        assert b29.tx_low == 0 and b29.tx_high == 0
        b32 = BANDS['LTE_B32']
        assert b32.tx_low == 0 and b32.tx_high == 0

    def test_frequencies_are_positive_or_zero(self):
        for b in BAND_LIST:
            assert b.tx_low >= 0
            assert b.tx_high >= 0
            assert b.rx_low >= 0
            assert b.rx_high >= 0
