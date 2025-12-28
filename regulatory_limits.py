"""
3GPP and FCC Spurious Emission Limits Database

Based on:
- 3GPP TS 36.101 (E-UTRA UE radio transmission and reception)
- 3GPP TS 38.101 (NR UE radio transmission and reception)
- FCC Part 15 and Part 22/24/27

This module provides:
- Band-specific spurious emission requirements
- Protected band limits (GPS L1, public safety, etc.)
- General spurious emission limits
- Compliance checking functions

Reference tables:
- TS 36.101 Table 6.6.3.1-1 (Additional spurious emission limits)
- TS 36.101 Table 6.7.3.1-1 (Additional requirements for Band 13)
"""

from typing import Dict, Tuple, List, Optional
from dataclasses import dataclass


@dataclass
class EmissionLimit:
    """Specification for an emission limit at a protected frequency."""
    freq_low_mhz: float
    freq_high_mhz: float
    limit_dbm: float
    measurement_bw_mhz: float
    reference: str
    notes: str = ""


@dataclass
class BandEmissionRequirements:
    """Complete emission requirements for a specific band."""
    protected_bands: Dict[str, EmissionLimit]
    general_spurious_9khz_1ghz: float  # dBm
    general_spurious_1ghz_12p75ghz: float  # dBm
    aclr_limit_dbc: float  # dBc
    sem_limit_dbm: float  # dBm (spectrum emission mask)


