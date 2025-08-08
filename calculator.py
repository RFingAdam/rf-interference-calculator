from typing import List, Tuple, Dict
from bands import Band

def calculate_all_products(selected_bands: List[Band], guard: float = 0.0, imd2: bool = True, imd4: bool = False, imd5: bool = True, imd7: bool = False, aclr_margin: float = 0.0) -> Tuple[List[Dict], List[str]]:
    """
    Exhaustive IMD/harmonic/overlap logic for all selected bands, matching app.py.
    Returns (results, overlap_alerts).
    """
    results = []
    overlap_alerts = []
    n = len(selected_bands)
    # Overlap checks (Tx/Tx, Rx/Rx, Tx in Rx, Rx in Tx)
    for i in range(n):
        b1 = selected_bands[i]
        for j in range(i+1, n):
            b2 = selected_bands[j]
            b1_tx_low = b1.tx_low - guard
            b1_tx_high = b1.tx_high + guard
            b2_tx_low = b2.tx_low - guard
            b2_tx_high = b2.tx_high + guard
            b1_rx_low = b1.rx_low - guard
            b1_rx_high = b1.rx_high + guard
            b2_rx_low = b2.rx_low - guard
            b2_rx_high = b2.rx_high + guard
            
            # Tx-Tx overlap (skip if either band is receive-only)
            b1_has_tx = not (b1.tx_low == 0 and b1.tx_high == 0)
            b2_has_tx = not (b2.tx_low == 0 and b2.tx_high == 0)
            
            if b1_has_tx and b2_has_tx:
                if not (b1_tx_high < b2_tx_low or b2_tx_high < b1_tx_low):
                    overlap_alerts.append(f"Tx band overlap: {b1.code} ({b1.tx_low}-{b1.tx_high} MHz) and {b2.code} ({b2.tx_low}-{b2.tx_high} MHz)")
                    
            # Rx-Rx overlap
            if not (b1_rx_high < b2_rx_low or b2_rx_high < b1_rx_low):
                overlap_alerts.append(f"Rx band overlap: {b1.code} ({b1.rx_low}-{b1.rx_high} MHz) and {b2.code} ({b2.rx_low}-{b2.rx_high} MHz)")
                
            # Tx of one in Rx of other (skip if transmitting band is receive-only)
            if b1_has_tx and not (b1_tx_high < b2_rx_low or b1_tx_low > b2_rx_high):
                overlap_alerts.append(f"Tx({b1.code}) overlaps Rx({b2.code})")
            if b2_has_tx and not (b2_tx_high < b1_rx_low or b2_tx_low > b1_rx_high):
                overlap_alerts.append(f"Tx({b2.code}) overlaps Rx({b1.code})")

    # Harmonics (2H, 3H, 4H, 5H) - Skip receive-only bands (tx_low = tx_high = 0)
    for b in selected_bands:
        # Skip receive-only bands like GNSS
        if b.tx_low == 0 and b.tx_high == 0:
            continue
            
        for order in (2, 3, 4, 5):
            for edge in [b.tx_low, b.tx_high]:
                if edge == 0:  # Additional safety check
                    continue
                freq = edge * order
                for victim in selected_bands:
                    rx_low = victim.rx_low - guard
                    rx_high = victim.rx_high + guard
                    risk = rx_low <= freq <= rx_high
                    results.append(dict(
                        Type=f"{order}H",
                        IM3_Type="Harmonic",
                        Formula=f"{order}×Tx_{'low' if edge==b.tx_low else 'high'}({b.code})",
                        Frequency_MHz=round(freq, 2),
                        Aggressors=b.code,
                        Victims=victim.code if risk else '',
                        Risk="⚠️" if risk else "✓",
                        Details=f"{order}th Harmonic: {order}×{edge} = {freq:.1f} MHz (Band: {b.code})",
                    ))

    # IM2 Beat Terms (f₁ ± f₂) - Critical for wideband systems, often higher than IM3
    if imd2:
        for i in range(n):
            b1 = selected_bands[i]
            # Skip receive-only bands as aggressors
            if b1.tx_low == 0 and b1.tx_high == 0:
                continue
                
            for j in range(i+1, n):  # Avoid duplicates with i+1
                b2 = selected_bands[j]
                # Skip receive-only bands as aggressors  
                if b2.tx_low == 0 and b2.tx_high == 0:
                    continue
                    
                A_edges = [b1.tx_low, b1.tx_high]
                B_edges = [b2.tx_low, b2.tx_high]
                
                for A in A_edges:
                    if A == 0:  # Additional safety check
                        continue
                    for B in B_edges:
                        if B == 0:  # Additional safety check
                            continue
                        
                        # f₁ + f₂ and f₁ - f₂ (and f₂ - f₁)
                        for sign, op_str in [(1, '+'), (-1, '-')]:
                            freq_plus_minus = A + sign * B
                            if freq_plus_minus > 0:  # Only positive frequencies
                                for victim in selected_bands:
                                    rx_low = victim.rx_low - guard
                                    rx_high = victim.rx_high + guard
                                    risk = rx_low <= freq_plus_minus <= rx_high
                                    results.append(dict(
                                        Type="IM2",
                                        IM3_Type="Beat Frequency",
                                        Formula=f"{b1.code}_{'low' if A==b1.tx_low else 'high'} {op_str} {b2.code}_{'low' if B==b2.tx_low else 'high'}",
                                        Frequency_MHz=round(freq_plus_minus, 2),
                                        Aggressors=f"{b1.code}, {b2.code}",
                                        Victims=victim.code if risk else '',
                                        Risk="⚠️" if risk else "✓",
                                        Details=f"IM2 Beat: {A} {op_str} {B} = {freq_plus_minus:.1f} MHz (A={b1.code}, B={b2.code})",
                                    ))
                            
                            # Also calculate B ± A to be thorough
                            if sign == -1:  # Only for subtraction to avoid complete duplication
                                freq_reverse = B - A
                                if freq_reverse > 0:  # Only positive frequencies
                                    for victim in selected_bands:
                                        rx_low = victim.rx_low - guard
                                        rx_high = victim.rx_high + guard
                                        risk = rx_low <= freq_reverse <= rx_high
                                        results.append(dict(
                                            Type="IM2",
                                            IM3_Type="Beat Frequency",
                                            Formula=f"{b2.code}_{'low' if B==b2.tx_low else 'high'} - {b1.code}_{'low' if A==b1.tx_low else 'high'}",
                                            Frequency_MHz=round(freq_reverse, 2),
                                            Aggressors=f"{b1.code}, {b2.code}",
                                            Victims=victim.code if risk else '',
                                            Risk="⚠️" if risk else "✓",
                                            Details=f"IM2 Beat: {B} - {A} = {freq_reverse:.1f} MHz (B={b2.code}, A={b1.code})",
                                        ))

    # IM3 exhaustive edge cases (all band pairs, all edges)
    for i in range(n):
        b1 = selected_bands[i]
        # Skip receive-only bands as aggressors
        if b1.tx_low == 0 and b1.tx_high == 0:
            continue
            
        for j in range(n):
            if i == j:
                continue
            b2 = selected_bands[j]
            # Skip receive-only bands as aggressors  
            if b2.tx_low == 0 and b2.tx_high == 0:
                continue
                
            A_edges = [b1.tx_low, b1.tx_high]
            B_edges = [b2.tx_low, b2.tx_high]
            # Fundamental-only (2A ± B, 2B ± A)
            for A in A_edges:
                if A == 0:  # Additional safety check
                    continue
                for B in B_edges:
                    if B == 0:  # Additional safety check
                        continue
                    for sign in [-1, 1]:
                        freq1 = 2*A + sign*B
                        for victim in selected_bands:
                            rx_low = victim.rx_low - guard
                            rx_high = victim.rx_high + guard
                            risk = rx_low <= freq1 <= rx_high
                            results.append(dict(
                                Type="IM3",
                                IM3_Type="Fundamental-only",
                                Formula=f"2×{b1.code}_{'low' if A==b1.tx_low else 'high'} {'+' if sign>0 else '-'} {b2.code}_{'low' if B==b2.tx_low else 'high'}",
                                Frequency_MHz=round(freq1, 2),
                                Aggressors=f"{b1.code}, {b2.code}",
                                Victims=victim.code if risk else '',
                                Risk="⚠️" if risk else "✓",
                                Details=f"IM3 (Fundamental-only): 2×{A} {'+' if sign>0 else '-'} {B} = {freq1:.1f} MHz (A={b1.code}, B={b2.code})",
                            ))
            for B in B_edges:
                for A in A_edges:
                    for sign in [-1, 1]:
                        freq2 = 2*B + sign*A
                        for victim in selected_bands:
                            rx_low = victim.rx_low - guard
                            rx_high = victim.rx_high + guard
                            risk = rx_low <= freq2 <= rx_high
                            results.append(dict(
                                Type="IM3",
                                IM3_Type="Fundamental-only",
                                Formula=f"2×{b2.code}_{'low' if B==b2.tx_low else 'high'} {'+' if sign>0 else '-'} {b1.code}_{'low' if A==b1.tx_low else 'high'}",
                                Frequency_MHz=round(freq2, 2),
                                Aggressors=f"{b1.code}, {b2.code}",
                                Victims=victim.code if risk else '',
                                Risk="⚠️" if risk else "✓",
                                Details=f"IM3 (Fundamental-only): 2×{B} {'+' if sign>0 else '-'} {A} = {freq2:.1f} MHz (B={b2.code}, A={b1.code})",
                            ))
            # Mixed 2nd-harmonic/fundamental (2*(2A) ± B, 2*(2B) ± A)
            for A in A_edges:
                for B in B_edges:
                    for sign in [-1, 1]:
                        freq3 = 2*(2*A) + sign*B
                        for victim in selected_bands:
                            rx_low = victim.rx_low - guard
                            rx_high = victim.rx_high + guard
                            risk = rx_low <= freq3 <= rx_high
                            results.append(dict(
                                Type="IM3",
                                IM3_Type="2nd Harmonic of A vs Fundamental B",
                                Formula=f"2×(2×{b1.code}_{'low' if A==b1.tx_low else 'high'}) {'+' if sign>0 else '-'} {b2.code}_{'low' if B==b2.tx_low else 'high'}",
                                Frequency_MHz=round(freq3, 2),
                                Aggressors=f"{b1.code}, {b2.code}",
                                Victims=victim.code if risk else '',
                                Risk="⚠️" if risk else "✓",
                                Details=f"IM3 (2nd Harmonic of A vs Fundamental B): 2×(2×{A}) {'+' if sign>0 else '-'} {B} = {freq3:.1f} MHz (A={b1.code}, B={b2.code})",
                            ))
            for B in B_edges:
                for A in A_edges:
                    for sign in [-1, 1]:
                        freq4 = 2*(2*B) + sign*A
                        for victim in selected_bands:
                            rx_low = victim.rx_low - guard
                            rx_high = victim.rx_high + guard
                            risk = rx_low <= freq4 <= rx_high
                            results.append(dict(
                                Type="IM3",
                                IM3_Type="2nd Harmonic of B vs Fundamental A",
                                Formula=f"2×(2×{b2.code}_{'low' if B==b2.tx_low else 'high'}) {'+' if sign>0 else '-'} {b1.code}_{'low' if A==b1.tx_low else 'high'}",
                                Frequency_MHz=round(freq4, 2),
                                Aggressors=f"{b1.code}, {b2.code}",
                                Victims=victim.code if risk else '',
                                Risk="⚠️" if risk else "✓",
                                Details=f"IM3 (2nd Harmonic of B vs Fundamental A): 2×(2×{B}) {'+' if sign>0 else '-'} {A} = {freq4:.1f} MHz (B={b2.code}, A={b1.code})",
                            ))
            # 2nd Harmonic of both (2A ± 2B, 2B ± 2A)
            for A in A_edges:
                for B in B_edges:
                    for sign in [-1, 1]:
                        freq5 = 2*A + sign*2*B
                        for victim in selected_bands:
                            rx_low = victim.rx_low - guard
                            rx_high = victim.rx_high + guard
                            risk = rx_low <= freq5 <= rx_high
                            results.append(dict(
                                Type="IM3",
                                IM3_Type="2nd Harmonic of A vs 2nd Harmonic of B",
                                Formula=f"2×{b1.code}_{'low' if A==b1.tx_low else 'high'} {'+' if sign>0 else '-'} 2×{b2.code}_{'low' if B==b2.tx_low else 'high'}",
                                Frequency_MHz=round(freq5, 2),
                                Aggressors=f"{b1.code}, {b2.code}",
                                Victims=victim.code if risk else '',
                                Risk="⚠️" if risk else "✓",
                                Details=f"IM3 (2nd Harmonic of A vs 2nd Harmonic of B): 2×{A} {'+' if sign>0 else '-'} 2×{B} = {freq5:.1f} MHz (A={b1.code}, B={b2.code})",
                            ))
            for B in B_edges:
                for A in A_edges:
                    for sign in [-1, 1]:
                        freq6 = 2*B + sign*2*A
                        for victim in selected_bands:
                            rx_low = victim.rx_low - guard
                            rx_high = victim.rx_high + guard
                            risk = rx_low <= freq6 <= rx_high
                            results.append(dict(
                                Type="IM3",
                                IM3_Type="2nd Harmonic of B vs 2nd Harmonic of A",
                                Formula=f"2×{b2.code}_{'low' if B==b2.tx_low else 'high'} {'+' if sign>0 else '-'} 2×{b1.code}_{'low' if A==b1.tx_low else 'high'}",
                                Frequency_MHz=round(freq6, 2),
                                Aggressors=f"{b1.code}, {b2.code}",
                                Victims=victim.code if risk else '',
                                Risk="⚠️" if risk else "✓",
                                Details=f"IM3 (2nd Harmonic of B vs 2nd Harmonic of A): 2×{B} {'+' if sign>0 else '-'} 2×{A} = {freq6:.1f} MHz (B={b2.code}, A={b1.code})",
                            ))
            # IM4 (2f1+2f2, 3f1+f2, f1+3f2)
            if imd4:
                for A in A_edges:
                    for B in B_edges:
                        # Standard IM4: 2f1+2f2
                        freq4_std = 2*A + 2*B
                        for victim in selected_bands:
                            rx_low = victim.rx_low - guard
                            rx_high = victim.rx_high + guard
                            risk = rx_low <= freq4_std <= rx_high
                            results.append(dict(
                                Type="IM4",
                                IM3_Type="Higher-order",
                                Formula=f"2×{b1.code}_{'low' if A==b1.tx_low else 'high'} + 2×{b2.code}_{'low' if B==b2.tx_low else 'high'}",
                                Frequency_MHz=round(freq4_std, 2),
                                Aggressors=f"{b1.code}, {b2.code}",
                                Victims=victim.code if risk else '',
                                Risk="⚠️" if risk else "✓",
                                Details=f"IM4: 2×{A} + 2×{B} = {freq4_std:.1f} MHz (A={b1.code}, B={b2.code})",
                            ))
                        
                        # Extended IM4: 3f1+f2 and f1+3f2
                        for coeff1, coeff2 in [(3, 1), (1, 3)]:
                            freq4_ext = coeff1*A + coeff2*B
                            for victim in selected_bands:
                                rx_low = victim.rx_low - guard
                                rx_high = victim.rx_high + guard
                                risk = rx_low <= freq4_ext <= rx_high
                                results.append(dict(
                                    Type="IM4",
                                    IM3_Type="Higher-order",
                                    Formula=f"{coeff1}×{b1.code}_{'low' if A==b1.tx_low else 'high'} + {coeff2}×{b2.code}_{'low' if B==b2.tx_low else 'high'}",
                                    Frequency_MHz=round(freq4_ext, 2),
                                    Aggressors=f"{b1.code}, {b2.code}",
                                    Victims=victim.code if risk else '',
                                    Risk="⚠️" if risk else "✓",
                                    Details=f"IM4: {coeff1}×{A} + {coeff2}×{B} = {freq4_ext:.1f} MHz (A={b1.code}, B={b2.code})",
                                ))
            # IM5 (3f1±2f2, 2f1±3f2)
            if imd5:
                for A in A_edges:
                    for B in B_edges:
                        # Standard IM5: 3f1±2f2
                        for sign in [-1, 1]:
                            freq5_std = 3*A + sign*2*B
                            for victim in selected_bands:
                                rx_low = victim.rx_low - guard
                                rx_high = victim.rx_high + guard
                                risk = rx_low <= freq5_std <= rx_high
                                results.append(dict(
                                    Type="IM5",
                                    IM3_Type="Higher-order",
                                    Formula=f"3×{b1.code}_{'low' if A==b1.tx_low else 'high'} {'+' if sign>0 else '-'} 2×{b2.code}_{'low' if B==b2.tx_low else 'high'}",
                                    Frequency_MHz=round(freq5_std, 2),
                                    Aggressors=f"{b1.code}, {b2.code}",
                                    Victims=victim.code if risk else '',
                                    Risk="⚠️" if risk else "✓",
                                    Details=f"IM5: 3×{A} {'+' if sign>0 else '-'} 2×{B} = {freq5_std:.1f} MHz (A={b1.code}, B={b2.code})",
                                ))
                        
                        # Extended IM5: 2f1±3f2
                        for sign in [-1, 1]:
                            freq5_ext = 2*A + sign*3*B
                            for victim in selected_bands:
                                rx_low = victim.rx_low - guard
                                rx_high = victim.rx_high + guard
                                risk = rx_low <= freq5_ext <= rx_high
                                results.append(dict(
                                    Type="IM5",
                                    IM3_Type="Higher-order",
                                    Formula=f"2×{b1.code}_{'low' if A==b1.tx_low else 'high'} {'+' if sign>0 else '-'} 3×{b2.code}_{'low' if B==b2.tx_low else 'high'}",
                                    Frequency_MHz=round(freq5_ext, 2),
                                    Aggressors=f"{b1.code}, {b2.code}",
                                    Victims=victim.code if risk else '',
                                    Risk="⚠️" if risk else "✓",
                                    Details=f"IM5: 2×{A} {'+' if sign>0 else '-'} 3×{B} = {freq5_ext:.1f} MHz (A={b1.code}, B={b2.code})",
                                ))
            # IM7 (4f1±3f2)
            if imd7:
                for A in A_edges:
                    for B in B_edges:
                        for sign in [-1, 1]:
                            freq7 = 4*A + sign*3*B
                            for victim in selected_bands:
                                rx_low = victim.rx_low - guard
                                rx_high = victim.rx_high + guard
                                risk = rx_low <= freq7 <= rx_high
                                results.append(dict(
                                    Type="IM7",
                                    IM3_Type="Higher-order",
                                    Formula=f"4×{b1.code}_{'low' if A==b1.tx_low else 'high'} {'+' if sign>0 else '-'} 3×{b2.code}_{'low' if B==b2.tx_low else 'high'}",
                                    Frequency_MHz=round(freq7, 2),
                                    Aggressors=f"{b1.code}, {b2.code}",
                                    Victims=victim.code if risk else '',
                                    Risk="⚠️" if risk else "✓",
                                    Details=f"IM7: 4×{A} {'+' if sign>0 else '-'} 3×{B} = {freq7:.1f} MHz (A={b1.code}, B={b2.code})",
                                ))
    # ACLR check (optional, for all pairs)
    if aclr_margin > 0:
        for i in range(n):
            b1 = selected_bands[i]
            # Skip receive-only bands for ACLR (no transmission)
            if b1.tx_low == 0 and b1.tx_high == 0:
                continue
                
            for j in range(n):
                if i == j:
                    continue
                b2 = selected_bands[j]
                aclr_risk = aclr_check(b1.tx_high, b2.rx_low, aclr_margin)
                results.append(dict(
                    Type="ACLR",
                    IM3_Type="Adjacent-channel",
                    Formula=f"{b1.code}_tx_high vs {b2.code}_rx_low",
                    Frequency_MHz=round((b1.tx_high + b2.rx_low) / 2, 2),
                    Aggressors=b1.code,
                    Victims=b2.code if aclr_risk else '',
                    Risk="⚠️" if aclr_risk else "✓",
                    Details=f"ACLR: {b1.tx_high} MHz vs {b2.rx_low} MHz (gap: {abs(b1.tx_high - b2.rx_low):.1f} MHz)",
                ))
    # Deduplicate: focus on mathematical uniqueness rather than descriptive differences
    seen = set()
    deduped = []
    for r in results:
        # Create unique key based on actual mathematical content
        freq = r.get('Frequency_MHz', 0)
        aggressors = tuple(sorted(r.get('Aggressors', '').split(', '))) if r.get('Aggressors') else ()
        victims = r.get('Victims', '')
        
        # For mathematical uniqueness, ignore descriptive IM3_Type differences
        # Same frequency + same aggressors + same victims = duplicate
        key = (
            r.get('Type'),
            round(freq, 2) if freq else 0,  # Round to avoid floating point precision issues
            aggressors,  # Sorted aggressor list to handle order differences
            victims,
        )
        if key not in seen:
            seen.add(key)
            deduped.append(r)
    # Sort: risk items (Risk='⚠️') at the top, ordered by signal level priority, then by Type, Formula, Frequency_MHz
    def get_signal_level_priority(r):
        """Return priority based on typical signal level (lower number = higher signal level)"""
        imd_type = r.get('Type', '')
        if imd_type == '2H':
            return 1  # 2nd harmonic - typically highest
        elif imd_type == 'IM2':
            return 2  # IM2 beat terms - often higher than IM3
        elif imd_type == '3H':
            return 3  # 3rd harmonic
        elif imd_type == 'IM3':
            return 4  # IM3 - most common analysis
        elif imd_type == '4H':
            return 5  # 4th harmonic
        elif imd_type == 'IM4':
            return 6  # IM4
        elif imd_type == '5H':
            return 7  # 5th harmonic
        elif imd_type == 'IM5':
            return 8  # IM5
        elif imd_type == 'IM7':
            return 9  # IM7 - lowest typical signal level
        elif imd_type == 'ACLR':
            return 10  # ACLR - different mechanism
        else:
            return 99  # Unknown types
    
    def sort_key(r):
        risk = 0 if r.get('Risk') == '⚠️' else 1
        signal_priority = get_signal_level_priority(r)
        freq = r.get('Frequency_MHz', 0)
        return (risk, signal_priority, str(r.get('Type')), str(r.get('Formula')), freq)
    
    deduped.sort(key=sort_key)
    return deduped, overlap_alerts


