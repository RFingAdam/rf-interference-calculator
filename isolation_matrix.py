"""
Per-Band Isolation Requirements Matrix

This module provides minimum isolation requirements for coexistence
between different radio technologies and bands.

Values are derived from:
- 3GPP TS 36.101 (LTE UE requirements)
- 3GPP TS 38.101 (NR UE requirements)
- IEEE 802.11 (WiFi coexistence)
- Bluetooth SIG specifications
- Industry coexistence studies

Usage:
    from isolation_matrix import get_required_isolation, get_isolation_recommendation

    # Get minimum required isolation
    isolation = get_required_isolation("LTE_B13", "GNSS_L1")  # Returns 50.0 dB

    # Get recommendation with explanation
    rec = get_isolation_recommendation("WiFi_2G", "BLE")
"""

from typing import Dict, Tuple, Optional, List
from dataclasses import dataclass


@dataclass
class IsolationRequirement:
    """Detailed isolation requirement between band pairs."""
    min_isolation_db: float
    recommended_isolation_db: float
    product_types: List[str]  # '2H', '3H', 'IM3', 'direct', etc.
    notes: str
    reference: str


# Per-band isolation requirements matrix
# Format: (aggressor, victim): IsolationRequirement
ISOLATION_REQUIREMENTS: Dict[Tuple[str, str], IsolationRequirement] = {
    # =========================================================================
    # Critical GPS/GNSS Protection
    # =========================================================================
    ("LTE_B13", "GNSS_L1"): IsolationRequirement(
        min_isolation_db=50.0,
        recommended_isolation_db=60.0,
        product_types=["2H"],
        notes="2nd harmonic of B13 (2×787=1574 MHz) hits GPS L1 (1575.42 MHz). Critical safety concern.",
        reference="FCC Order 10-4, 3GPP TS 36.101"
    ),

    ("LTE_B14", "GNSS_L1"): IsolationRequirement(
        min_isolation_db=45.0,
        recommended_isolation_db=55.0,
        product_types=["2H"],
        notes="2nd harmonic near GPS L1. FirstNet public safety band.",
        reference="3GPP TS 36.101"
    ),

    ("LTE_B26", "GNSS_L2"): IsolationRequirement(
        min_isolation_db=40.0,
        recommended_isolation_db=50.0,
        product_types=["3H"],
        notes="3rd harmonic of upper B26 near GPS L2.",
        reference="3GPP TS 36.101"
    ),

    # =========================================================================
    # LTE/WiFi 5 GHz Coexistence
    # =========================================================================
    ("LTE_B7", "WiFi_5G"): IsolationRequirement(
        min_isolation_db=35.0,
        recommended_isolation_db=45.0,
        product_types=["2H"],
        notes="2nd harmonic of B7 (2×2570=5140 MHz) near WiFi 5 GHz.",
        reference="3GPP TS 36.101"
    ),

    ("LTE_B41", "WiFi_5G"): IsolationRequirement(
        min_isolation_db=30.0,
        recommended_isolation_db=40.0,
        product_types=["2H"],
        notes="2nd harmonic of B41 in WiFi 5 GHz band.",
        reference="3GPP TS 36.101"
    ),

    ("LTE_B4", "WiFi_5G"): IsolationRequirement(
        min_isolation_db=30.0,
        recommended_isolation_db=40.0,
        product_types=["3H"],
        notes="3rd harmonic of B4 (3×1755=5265 MHz) in WiFi 5 GHz.",
        reference="3GPP TS 36.101"
    ),

    ("LTE_B66", "WiFi_5G"): IsolationRequirement(
        min_isolation_db=30.0,
        recommended_isolation_db=40.0,
        product_types=["3H"],
        notes="3rd harmonic of AWS-3 in WiFi 5 GHz.",
        reference="3GPP TS 36.101"
    ),

    # =========================================================================
    # 2.4 GHz ISM Band Coexistence
    # =========================================================================
    ("LTE_B26", "WiFi_2G"): IsolationRequirement(
        min_isolation_db=40.0,
        recommended_isolation_db=50.0,
        product_types=["3H"],
        notes="3rd harmonic of B26 (3×814=2442 MHz) in 2.4 GHz ISM.",
        reference="3GPP TS 36.101"
    ),

    ("LTE_B26", "BLE"): IsolationRequirement(
        min_isolation_db=40.0,
        recommended_isolation_db=50.0,
        product_types=["3H"],
        notes="3rd harmonic of B26 affects BLE channels.",
        reference="3GPP TS 36.101"
    ),

    ("WiFi_2G", "BLE"): IsolationRequirement(
        min_isolation_db=15.0,
        recommended_isolation_db=25.0,
        product_types=["direct", "IM3"],
        notes="Co-channel/adjacent channel coexistence in 2.4 GHz ISM.",
        reference="Bluetooth SIG, IEEE 802.11"
    ),

    ("BLE", "WiFi_2G"): IsolationRequirement(
        min_isolation_db=15.0,
        recommended_isolation_db=25.0,
        product_types=["direct", "IM3"],
        notes="Bidirectional coexistence in 2.4 GHz ISM.",
        reference="Bluetooth SIG, IEEE 802.11"
    ),

    ("WiFi_2G", "Zigbee"): IsolationRequirement(
        min_isolation_db=20.0,
        recommended_isolation_db=30.0,
        product_types=["direct"],
        notes="WiFi can block Zigbee channels.",
        reference="IEEE 802.15.4"
    ),

    # =========================================================================
    # Sub-1 GHz Coexistence (HaLow, LoRa, ISM)
    # =========================================================================
    ("LTE_B26", "ISM902"): IsolationRequirement(
        min_isolation_db=25.0,
        recommended_isolation_db=35.0,
        product_types=["direct", "IM3"],
        notes="LTE B26 uplink can interfere with 900 MHz ISM.",
        reference="FCC Part 15"
    ),

    ("HaLow_NA", "ISM902"): IsolationRequirement(
        min_isolation_db=15.0,
        recommended_isolation_db=25.0,
        product_types=["direct"],
        notes="Wi-Fi HaLow shares 900 MHz ISM band.",
        reference="IEEE 802.11ah"
    ),

    ("LoRa_US", "ISM902"): IsolationRequirement(
        min_isolation_db=10.0,
        recommended_isolation_db=20.0,
        product_types=["direct"],
        notes="LoRaWAN shares 900 MHz ISM band.",
        reference="LoRa Alliance"
    ),

    # =========================================================================
    # Cellular Band Coexistence
    # =========================================================================
    ("LTE_B7", "LTE_B38"): IsolationRequirement(
        min_isolation_db=25.0,
        recommended_isolation_db=35.0,
        product_types=["direct"],
        notes="B7 FDD and B38 TDD share 2600 MHz spectrum.",
        reference="3GPP TS 36.101"
    ),

    ("LTE_B41", "LTE_B7"): IsolationRequirement(
        min_isolation_db=25.0,
        recommended_isolation_db=35.0,
        product_types=["direct", "IM3"],
        notes="B41 and B7 are adjacent in 2.5-2.7 GHz.",
        reference="3GPP TS 36.101"
    ),

    # =========================================================================
    # 5G NR Coexistence
    # =========================================================================
    ("NR_n77", "WiFi_6E"): IsolationRequirement(
        min_isolation_db=35.0,
        recommended_isolation_db=45.0,
        product_types=["2H"],
        notes="2nd harmonic of n77 (2×4200=8400 MHz) near WiFi 6E upper band. Direct adjacency at 5-7 GHz.",
        reference="3GPP TS 38.101-1"
    ),

    ("NR_n78", "WiFi_6E"): IsolationRequirement(
        min_isolation_db=35.0,
        recommended_isolation_db=45.0,
        product_types=["2H"],
        notes="2nd harmonic of n78 (2×3800=7600 MHz) hits WiFi 6E band.",
        reference="3GPP TS 38.101-1"
    ),

    ("NR_n77", "WiFi_5G"): IsolationRequirement(
        min_isolation_db=30.0,
        recommended_isolation_db=40.0,
        product_types=["direct", "IM3"],
        notes="NR n77 upper edge (4200 MHz) near WiFi 5G band (4900+ MHz).",
        reference="3GPP TS 38.101-1"
    ),

    ("NR_n79", "WiFi_5G"): IsolationRequirement(
        min_isolation_db=30.0,
        recommended_isolation_db=40.0,
        product_types=["direct"],
        notes="NR n79 (4400-5000 MHz) overlaps WiFi 5G band.",
        reference="3GPP TS 38.101-1"
    ),

    ("NR_n41", "WiFi_5G"): IsolationRequirement(
        min_isolation_db=30.0,
        recommended_isolation_db=40.0,
        product_types=["2H"],
        notes="2nd harmonic of n41 (2×2690=5380 MHz) in WiFi 5 GHz band.",
        reference="3GPP TS 38.101-1"
    ),

    ("NR_n77", "GNSS_L1"): IsolationRequirement(
        min_isolation_db=35.0,
        recommended_isolation_db=45.0,
        product_types=["IM3"],
        notes="NR n77 IM3 products can fall near GNSS L1.",
        reference="3GPP TS 38.101-1"
    ),

    ("NR_n78", "GNSS_L1"): IsolationRequirement(
        min_isolation_db=35.0,
        recommended_isolation_db=45.0,
        product_types=["IM3"],
        notes="NR n78 IM3 products can fall near GNSS L1.",
        reference="3GPP TS 38.101-1"
    ),

    # =========================================================================
    # Additional LTE Harmonic Pairs
    # =========================================================================
    ("LTE_B3", "WiFi_5G"): IsolationRequirement(
        min_isolation_db=30.0,
        recommended_isolation_db=40.0,
        product_types=["3H"],
        notes="3rd harmonic of B3 (3×1785=5355 MHz) hits WiFi 5 GHz.",
        reference="3GPP TS 36.101"
    ),

    ("LTE_B8", "WiFi_2G"): IsolationRequirement(
        min_isolation_db=35.0,
        recommended_isolation_db=45.0,
        product_types=["3H"],
        notes="3rd harmonic of B8 (3×915=2745 MHz) near 2.4 GHz ISM upper edge.",
        reference="3GPP TS 36.101"
    ),

    ("LTE_B5", "GNSS_L2"): IsolationRequirement(
        min_isolation_db=40.0,
        recommended_isolation_db=50.0,
        product_types=["2H"],
        notes="2nd harmonic of B5 (2×849=1698 MHz) near GPS L2 (1227 MHz). Actually 3H: 3×415=1245.",
        reference="3GPP TS 36.101"
    ),

    ("LTE_B5", "GNSS_L5"): IsolationRequirement(
        min_isolation_db=40.0,
        recommended_isolation_db=50.0,
        product_types=["IM3"],
        notes="LTE B5 IM3 products can fall near GNSS L5.",
        reference="3GPP TS 36.101"
    ),

    ("WiFi_2G", "WiFi_5G"): IsolationRequirement(
        min_isolation_db=20.0,
        recommended_isolation_db=30.0,
        product_types=["2H"],
        notes="2nd harmonic of WiFi 2.4G (2×2495=4990 MHz) near WiFi 5 GHz.",
        reference="IEEE 802.11"
    ),

    ("LTE_B1", "WiFi_5G"): IsolationRequirement(
        min_isolation_db=30.0,
        recommended_isolation_db=40.0,
        product_types=["3H"],
        notes="3rd harmonic of B1 (3×1980=5940 MHz) hits WiFi 5/6E.",
        reference="3GPP TS 36.101"
    ),

    ("LTE_B25", "WiFi_5G"): IsolationRequirement(
        min_isolation_db=30.0,
        recommended_isolation_db=40.0,
        product_types=["3H"],
        notes="3rd harmonic of B25 (3×1915=5745 MHz) hits WiFi 5 GHz.",
        reference="3GPP TS 36.101"
    ),

    ("NR_n3", "WiFi_5G"): IsolationRequirement(
        min_isolation_db=30.0,
        recommended_isolation_db=40.0,
        product_types=["3H"],
        notes="3rd harmonic of n3 (3×1785=5355 MHz) hits WiFi 5 GHz.",
        reference="3GPP TS 38.101-1"
    ),

    ("NR_n7", "WiFi_5G"): IsolationRequirement(
        min_isolation_db=35.0,
        recommended_isolation_db=45.0,
        product_types=["2H"],
        notes="2nd harmonic of n7 (2×2570=5140 MHz) near WiFi 5 GHz.",
        reference="3GPP TS 38.101-1"
    ),

    ("NR_n41", "GNSS_L1"): IsolationRequirement(
        min_isolation_db=30.0,
        recommended_isolation_db=40.0,
        product_types=["IM3"],
        notes="NR n41 IM3 products can interact with GNSS L1.",
        reference="3GPP TS 38.101-1"
    ),
}