# Band-specific spurious emission requirements from 3GPP TS 36.101
SPURIOUS_LIMITS_3GPP: Dict[str, BandEmissionRequirements] = {
    # LTE Band 13 (777-787 MHz) - Critical GPS L1 protection
    # Reference: TS 36.101 Table 6.6.3.2-1
    "LTE_B13": BandEmissionRequirements(
        protected_bands={
            "GPS_L1": EmissionLimit(
                freq_low_mhz=1559.0,
                freq_high_mhz=1610.0,
                limit_dbm=-60.0,  # Very strict: -60 dBm (older) or -50 dBm (newer devices)
                measurement_bw_mhz=1.023,  # GPS C/A code bandwidth
                reference="TS 36.101 Table 6.6.3.2-1, FCC 10-4",
                notes="GPS L1 protection, critical for public safety"
            ),
            "GPS_L5": EmissionLimit(
                freq_low_mhz=1164.0,
                freq_high_mhz=1189.0,
                limit_dbm=-50.0,
                measurement_bw_mhz=10.0,
                reference="TS 36.101",
                notes="GPS L5/Galileo E5a protection"
            )
        },
        general_spurious_9khz_1ghz=-36.0,
        general_spurious_1ghz_12p75ghz=-30.0,
        aclr_limit_dbc=-30.0,
        sem_limit_dbm=-15.0
    ),

    # LTE Band 14 (788-798 MHz) - FirstNet Public Safety
    "LTE_B14": BandEmissionRequirements(
        protected_bands={
            "GPS_L1": EmissionLimit(
                freq_low_mhz=1559.0,
                freq_high_mhz=1610.0,
                limit_dbm=-50.0,
                measurement_bw_mhz=1.023,
                reference="TS 36.101, FCC FirstNet rules",
                notes="GPS L1 protection for public safety"
            )
        },
        general_spurious_9khz_1ghz=-36.0,
        general_spurious_1ghz_12p75ghz=-30.0,
        aclr_limit_dbc=-30.0,
        sem_limit_dbm=-15.0
    ),

    # LTE Band 7 (2500-2570 MHz TX)
    "LTE_B7": BandEmissionRequirements(
        protected_bands={
            "WiFi_5G": EmissionLimit(
                freq_low_mhz=5150.0,
                freq_high_mhz=5350.0,
                limit_dbm=-30.0,
                measurement_bw_mhz=1.0,
                reference="TS 36.101",
                notes="2nd harmonic protection for WiFi 5GHz"
            )
        },
        general_spurious_9khz_1ghz=-36.0,
        general_spurious_1ghz_12p75ghz=-30.0,
        aclr_limit_dbc=-45.0,
        sem_limit_dbm=-10.0
    ),

    # LTE Band 26 (814-849 MHz TX) - ESMR, can produce 3H in 2.4 GHz
    "LTE_B26": BandEmissionRequirements(
        protected_bands={
            "ISM_2400": EmissionLimit(
                freq_low_mhz=2400.0,
                freq_high_mhz=2500.0,
                limit_dbm=-40.0,
                measurement_bw_mhz=1.0,
                reference="TS 36.101, FCC Part 15",
                notes="3rd harmonic in 2.4 GHz ISM band"
            ),
            "GPS_L2": EmissionLimit(
                freq_low_mhz=1215.0,
                freq_high_mhz=1245.0,
                limit_dbm=-50.0,
                measurement_bw_mhz=10.0,
                reference="TS 36.101",
                notes="GPS L2 protection"
            )
        },
        general_spurious_9khz_1ghz=-36.0,
        general_spurious_1ghz_12p75ghz=-30.0,
        aclr_limit_dbc=-33.0,
        sem_limit_dbm=-13.0
    ),

    # LTE Band 4 (1710-1755 MHz TX) - AWS-1, 3H in WiFi 5GHz
    "LTE_B4": BandEmissionRequirements(
        protected_bands={
            "WiFi_5G_UNII1": EmissionLimit(
                freq_low_mhz=5150.0,
                freq_high_mhz=5350.0,
                limit_dbm=-30.0,
                measurement_bw_mhz=1.0,
                reference="TS 36.101",
                notes="3rd harmonic in WiFi 5GHz UNII-1"
            ),
            "WiFi_5G_UNII2": EmissionLimit(
                freq_low_mhz=5470.0,
                freq_high_mhz=5725.0,
                limit_dbm=-30.0,
                measurement_bw_mhz=1.0,
                reference="TS 36.101",
                notes="3rd harmonic in WiFi 5GHz UNII-2"
            )
        },
        general_spurious_9khz_1ghz=-36.0,
        general_spurious_1ghz_12p75ghz=-30.0,
        aclr_limit_dbc=-33.0,
        sem_limit_dbm=-13.0
    ),

    # LTE Band 41 (2496-2690 MHz TDD)
    "LTE_B41": BandEmissionRequirements(
        protected_bands={
            "WiFi_5G": EmissionLimit(
                freq_low_mhz=4900.0,
                freq_high_mhz=5900.0,
                limit_dbm=-30.0,
                measurement_bw_mhz=1.0,
                reference="TS 36.101",
                notes="2nd harmonic protection for WiFi 5GHz"
            )
        },
        general_spurious_9khz_1ghz=-36.0,
        general_spurious_1ghz_12p75ghz=-30.0,
        aclr_limit_dbc=-45.0,
        sem_limit_dbm=-10.0
    ),

    # Generic LTE bands (default limits)
    "LTE_DEFAULT": BandEmissionRequirements(
        protected_bands={},
        general_spurious_9khz_1ghz=-36.0,
        general_spurious_1ghz_12p75ghz=-30.0,
        aclr_limit_dbc=-30.0,
        sem_limit_dbm=-13.0
    ),
}

# General 3GPP spurious emission limits (TS 36.101 Table 6.6.2.1-1)
GENERAL_SPURIOUS_LIMITS = {
    "9kHz-150kHz": -36.0,      # dBm in 1 kHz
    "150kHz-30MHz": -36.0,     # dBm in 10 kHz
    "30MHz-1GHz": -36.0,       # dBm in 100 kHz
    "1GHz-12.75GHz": -30.0,    # dBm in 1 MHz
}

# FCC-specific limits
FCC_LIMITS = {
    "Part15_unintentional": -41.2,  # dBm EIRP (equivalent to 500 uV/m at 3m)
    "Part15_ISM_2400": 30.0,        # dBm EIRP max for 2.4 GHz ISM
    "Part15_ISM_5800": 30.0,        # dBm EIRP max for 5.8 GHz ISM
    "GPS_L1_protection": -60.0,     # dBm in 1.023 MHz (FCC Order 10-4)
}