def hits_rx(freq_low: float, freq_high: float, rx_low: float, rx_high: float) -> bool:
    return (
        rx_low <= freq_low <= rx_high
        or rx_low <= freq_high <= rx_high
        or (freq_low <= rx_low and freq_high >= rx_high)
    )

def aclr_check(tx_high: float, rx_low: float, margin: float) -> bool:
    # Adjacent channel leakage: Tx high within margin of Rx low
    return abs(tx_high - rx_low) <= margin

def evaluate(
    tx_band: Band,
    rx_band: Band,
    guard: float,
    imd4: bool = False,
    imd5: bool = True,
    imd7: bool = False,
    aclr_margin: float = 0.0
) -> List[Dict]:
    # Skip calculations if tx_band is receive-only (like GNSS)
    if tx_band.tx_low == 0 and tx_band.tx_high == 0:
        return []
        
    rx_low, rx_high = rx_band.rx_low - guard, rx_band.rx_high + guard
    rows = []

    # 2H / 3H / 4H / 5H
    for order in (2, 3, 4, 5):
        low, high = tx_band.tx_low * order, tx_band.tx_high * order
        rows.append(
            dict(
                Type=f"{order}H",
                Formula=f"{order}×Tx({tx_band.code})",
                Freq_low=low,
                Freq_high=high,
                Risk=hits_rx(low, high, rx_low, rx_high),
                RiskLevel=risk_level(low, high, rx_low, rx_high),
            )
        )

    # IM2 Beat Terms (f1 ± f2) - Critical for wideband systems
    # Only calculate if both bands have transmission capability
    if not (tx_band.tx_low == 0 and tx_band.tx_high == 0) and not (rx_band.tx_low == 0 and rx_band.tx_high == 0):
        tx_edges = [tx_band.tx_low, tx_band.tx_high]
        rx_tx_edges = [rx_band.tx_low, rx_band.tx_high]
        
        for f1 in tx_edges:
            for f2 in rx_tx_edges:
                if f1 > 0 and f2 > 0:  # Ensure positive frequencies
                    # f1 + f2
                    freq_sum = f1 + f2
                    rows.append(dict(
                        Type="IM2",
                        Formula=f"Tx({tx_band.code}) + Tx({rx_band.code})",
                        Freq_low=freq_sum,
                        Freq_high=freq_sum,
                        Risk=rx_low <= freq_sum <= rx_high,
                        RiskLevel=risk_level(freq_sum, freq_sum, rx_low, rx_high),
                    ))
                    
                    # |f1 - f2| (absolute difference)
                    freq_diff = abs(f1 - f2)
                    if freq_diff > 0:  # Avoid zero frequency
                        rows.append(dict(
                            Type="IM2",
                            Formula=f"|Tx({tx_band.code}) - Tx({rx_band.code})|",
                            Freq_low=freq_diff,
                            Freq_high=freq_diff,
                            Risk=rx_low <= freq_diff <= rx_high,
                            RiskLevel=risk_level(freq_diff, freq_diff, rx_low, rx_high),
                        ))

    # IM3: 2f1 ± f2 (use both band edges)
    edges = [
        (tx_band.tx_low, tx_band.tx_high),
        (rx_band.tx_low, rx_band.tx_high),
    ]
    combos = [
        (2 * edges[0][0] - edges[1][1], "2·X_low − Y_high"),
        (2 * edges[0][1] - edges[1][0], "2·X_high − Y_low"),
        (2 * edges[1][0] - edges[0][1], "2·Y_low − X_high"),
        (2 * edges[1][1] - edges[0][0], "2·Y_high − X_low"),
    ]
    for freq, label in combos:
        rows.append(
            dict(
                Type="IM3",
                Formula=label,
                Freq_low=freq,
                Freq_high=freq,  # discrete
                Risk=rx_low <= freq <= rx_high,
                RiskLevel=risk_level(freq, freq, rx_low, rx_high),
            )
        )

    # IM4 (2f1+2f2)
    if imd4:
        combos4 = [
            (2 * edges[0][0] + 2 * edges[1][1], "2·X_low + 2·Y_high"),
            (2 * edges[0][1] + 2 * edges[1][0], "2·X_high + 2·Y_low"),
            (2 * edges[1][0] + 2 * edges[0][1], "2·Y_low + 2·X_high"),
            (2 * edges[1][1] + 2 * edges[0][0], "2·Y_high + 2·X_low"),
        ]
        for freq, label in combos4:
            rows.append(
                dict(
                    Type="IM4",
                    Formula=label,
                    Freq_low=freq,
                    Freq_high=freq,
                    Risk=rx_low <= freq <= rx_high,
                    RiskLevel=risk_level(freq, freq, rx_low, rx_high),
                )
            )
    # IM5 (3f1±2f2)
    if imd5:
        combos5 = [
            (3 * edges[0][0] - 2 * edges[1][1], "3·X_low − 2·Y_high"),
            (3 * edges[0][1] - 2 * edges[1][0], "3·X_high − 2·Y_low"),
            (3 * edges[1][0] - 2 * edges[0][1], "3·Y_low − 2·X_high"),
            (3 * edges[1][1] - 2 * edges[0][0], "3·Y_high − 2·X_low"),
        ]
        for freq, label in combos5:
            rows.append(
                dict(
                    Type="IM5",
                    Formula=label,
                    Freq_low=freq,
                    Freq_high=freq,
                    Risk=rx_low <= freq <= rx_high,
                    RiskLevel=risk_level(freq, freq, rx_low, rx_high),
                )
            )
    # IM7 (4f1±3f2)
    if imd7:
        combos7 = [
            (4 * edges[0][0] - 3 * edges[1][1], "4·X_low − 3·Y_high"),
            (4 * edges[0][1] - 3 * edges[1][0], "4·X_high − 3·Y_low"),
            (4 * edges[1][0] - 3 * edges[0][1], "4·Y_low − 3·X_high"),
            (4 * edges[1][1] - 3 * edges[0][0], "4·Y_high − 3·X_low"),
        ]
        for freq, label in combos7:
            rows.append(
                dict(
                    Type="IM7",
                    Formula=label,
                    Freq_low=freq,
                    Freq_high=freq,
                    Risk=rx_low <= freq <= rx_high,
                    RiskLevel=risk_level(freq, freq, rx_low, rx_high),
                )
            )
    # ACLR check
    if aclr_margin > 0:
        aclr_risk = aclr_check(tx_band.tx_high, rx_band.rx_low, aclr_margin)
        rows.append(
            dict(
                Type="ACLR",
                Formula="Tx_high vs Rx_low",
                Freq_low=tx_band.tx_high,
                Freq_high=rx_band.rx_low,
                Risk=aclr_risk,
                RiskLevel="High" if aclr_risk else "Low",
            )
        )
    return rows