# Default isolation values based on victim criticality
DEFAULT_ISOLATION = {
    "GNSS": 45.0,      # GNSS is always critical
    "GPS": 45.0,
    "PUBLIC_SAFETY": 40.0,
    "FIRSTNET": 40.0,
    "LTE": 30.0,
    "5G": 30.0,
    "WIFI": 25.0,
    "WI-FI": 25.0,
    "BLE": 20.0,
    "BLUETOOTH": 20.0,
    "ISM": 25.0,
    "HALOW": 25.0,
    "LORA": 20.0,
    "ZIGBEE": 20.0,
    "DEFAULT": 25.0
}


def get_required_isolation(aggressor: str, victim: str) -> float:
    """
    Get minimum required isolation between band pair.

    Args:
        aggressor: Transmitting band code
        victim: Receiving band code

    Returns:
        Minimum required isolation in dB
    """
    # Check exact match first
    key = (aggressor, victim)
    if key in ISOLATION_REQUIREMENTS:
        return ISOLATION_REQUIREMENTS[key].min_isolation_db

    # Check reverse direction (some pairs are symmetric)
    key_reverse = (victim, aggressor)
    if key_reverse in ISOLATION_REQUIREMENTS:
        return ISOLATION_REQUIREMENTS[key_reverse].min_isolation_db

    # Check partial matches (e.g., any LTE to any GNSS)
    for (agg_pattern, vic_pattern), req in ISOLATION_REQUIREMENTS.items():
        if agg_pattern in aggressor and vic_pattern in victim:
            return req.min_isolation_db

    # Fall back to default based on victim criticality
    victim_upper = victim.upper()
    for tech, default_iso in DEFAULT_ISOLATION.items():
        if tech in victim_upper:
            return default_iso

    return DEFAULT_ISOLATION["DEFAULT"]