def check_emission_compliance(
    band_code: str,
    product_freq_mhz: float,
    product_power_dbm: float
) -> Tuple[bool, str, float]:
    """
    Check if emission at frequency meets 3GPP/FCC limits.

    Args:
        band_code: Transmitting band code (e.g., 'LTE_B13')
        product_freq_mhz: Frequency of spurious/harmonic product (MHz)
        product_power_dbm: Power of the product (dBm)

    Returns:
        (compliant: bool, reason: str, margin_db: float)
        - compliant: True if within limits
        - reason: Description of limit checked
        - margin_db: Margin to limit (positive = headroom, negative = violation)
    """
    # Get band-specific requirements
    if band_code in SPURIOUS_LIMITS_3GPP:
        band_limits = SPURIOUS_LIMITS_3GPP[band_code]
    elif band_code.startswith("LTE_"):
        band_limits = SPURIOUS_LIMITS_3GPP["LTE_DEFAULT"]
    else:
        # Non-LTE bands - use general limits
        band_limits = SPURIOUS_LIMITS_3GPP["LTE_DEFAULT"]

    # Check protected bands first (strictest limits)
    for protected_name, limit_spec in band_limits.protected_bands.items():
        if limit_spec.freq_low_mhz <= product_freq_mhz <= limit_spec.freq_high_mhz:
            margin = limit_spec.limit_dbm - product_power_dbm
            compliant = product_power_dbm <= limit_spec.limit_dbm
            return (
                compliant,
                f"{protected_name}: {product_power_dbm:.1f} dBm vs {limit_spec.limit_dbm:.1f} dBm limit ({limit_spec.reference})",
                margin
            )

    # Check general spurious limits
    if product_freq_mhz < 1000:
        limit = band_limits.general_spurious_9khz_1ghz
        freq_range = "9kHz-1GHz"
    else:
        limit = band_limits.general_spurious_1ghz_12p75ghz
        freq_range = "1GHz-12.75GHz"

    margin = limit - product_power_dbm
    compliant = product_power_dbm <= limit

    return (
        compliant,
        f"General spurious ({freq_range}): {product_power_dbm:.1f} dBm vs {limit:.1f} dBm limit",
        margin
    )


def get_emission_limit_for_frequency(
    band_code: str,
    target_freq_mhz: float
) -> Tuple[float, str]:
    """
    Get the applicable emission limit for a specific frequency.

    Args:
        band_code: Transmitting band code
        target_freq_mhz: Target frequency (MHz)

    Returns:
        (limit_dbm: float, reference: str)
    """
    if band_code in SPURIOUS_LIMITS_3GPP:
        band_limits = SPURIOUS_LIMITS_3GPP[band_code]
    else:
        band_limits = SPURIOUS_LIMITS_3GPP.get("LTE_DEFAULT", None)
        if band_limits is None:
            return (-30.0, "Default limit")

    # Check protected bands
    for protected_name, limit_spec in band_limits.protected_bands.items():
        if limit_spec.freq_low_mhz <= target_freq_mhz <= limit_spec.freq_high_mhz:
            return (limit_spec.limit_dbm, limit_spec.reference)

    # Return general limit
    if target_freq_mhz < 1000:
        return (band_limits.general_spurious_9khz_1ghz, "TS 36.101 Table 6.6.2.1-1")
    else:
        return (band_limits.general_spurious_1ghz_12p75ghz, "TS 36.101 Table 6.6.2.1-1")


