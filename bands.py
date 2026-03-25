from dataclasses import dataclass
from typing import List


@dataclass
class Band:
    code: str
    tx_low: float
    tx_high: float
    rx_low: float
    rx_high: float
    label: str
    category: str
    papr_db: float = 0.0  # Peak-to-Average Power Ratio in dB (modulation-dependent)

# LTE and ISM bands (extend as needed)
# To add new bands, follow the format:
# Band("BAND_CODE", tx_low, tx_high, rx_low, rx_high, "Band Label", "Category")
# Example:
# Band("LTE_B1", 1920, 1980, 2110, 2170, "LTE B1 (2100)", "LTE")
    # 2G GSM (GMSK: constant envelope, PAPR ~0 dB)
BAND_LIST: List[Band] = [
    Band("GSM_850", 824, 849, 869, 894, "GSM 850", "2G GSM", papr_db=0.0),
    Band("GSM_1800", 1710, 1785, 1805, 1880, "GSM 1800 (DCS)", "2G GSM", papr_db=0.0),
    Band("GSM_1900", 1850, 1910, 1930, 1990, "GSM 1900 (PCS)", "2G GSM", papr_db=0.0),

    # 3G UMTS/WCDMA (WCDMA: PAPR ~3.4 dB)
    Band("UMTS_B1", 1920, 1980, 2110, 2170, "UMTS B1 (2100)", "3G UMTS/WCDMA", papr_db=3.4),
    Band("UMTS_B2", 1850, 1910, 1930, 1990, "UMTS B2 (1900 PCS)", "3G UMTS/WCDMA", papr_db=3.4),
    Band("UMTS_B3", 1710, 1785, 1805, 1880, "UMTS B3 (1800 DCS)", "3G UMTS/WCDMA", papr_db=3.4),
    Band("UMTS_B4", 1710, 1755, 2110, 2155, "UMTS B4 (AWS-1)", "3G UMTS/WCDMA", papr_db=3.4),
    Band("UMTS_B5", 824, 849, 869, 894, "UMTS B5 (850)", "3G UMTS/WCDMA", papr_db=3.4),
    Band("UMTS_B8", 880, 915, 925, 960, "UMTS B8 (900)", "3G UMTS/WCDMA", papr_db=3.4),

    # LTE (SC-FDMA UL: PAPR ~8.0 dB)
    Band("LTE_B1", 1920, 1980, 2110, 2170, "LTE B1 (2100)", "LTE", papr_db=8.0),
    Band("LTE_B2", 1850, 1910, 1930, 1990, "LTE B2 (1900 PCS)", "LTE", papr_db=8.0),
    Band("LTE_B3", 1710, 1785, 1805, 1880, "LTE B3 (1800 DCS)", "LTE", papr_db=8.0),
    Band("LTE_B4", 1710, 1755, 2110, 2155, "LTE B4 (AWS-1)", "LTE", papr_db=8.0),
    Band("LTE_B5", 824, 849, 869, 894, "LTE B5 (850)", "LTE", papr_db=8.0),
    Band("LTE_B7", 2500, 2570, 2620, 2690, "LTE B7 (2600)", "LTE", papr_db=8.0),
    Band("LTE_B8", 880, 915, 925, 960, "LTE B8 (900)", "LTE", papr_db=8.0),
    Band("LTE_B12", 699, 716, 729, 746, "LTE B12 (700a)", "LTE", papr_db=8.0),
    Band("LTE_B13", 777, 787, 746, 756, "LTE B13 (700c)", "LTE", papr_db=8.0),
    Band("LTE_B14", 788, 798, 758, 768, "LTE B14 (700 PS)", "LTE", papr_db=8.0),
    Band("LTE_B17", 704, 716, 734, 746, "LTE B17 (700b)", "LTE", papr_db=8.0),
    Band("LTE_B18", 815, 830, 860, 875, "LTE B18 (800 Lower)", "LTE", papr_db=8.0),
    Band("LTE_B19", 830, 845, 875, 890, "LTE B19 (800 Upper)", "LTE", papr_db=8.0),
    Band("LTE_B20", 832, 862, 791, 821, "LTE B20 (800 DD)", "LTE", papr_db=8.0),
    Band("LTE_B21", 1447.9, 1462.9, 1495.9, 1510.9, "LTE B21 (1500)", "LTE", papr_db=8.0),
    Band("LTE_B25", 1850, 1915, 1930, 1995, "LTE B25 (1900+)", "LTE", papr_db=8.0),
    Band("LTE_B26", 814, 849, 859, 894, "LTE B26 (850+)", "LTE", papr_db=8.0),
    Band("LTE_B28", 703, 748, 758, 803, "LTE B28 (700)", "LTE", papr_db=8.0),
    Band("LTE_B29", 0, 0, 717, 728, "LTE B29 (700 DL)", "LTE", papr_db=8.0),
    Band("LTE_B30", 2305, 2315, 2350, 2360, "LTE B30 (2300)", "LTE", papr_db=8.0),
    Band("LTE_B32", 0, 0, 1452, 1496, "LTE B32 (1500 SDL)", "LTE", papr_db=8.0),  # SDL = Supplemental Downlink (receive-only)
    Band("LTE_B38", 2570, 2620, 2570, 2620, "LTE B38 (TDD 2600)", "LTE", papr_db=8.0),
    Band("LTE_B39", 1880, 1920, 1880, 1920, "LTE B39 (TDD 1900)", "LTE", papr_db=8.0),
    Band("LTE_B40", 2300, 2400, 2300, 2400, "LTE B40 (TDD 2300)", "LTE", papr_db=8.0),
    Band("LTE_B41", 2496, 2690, 2496, 2690, "LTE B41 (TDD 2500)", "LTE", papr_db=8.0),
    Band("LTE_B42", 3400, 3600, 3400, 3600, "LTE B42 (TDD 3500)", "LTE", papr_db=8.0),
    Band("LTE_B43", 3600, 3800, 3600, 3800, "LTE B43 (TDD 3700)", "LTE", papr_db=8.0),
    Band("LTE_B44", 703, 803, 703, 803, "LTE B44 (TDD 700)", "LTE", papr_db=8.0),
    Band("LTE_B48", 3550, 3700, 3550, 3700, "LTE B48 (TDD CBRS)", "LTE", papr_db=8.0),
    Band("LTE_B66", 1710, 1780, 2110, 2200, "LTE B66 (AWS-3)", "LTE", papr_db=8.0),
    Band("LTE_B71", 663, 698, 617, 652, "LTE B71 (600)", "LTE", papr_db=8.0),

    # 5G NR FR1 (Sub-6 GHz) - 3GPP TS 38.101-1 (CP-OFDM: PAPR ~9.0 dB)
    Band("NR_n1", 1920, 1980, 2110, 2170, "NR n1 (2100 FDD)", "5G NR", papr_db=9.0),
    Band("NR_n2", 1850, 1910, 1930, 1990, "NR n2 (1900 PCS)", "5G NR", papr_db=9.0),
    Band("NR_n3", 1710, 1785, 1805, 1880, "NR n3 (1800)", "5G NR", papr_db=9.0),
    Band("NR_n5", 824, 849, 869, 894, "NR n5 (850)", "5G NR", papr_db=9.0),
    Band("NR_n7", 2500, 2570, 2620, 2690, "NR n7 (2600)", "5G NR", papr_db=9.0),
    Band("NR_n25", 1850, 1915, 1930, 1995, "NR n25 (1900+)", "5G NR", papr_db=9.0),
    Band("NR_n28", 703, 748, 758, 803, "NR n28 (700)", "5G NR", papr_db=9.0),
    Band("NR_n38", 2570, 2620, 2570, 2620, "NR n38 (TDD 2600)", "5G NR", papr_db=9.0),
    Band("NR_n41", 2496, 2690, 2496, 2690, "NR n41 (TDD 2500)", "5G NR", papr_db=9.0),
    Band("NR_n66", 1710, 1780, 2110, 2200, "NR n66 (AWS)", "5G NR", papr_db=9.0),
    Band("NR_n71", 663, 698, 617, 652, "NR n71 (600)", "5G NR", papr_db=9.0),
    Band("NR_n77", 3300, 4200, 3300, 4200, "NR n77 (TDD C-Band)", "5G NR", papr_db=9.0),
    Band("NR_n78", 3300, 3800, 3300, 3800, "NR n78 (TDD C-Band)", "5G NR", papr_db=9.0),
    Band("NR_n79", 4400, 5000, 4400, 5000, "NR n79 (TDD 4.5 GHz)", "5G NR", papr_db=9.0),

    # Wi-Fi (OFDM: PAPR ~10.0 dB)
    Band("WiFi_2G", 2400, 2495, 2400, 2495, "Wi-Fi 2.4G Band", "Wi-Fi", papr_db=10.0),
    Band("WiFi_5G", 4900, 5900, 4900, 5900, "Wi-Fi 5G Band", "Wi-Fi", papr_db=10.0),
    Band("WiFi_6E", 5900, 7125, 5900, 7125, "Wi-Fi 6E Band", "Wi-Fi", papr_db=10.0),

    # Bluetooth/BLE (GFSK: PAPR ~2.0 dB)
    Band("BLE", 2402, 2480, 2402, 2480, "Bluetooth LE (2402-2480)", "BLE", papr_db=2.0),

    # ISM Bands (default 0 dB, varies by application)
    Band("UHF433", 433, 435, 433, 435, "UHF 433 MHz", "ISM", papr_db=0.0),
    Band("UHF450", 450, 470, 450, 470, "UHF 450 MHz", "ISM", papr_db=0.0),
    Band("ISM902", 902, 928, 902, 928, "ISM 902-928 MHz", "ISM", papr_db=0.0),
    Band("ISM_24", 2400, 2500, 2400, 2500, "ISM 2.4 GHz Band", "ISM", papr_db=0.0),
    Band("ISM_58", 5725, 5875, 5725, 5875, "ISM 5.8 GHz Band", "ISM", papr_db=0.0),

    # IoT/Smart Home (2.4 GHz) (DSSS/O-QPSK: PAPR ~0 dB)
    Band("Zigbee", 2405, 2480, 2405, 2480, "Zigbee (2.4 GHz)", "IoT", papr_db=0.0),
    Band("Thread", 2405, 2480, 2405, 2480, "Thread (2.4 GHz)", "IoT", papr_db=0.0),
    Band("Matter", 2405, 2480, 2405, 2480, "Matter/Thread (2.4 GHz)", "IoT", papr_db=0.0),

    # UHF Bands

    # LoRaWAN (CSS: constant envelope, PAPR ~0 dB)
    Band("LoRa_US", 902, 928, 902, 928, "LoRaWAN US", "LoRa", papr_db=0.0),
    Band("LoRa_EU", 863, 870, 863, 870, "LoRaWAN EU", "LoRa", papr_db=0.0),

    # HaLow (Wi-Fi Sub-1 GHz, OFDM: PAPR ~8.0 dB)
    Band("HaLow_NA", 902, 928, 902, 928, "HaLow NA (915)", "HaLow", papr_db=8.0),
    Band("HaLow_EU", 863, 868, 863, 868, "HaLow EU (866)", "HaLow", papr_db=8.0),
    Band("HaLow_AUS", 915, 928, 915, 928, "HaLow AUS/NZ (920)", "HaLow", papr_db=8.0),
    Band("HaLow_JP", 920.5, 928.1, 920.5, 928.1, "HaLow JP (922.5)", "HaLow", papr_db=8.0),
    Band("HaLow_TW", 920, 925, 920, 925, "HaLow TW (922.5)", "HaLow", papr_db=8.0),
    Band("HaLow_KR", 918, 923, 918, 923, "HaLow KR (920.5)", "HaLow", papr_db=8.0),

    # RFID/NFC (ASK/OOK: PAPR ~0 dB)
    Band("RFID_HF", 13.50, 13.62, 13.50, 13.62, "RFID HF (13.56 MHz)", "RFID", papr_db=0.0),
    Band("RFID_UHF", 860, 960, 860, 960, "RFID UHF (860-960 MHz)", "RFID", papr_db=0.0),
    Band("NFC", 13.50, 13.62, 13.50, 13.62, "NFC (13.56 MHz)", "RFID", papr_db=0.0),

    # Public Safety (various modulation, typical ~3.0 dB)
    Band("TETRA", 380, 470, 380, 470, "TETRA (400 MHz)", "Public Safety", papr_db=3.0),
    Band("P25_VHF", 136, 174, 136, 174, "P25 VHF (150 MHz)", "Public Safety", papr_db=3.0),
    Band("P25_UHF", 380, 520, 380, 520, "P25 UHF (450 MHz)", "Public Safety", papr_db=3.0),

    # Amateur Radio (SSB/FM: PAPR ~0 dB)
    Band("Amateur_2M", 144, 148, 144, 148, "Amateur 2m (VHF)", "Amateur", papr_db=0.0),
    Band("Amateur_70CM", 420, 450, 420, 450, "Amateur 70cm (UHF)", "Amateur", papr_db=0.0),

    # GNSS bands are receive-only (no transmission from user equipment)
    Band("GNSS_L1", 0, 0, 1559, 1606, "GNSS L1/E1", "GNSS", papr_db=0.0),
    Band("GNSS_L2", 0, 0, 1215, 1245, "GNSS L2", "GNSS", papr_db=0.0),
    Band("GNSS_L5", 0, 0, 1164, 1189, "GNSS L5/E5", "GNSS", papr_db=0.0),
]

BANDS = {b.code: b for b in BAND_LIST}