def get_recommended_isolation(aggressor: str, victim: str) -> float:
    """
    Get recommended isolation between band pair (with margin).

    Args:
        aggressor: Transmitting band code
        victim: Receiving band code

    Returns:
        Recommended isolation in dB
    """
    key = (aggressor, victim)
    if key in ISOLATION_REQUIREMENTS:
        return ISOLATION_REQUIREMENTS[key].recommended_isolation_db

    # Use minimum + 10 dB as default recommendation
    return get_required_isolation(aggressor, victim) + 10.0


def get_isolation_recommendation(aggressor: str, victim: str) -> Dict:
    """
    Get detailed isolation recommendation with explanation.

    Args:
        aggressor: Transmitting band code
        victim: Receiving band code

    Returns:
        Dictionary with isolation details and recommendations
    """
    key = (aggressor, victim)

    if key in ISOLATION_REQUIREMENTS:
        req = ISOLATION_REQUIREMENTS[key]
        return {
            "aggressor": aggressor,
            "victim": victim,
            "min_isolation_db": req.min_isolation_db,
            "recommended_isolation_db": req.recommended_isolation_db,
            "product_types": req.product_types,
            "notes": req.notes,
            "reference": req.reference,
            "source": "specific_requirement"
        }

    # Check reverse
    key_reverse = (victim, aggressor)
    if key_reverse in ISOLATION_REQUIREMENTS:
        req = ISOLATION_REQUIREMENTS[key_reverse]
        return {
            "aggressor": aggressor,
            "victim": victim,
            "min_isolation_db": req.min_isolation_db,
            "recommended_isolation_db": req.recommended_isolation_db,
            "product_types": req.product_types,
            "notes": f"(Reverse of {victim} -> {aggressor}) " + req.notes,
            "reference": req.reference,
            "source": "reverse_requirement"
        }

    # Generate default recommendation
    min_iso = get_required_isolation(aggressor, victim)
    return {
        "aggressor": aggressor,
        "victim": victim,
        "min_isolation_db": min_iso,
        "recommended_isolation_db": min_iso + 10.0,
        "product_types": ["general"],
        "notes": f"Default isolation based on {victim} technology sensitivity.",
        "reference": "Default estimation",
        "source": "default"
    }