def risk_level(freq_low, freq_high, rx_low, rx_high):
    """Enhanced risk assessment with multiple criteria."""
    # In-band interference (highest priority)
    if rx_low <= freq_low <= rx_high or rx_low <= freq_high <= rx_high:
        return "High"
    
    # Close proximity assessment
    min_distance = min(
        abs(freq_low - rx_low), 
        abs(freq_low - rx_high),
        abs(freq_high - rx_low), 
        abs(freq_high - rx_high)
    )
    
    # Adjacent channel interference
    if min_distance < 1.0:  # Within 1 MHz
        return "High"
    elif min_distance < 5.0:  # Within 5 MHz
        return "Med"
    elif min_distance < 20.0:  # Within 20 MHz
        return "Low"
    else:
        return "Minimal"


def validate_band_configuration(selected_bands: List[Band]) -> List[str]:
    """Validate band configuration and return list of warnings/errors."""
    warnings = []
    
    if not selected_bands:
        warnings.append("No bands selected for analysis")
        return warnings
    
    # Check for invalid frequency ranges
    for band in selected_bands:
        # Check if this is a receive-only band (like GNSS)
        is_rx_only = (band.tx_low == 0 and band.tx_high == 0)
        
        # Validate Tx range (skip for receive-only bands)
        if not is_rx_only and band.tx_low >= band.tx_high:
            warnings.append(f"Invalid Tx range for {band.code}: {band.tx_low} >= {band.tx_high}")
            
        # Validate Rx range (always required)
        if band.rx_low >= band.rx_high:
            warnings.append(f"Invalid Rx range for {band.code}: {band.rx_low} >= {band.rx_high}")
            
        # Validate positive frequencies (allow 0 for Tx in receive-only bands)
        if (not is_rx_only and band.tx_low <= 0) or band.rx_low <= 0:
            warnings.append(f"Invalid frequency values for {band.code}: frequencies must be positive")
    
    # Check for suspicious configurations
    for band in selected_bands:
        # Check if this is a receive-only band
        is_rx_only = (band.tx_low == 0 and band.tx_high == 0)
        
        if not is_rx_only:
            tx_bw = band.tx_high - band.tx_low
            if tx_bw > 1000:  # > 1 GHz
                warnings.append(f"Very wide Tx band for {band.code}: {tx_bw:.1f} MHz")
                
        rx_bw = band.rx_high - band.rx_low
        if rx_bw > 1000:  # > 1 GHz
            warnings.append(f"Very wide Rx band for {band.code}: {rx_bw:.1f} MHz")
    
    return warnings
