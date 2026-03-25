"""
Shared fixtures for RF Interference Calculator tests.
"""
import pytest
from bands import Band, BANDS, BAND_LIST
from rf_performance import SystemParameters


@pytest.fixture
def default_params():
    """Default SystemParameters for testing."""
    return SystemParameters()


@pytest.fixture
def gnss_l1_band():
    return BANDS['GNSS_L1']


@pytest.fixture
def lte_b13_band():
    return BANDS['LTE_B13']


@pytest.fixture
def lte_b3_band():
    return BANDS['LTE_B3']


@pytest.fixture
def wifi_2g_band():
    return BANDS['WiFi_2G']


@pytest.fixture
def ble_band():
    return BANDS['BLE']


@pytest.fixture
def lora_us_band():
    return BANDS['LoRa_US']


@pytest.fixture
def two_band_selection():
    return [BANDS['LTE_B13'], BANDS['GNSS_L1']]


@pytest.fixture
def multi_band_selection():
    return [BANDS['LTE_B3'], BANDS['WiFi_2G'], BANDS['BLE'], BANDS['GNSS_L1']]