def check_isolation_compliance(
    aggressor: str,
    victim: str,
    actual_isolation_db: float
) -> Tuple[bool, str, float]:
    """
    Check if actual isolation meets requirements.

    Args:
        aggressor: Transmitting band code
        victim: Receiving band code
        actual_isolation_db: Measured or calculated isolation

    Returns:
        (compliant, status_message, margin_db)
    """
    min_required = get_required_isolation(aggressor, victim)
    recommended = get_recommended_isolation(aggressor, victim)

    margin = actual_isolation_db - min_required

    if actual_isolation_db >= recommended:
        return (True, "Excellent - Exceeds recommended isolation", margin)
    elif actual_isolation_db >= min_required:
        return (True, "Acceptable - Meets minimum requirement", margin)
    else:
        return (False, f"FAIL - {abs(margin):.1f} dB below minimum", margin)


def get_all_critical_pairs() -> List[Dict]:
    """
    Get list of all critical band pairs requiring special attention.

    Returns:
        List of critical pairs with isolation requirements
    """
    critical = []

    for (agg, vic), req in ISOLATION_REQUIREMENTS.items():
        if req.min_isolation_db >= 40.0:  # High isolation = critical
            critical.append({
                "aggressor": agg,
                "victim": vic,
                "min_isolation_db": req.min_isolation_db,
                "product_types": req.product_types,
                "notes": req.notes
            })

    return critical