def get_critical_frequency_pairs() -> List[Dict]:
    """
    Get list of known critical frequency pairs requiring special attention.

    Returns:
        List of dictionaries with aggressor, victim, product_type, and severity info
    """
    return [
        {
            "aggressor": "LTE_B13",
            "victim": "GNSS_L1",
            "product_type": "2H",
            "description": "LTE B13 2nd harmonic directly hits GPS L1",
            "severity": "Critical",
            "formula": "2 × 787 MHz = 1574 MHz (GPS L1 @ 1575.42 MHz)"
        },
        {
            "aggressor": "LTE_B26",
            "victim": "WiFi_2G",
            "product_type": "3H",
            "description": "LTE B26 3rd harmonic hits 2.4 GHz ISM band",
            "severity": "High",
            "formula": "3 × 814 MHz = 2442 MHz (2.4 GHz ISM center)"
        },
        {
            "aggressor": "LTE_B4",
            "victim": "WiFi_5G",
            "product_type": "3H",
            "description": "LTE B4 3rd harmonic hits WiFi 5 GHz",
            "severity": "High",
            "formula": "3 × 1755 MHz = 5265 MHz (WiFi 5 GHz U-NII-1)"
        },
        {
            "aggressor": "LTE_B7",
            "victim": "WiFi_5G",
            "product_type": "2H",
            "description": "LTE B7 2nd harmonic near WiFi 5 GHz",
            "severity": "Medium",
            "formula": "2 × 2570 MHz = 5140 MHz (near WiFi 5 GHz)"
        },
        {
            "aggressor": "WiFi_2G",
            "victim": "BLE",
            "product_type": "IM3",
            "description": "WiFi/BLE coexistence in 2.4 GHz ISM",
            "severity": "Medium",
            "formula": "Co-channel interference in 2.4 GHz"
        },
        {
            "aggressor": "LTE_B41",
            "victim": "WiFi_5G",
            "product_type": "2H",
            "description": "LTE B41 2nd harmonic in WiFi 5 GHz",
            "severity": "Medium",
            "formula": "2 × 2690 MHz = 5380 MHz (WiFi 5 GHz)"
        },
    ]


def generate_compliance_report(
    band_code: str,
    interference_products: List[Dict]
) -> Dict:
    """
    Generate a compliance report for a set of interference products.

    Args:
        band_code: Transmitting band code
        interference_products: List of products with freq_mhz and power_dbm

    Returns:
        Report dictionary with compliance status and details
    """
    report = {
        "band_code": band_code,
        "total_products": len(interference_products),
        "compliant_count": 0,
        "violation_count": 0,
        "violations": [],
        "warnings": [],
        "passed": []
    }

    for product in interference_products:
        freq = product.get("freq_mhz", 0)
        power = product.get("power_dbm", 0)
        product_type = product.get("type", "unknown")

        compliant, reason, margin = check_emission_compliance(band_code, freq, power)

        entry = {
            "frequency_mhz": freq,
            "power_dbm": power,
            "product_type": product_type,
            "compliant": compliant,
            "reason": reason,
            "margin_db": margin
        }

        if compliant:
            report["compliant_count"] += 1
            if margin < 6.0:  # Less than 6 dB margin = warning
                report["warnings"].append(entry)
            else:
                report["passed"].append(entry)
        else:
            report["violation_count"] += 1
            report["violations"].append(entry)

    return report


if __name__ == "__main__":
    # Test the compliance checking
    print("=== 3GPP Regulatory Limits Database ===\n")

    # Test LTE B13 -> GPS L1
    print("Test Case: LTE B13 -> GPS L1 (2H @ 1574 MHz)")
    compliant, reason, margin = check_emission_compliance("LTE_B13", 1574.0, -50.0)
    print(f"  Power: -50 dBm")
    print(f"  Compliant: {compliant}")
    print(f"  Reason: {reason}")
    print(f"  Margin: {margin:+.1f} dB")
    print()

    # Test violation case
    print("Test Case: LTE B13 -> GPS L1 (2H @ 1574 MHz) - VIOLATION")
    compliant, reason, margin = check_emission_compliance("LTE_B13", 1574.0, -40.0)
    print(f"  Power: -40 dBm")
    print(f"  Compliant: {compliant}")
    print(f"  Reason: {reason}")
    print(f"  Margin: {margin:+.1f} dB")
    print()

    # Test general spurious
    print("Test Case: General spurious emission")
    compliant, reason, margin = check_emission_compliance("LTE_B1", 5000.0, -35.0)
    print(f"  Power: -35 dBm @ 5000 MHz")
    print(f"  Compliant: {compliant}")
    print(f"  Reason: {reason}")
    print(f"  Margin: {margin:+.1f} dB")
    print()

    # Print critical frequency pairs
    print("=== Critical Frequency Pairs ===\n")
    for pair in get_critical_frequency_pairs():
        print(f"  {pair['aggressor']} -> {pair['victim']}")
        print(f"    Product: {pair['product_type']}")
        print(f"    Severity: {pair['severity']}")
        print(f"    {pair['formula']}")
        print()