def generate_isolation_matrix_table(bands: List[str]) -> Dict[str, Dict[str, float]]:
    """
    Generate isolation matrix for a set of bands.

    Args:
        bands: List of band codes to include

    Returns:
        Dictionary of dictionaries: matrix[aggressor][victim] = isolation_db
    """
    matrix = {}

    for agg in bands:
        matrix[agg] = {}
        for vic in bands:
            if agg != vic:
                matrix[agg][vic] = get_required_isolation(agg, vic)
            else:
                matrix[agg][vic] = 0.0  # Self-interference not applicable

    return matrix


if __name__ == "__main__":
    # Test the isolation matrix
    print("=== Isolation Matrix Database ===\n")

    # Test specific pairs
    test_pairs = [
        ("LTE_B13", "GNSS_L1"),
        ("LTE_B26", "WiFi_2G"),
        ("WiFi_2G", "BLE"),
        ("LTE_B4", "WiFi_5G"),
        ("LTE_B41", "WiFi_5G"),
    ]

    print("Critical Band Pairs:\n")
    for agg, vic in test_pairs:
        rec = get_isolation_recommendation(agg, vic)
        print(f"{agg} -> {vic}:")
        print(f"  Min: {rec['min_isolation_db']:.0f} dB")
        print(f"  Recommended: {rec['recommended_isolation_db']:.0f} dB")
        print(f"  Products: {', '.join(rec['product_types'])}")
        print(f"  Notes: {rec['notes']}")
        print()

    # Test compliance checking
    print("=== Compliance Checking ===\n")

    test_cases = [
        ("LTE_B13", "GNSS_L1", 55.0),  # Pass
        ("LTE_B13", "GNSS_L1", 45.0),  # Fail
        ("WiFi_2G", "BLE", 20.0),      # Pass
    ]

    for agg, vic, isolation in test_cases:
        compliant, status, margin = check_isolation_compliance(agg, vic, isolation)
        print(f"{agg} -> {vic} @ {isolation:.0f} dB:")
        print(f"  {status}")
        print(f"  Margin: {margin:+.1f} dB")
        print()

    # Print all critical pairs
    print("=== All Critical Pairs (>40 dB required) ===\n")
    for pair in get_all_critical_pairs():
        print(f"  {pair['aggressor']} -> {pair['victim']}: {pair['min_isolation_db']:.0f} dB")
