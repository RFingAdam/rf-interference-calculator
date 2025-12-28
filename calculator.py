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
                    
                    # Enhanced risk assessment with severity
                    if risk:
                        risk_symbol, severity = assess_risk_severity(freq, victim.code, b.code, f"{order}H")
                    else:
                        risk_symbol, severity = "✅", 0
                    
                    results.append(dict(
                        Type=f"{order}H",
                        Product_Subtype="Harmonic",
                        Formula=f"{order}×Tx_{'low' if edge==b.tx_low else 'high'}({b.code})",
                        Frequency_MHz=round(freq, 2),
                        Aggressors=b.code,
                        Victims=victim.code if risk else '',
                        Risk=risk_symbol,
                        Severity=severity,
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
                                    
                                    # Enhanced risk assessment with severity
                                    if risk:
                                        risk_symbol, severity = assess_risk_severity(freq_plus_minus, victim.code, f"{b1.code}, {b2.code}", "IM2")
                                    else:
                                        risk_symbol, severity = "✅", 0
                                    
                                    results.append(dict(
                                        Type="IM2",
                                        Product_Subtype="Beat Frequency",
                                        Formula=f"{b1.code}_{'low' if A==b1.tx_low else 'high'} {op_str} {b2.code}_{'low' if B==b2.tx_low else 'high'}",
                                        Frequency_MHz=round(freq_plus_minus, 2),
                                        Aggressors=f"{b1.code}, {b2.code}",
                                        Victims=victim.code if risk else '',
                                        Risk=risk_symbol,
                                        Severity=severity,
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
                                        
                                        # Enhanced risk assessment with severity
                                        if risk:
                                            risk_symbol, severity = assess_risk_severity(freq_reverse, victim.code, f"{b1.code}, {b2.code}", "IM2")
                                        else:
                                            risk_symbol, severity = "✅", 0
                                        
                                        results.append(dict(
                                            Type="IM2",
                                            Product_Subtype="Beat Frequency",
                                            Formula=f"{b2.code}_{'low' if B==b2.tx_low else 'high'} - {b1.code}_{'low' if A==b1.tx_low else 'high'}",
                                            Frequency_MHz=round(freq_reverse, 2),
                                            Aggressors=f"{b1.code}, {b2.code}",
                                            Victims=victim.code if risk else '',
                                            Risk=risk_symbol,
                                            Severity=severity,
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
                            
                            # Enhanced risk assessment with severity
                            if risk:
                                risk_symbol, severity = assess_risk_severity(freq1, victim.code, f"{b1.code}, {b2.code}", "IM3")
                            else:
                                risk_symbol, severity = "✅", 0
                            
                            results.append(dict(
                                Type="IM3",
                                Product_Subtype="Fundamental-only",
                                Formula=f"2×{b1.code}_{'low' if A==b1.tx_low else 'high'} {'+' if sign>0 else '-'} {b2.code}_{'low' if B==b2.tx_low else 'high'}",
                                Frequency_MHz=round(freq1, 2),
                                Aggressors=f"{b1.code}, {b2.code}",
                                Victims=victim.code if risk else '',
                                Risk=risk_symbol,
                                Severity=severity,
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
                            
                            # Enhanced risk assessment with severity
                            if risk:
                                risk_symbol, severity = assess_risk_severity(freq2, victim.code, f"{b1.code}, {b2.code}", "IM3")
                            else:
                                risk_symbol, severity = "✅", 0
                            
                            results.append(dict(
                                Type="IM3",
                                Product_Subtype="Fundamental-only",
                                Formula=f"2×{b2.code}_{'low' if B==b2.tx_low else 'high'} {'+' if sign>0 else '-'} {b1.code}_{'low' if A==b1.tx_low else 'high'}",
                                Frequency_MHz=round(freq2, 2),
                                Aggressors=f"{b1.code}, {b2.code}",
                                Victims=victim.code if risk else '',
                                Risk=risk_symbol,
                                Severity=severity,
                                Details=f"IM3 (Fundamental-only): 2×{B} {'+' if sign>0 else '-'} {A} = {freq2:.1f} MHz (B={b2.code}, A={b1.code})",
                            ))
            # Mixed 2nd-harmonic/fundamental (2*(2A) ± B = 4A ± B, 2*(2B) ± A = 4B ± A)
            # Note: These are 5th-order products (4+1=5), classified as IM5
            for A in A_edges:
                for B in B_edges:
                    for sign in [-1, 1]:
                        freq3 = 2*(2*A) + sign*B
                        for victim in selected_bands:
                            rx_low = victim.rx_low - guard
                            rx_high = victim.rx_high + guard
                            risk = rx_low <= freq3 <= rx_high

                            # Enhanced risk assessment with severity
                            if risk:
                                risk_symbol, severity = assess_risk_severity(freq3, victim.code, f"{b1.code}, {b2.code}", "IM5")
                            else:
                                risk_symbol, severity = "✅", 0

                            results.append(dict(
                                Type="IM5",
                                Product_Subtype="2H×A ± B (Mixed Harmonic)",
                                Formula=f"4×{b1.code}_{'low' if A==b1.tx_low else 'high'} {'+' if sign>0 else '-'} {b2.code}_{'low' if B==b2.tx_low else 'high'}",
                                Frequency_MHz=round(freq3, 2),
                                Aggressors=f"{b1.code}, {b2.code}",
                                Victims=victim.code if risk else '',
                                Risk=risk_symbol,
                                Severity=severity,
                                Details=f"IM5 (2H of A vs Fundamental B): 4×{A} {'+' if sign>0 else '-'} {B} = {freq3:.1f} MHz (A={b1.code}, B={b2.code})",
                            ))
            for B in B_edges:
                for A in A_edges:
                    for sign in [-1, 1]:
                        freq4 = 2*(2*B) + sign*A
                        for victim in selected_bands:
                            rx_low = victim.rx_low - guard
                            rx_high = victim.rx_high + guard
                            risk = rx_low <= freq4 <= rx_high

                            # Enhanced risk assessment with severity
                            if risk:
                                risk_symbol, severity = assess_risk_severity(freq4, victim.code, f"{b1.code}, {b2.code}", "IM5")
                            else:
                                risk_symbol, severity = "✅", 0

                            results.append(dict(
                                Type="IM5",
                                Product_Subtype="2H×B ± A (Mixed Harmonic)",
                                Formula=f"4×{b2.code}_{'low' if B==b2.tx_low else 'high'} {'+' if sign>0 else '-'} {b1.code}_{'low' if A==b1.tx_low else 'high'}",
                                Frequency_MHz=round(freq4, 2),
                                Aggressors=f"{b1.code}, {b2.code}",
                                Victims=victim.code if risk else '',
                                Risk=risk_symbol,
                                Severity=severity,
                                Details=f"IM5 (2H of B vs Fundamental A): 4×{B} {'+' if sign>0 else '-'} {A} = {freq4:.1f} MHz (B={b2.code}, A={b1.code})",
                            ))
            # 2nd Harmonic of both (2A ± 2B, 2B ± 2A)
            # Note: These are 4th-order products (2+2=4), classified as IM4
            for A in A_edges:
                for B in B_edges:
                    for sign in [-1, 1]:
                        freq5 = 2*A + sign*2*B
                        for victim in selected_bands:
                            rx_low = victim.rx_low - guard
                            rx_high = victim.rx_high + guard
                            risk = rx_low <= freq5 <= rx_high

                            # Enhanced risk assessment with severity
                            if risk:
                                risk_symbol, severity = assess_risk_severity(freq5, victim.code, f"{b1.code}, {b2.code}", "IM4")
                            else:
                                risk_symbol, severity = "✅", 0

                            results.append(dict(
                                Type="IM4",
                                Product_Subtype="2H×A ± 2H×B (Double Harmonic)",
                                Formula=f"2×{b1.code}_{'low' if A==b1.tx_low else 'high'} {'+' if sign>0 else '-'} 2×{b2.code}_{'low' if B==b2.tx_low else 'high'}",
                                Frequency_MHz=round(freq5, 2),
                                Aggressors=f"{b1.code}, {b2.code}",
                                Victims=victim.code if risk else '',
                                Risk=risk_symbol,
                                Severity=severity,
                                Details=f"IM4 (2H of A vs 2H of B): 2×{A} {'+' if sign>0 else '-'} 2×{B} = {freq5:.1f} MHz (A={b1.code}, B={b2.code})",
                            ))
            for B in B_edges:
                for A in A_edges:
                    for sign in [-1, 1]:
                        freq6 = 2*B + sign*2*A
                        for victim in selected_bands:
                            rx_low = victim.rx_low - guard
                            rx_high = victim.rx_high + guard
                            risk = rx_low <= freq6 <= rx_high

                            # Enhanced risk assessment with severity
                            if risk:
                                risk_symbol, severity = assess_risk_severity(freq6, victim.code, f"{b1.code}, {b2.code}", "IM4")
                            else:
                                risk_symbol, severity = "✅", 0

                            results.append(dict(
                                Type="IM4",
                                Product_Subtype="2H×B ± 2H×A (Double Harmonic)",
                                Formula=f"2×{b2.code}_{'low' if B==b2.tx_low else 'high'} {'+' if sign>0 else '-'} 2×{b1.code}_{'low' if A==b1.tx_low else 'high'}",
                                Frequency_MHz=round(freq6, 2),
                                Aggressors=f"{b1.code}, {b2.code}",
                                Victims=victim.code if risk else '',
                                Risk=risk_symbol,
                                Severity=severity,
                                Details=f"IM4 (2H of B vs 2H of A): 2×{B} {'+' if sign>0 else '-'} 2×{A} = {freq6:.1f} MHz (B={b2.code}, A={b1.code})",
                            ))
            # IM4 (2f1+2f2, 3f1+f2, f1+3f2) - Standard higher-order products
            if imd4:
                for A in A_edges:
                    for B in B_edges:
                        # Standard IM4: 2f1+2f2
                        freq4_std = 2*A + 2*B
                        for victim in selected_bands:
                            rx_low = victim.rx_low - guard
                            rx_high = victim.rx_high + guard
                            risk = rx_low <= freq4_std <= rx_high

                            # Enhanced risk assessment with severity
                            if risk:
                                risk_symbol, severity = assess_risk_severity(freq4_std, victim.code, f"{b1.code}, {b2.code}", "IM4")
                            else:
                                risk_symbol, severity = "✅", 0

                            results.append(dict(
                                Type="IM4",
                                Product_Subtype="Standard (2f₁+2f₂)",
                                Formula=f"2×{b1.code}_{'low' if A==b1.tx_low else 'high'} + 2×{b2.code}_{'low' if B==b2.tx_low else 'high'}",
                                Frequency_MHz=round(freq4_std, 2),
                                Aggressors=f"{b1.code}, {b2.code}",
                                Victims=victim.code if risk else '',
                                Risk=risk_symbol,
                                Severity=severity,
                                Details=f"IM4: 2×{A} + 2×{B} = {freq4_std:.1f} MHz (A={b1.code}, B={b2.code})",
                            ))

                        # Extended IM4: 3f1+f2 and f1+3f2
                        for coeff1, coeff2 in [(3, 1), (1, 3)]:
                            freq4_ext = coeff1*A + coeff2*B
                            for victim in selected_bands:
                                rx_low = victim.rx_low - guard
                                rx_high = victim.rx_high + guard
                                risk = rx_low <= freq4_ext <= rx_high

                                # Enhanced risk assessment with severity
                                if risk:
                                    risk_symbol, severity = assess_risk_severity(freq4_ext, victim.code, f"{b1.code}, {b2.code}", "IM4")
                                else:
                                    risk_symbol, severity = "✅", 0

                                results.append(dict(
                                    Type="IM4",
                                    Product_Subtype=f"Extended ({coeff1}f₁+{coeff2}f₂)",
                                    Formula=f"{coeff1}×{b1.code}_{'low' if A==b1.tx_low else 'high'} + {coeff2}×{b2.code}_{'low' if B==b2.tx_low else 'high'}",
                                    Frequency_MHz=round(freq4_ext, 2),
                                    Aggressors=f"{b1.code}, {b2.code}",
                                    Victims=victim.code if risk else '',
                                    Risk=risk_symbol,
                                    Severity=severity,
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

                                # Enhanced risk assessment with severity
                                if risk:
                                    risk_symbol, severity = assess_risk_severity(freq5_std, victim.code, f"{b1.code}, {b2.code}", "IM5")
                                else:
                                    risk_symbol, severity = "✅", 0

                                results.append(dict(
                                    Type="IM5",
                                    Product_Subtype="Standard (3f₁±2f₂)",
                                    Formula=f"3×{b1.code}_{'low' if A==b1.tx_low else 'high'} {'+' if sign>0 else '-'} 2×{b2.code}_{'low' if B==b2.tx_low else 'high'}",
                                    Frequency_MHz=round(freq5_std, 2),
                                    Aggressors=f"{b1.code}, {b2.code}",
                                    Victims=victim.code if risk else '',
                                    Risk=risk_symbol,
                                    Severity=severity,
                                    Details=f"IM5: 3×{A} {'+' if sign>0 else '-'} 2×{B} = {freq5_std:.1f} MHz (A={b1.code}, B={b2.code})",
                                ))

                        # Extended IM5: 2f1±3f2
                        for sign in [-1, 1]:
                            freq5_ext = 2*A + sign*3*B
                            for victim in selected_bands:
                                rx_low = victim.rx_low - guard
                                rx_high = victim.rx_high + guard
                                risk = rx_low <= freq5_ext <= rx_high

                                # Enhanced risk assessment with severity
                                if risk:
                                    risk_symbol, severity = assess_risk_severity(freq5_ext, victim.code, f"{b1.code}, {b2.code}", "IM5")
                                else:
                                    risk_symbol, severity = "✅", 0

                                results.append(dict(
                                    Type="IM5",
                                    Product_Subtype="Extended (2f₁±3f₂)",
                                    Formula=f"2×{b1.code}_{'low' if A==b1.tx_low else 'high'} {'+' if sign>0 else '-'} 3×{b2.code}_{'low' if B==b2.tx_low else 'high'}",
                                    Frequency_MHz=round(freq5_ext, 2),
                                    Aggressors=f"{b1.code}, {b2.code}",
                                    Victims=victim.code if risk else '',
                                    Risk=risk_symbol,
                                    Severity=severity,
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

                                # Enhanced risk assessment with severity
                                if risk:
                                    risk_symbol, severity = assess_risk_severity(freq7, victim.code, f"{b1.code}, {b2.code}", "IM7")
                                else:
                                    risk_symbol, severity = "✅", 0

                                results.append(dict(
                                    Type="IM7",
                                    Product_Subtype="Standard (4f₁±3f₂)",
                                    Formula=f"4×{b1.code}_{'low' if A==b1.tx_low else 'high'} {'+' if sign>0 else '-'} 3×{b2.code}_{'low' if B==b2.tx_low else 'high'}",
                                    Frequency_MHz=round(freq7, 2),
                                    Aggressors=f"{b1.code}, {b2.code}",
                                    Victims=victim.code if risk else '',
                                    Risk=risk_symbol,
                                    Severity=severity,
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

                # Enhanced risk assessment with severity
                if aclr_risk:
                    risk_symbol, severity = assess_risk_severity(b2.rx_low, b2.code, b1.code, "ACLR")
                else:
                    risk_symbol, severity = "✅", 0

                # Show the gap distance as the frequency (more meaningful than average)
                gap_mhz = abs(b1.tx_high - b2.rx_low)
                results.append(dict(
                    Type="ACLR",
                    Product_Subtype="Adjacent-channel",
                    Formula=f"{b1.code}_tx_high vs {b2.code}_rx_low",
                    Frequency_MHz=round(gap_mhz, 2),
                    Aggressors=b1.code,
                    Victims=b2.code if aclr_risk else '',
                    Risk=risk_symbol,
                    Severity=severity,
                    Details=f"ACLR: {b1.tx_high} MHz vs {b2.rx_low} MHz (gap: {gap_mhz:.1f} MHz)",
                ))
    # Deduplicate: focus on mathematical uniqueness rather than descriptive differences
    seen = set()
    deduped = []
    for r in results:
        # Update legacy risk symbols with severity assessment - ONLY for products with actual victims
        if r.get('Risk') in ['⚠️', '✓'] and 'Severity' not in r:
            freq = r.get('Frequency_MHz', 0)
            victim = r.get('Victims', '')
            aggressors = r.get('Aggressors', '')
            product_type = r.get('Type', '')
            
            # Only assess risk for products that actually have victims (real interference)
            if r.get('Risk') == '⚠️' and victim and victim.strip():  # Must have actual victims
                risk_symbol, severity = assess_risk_severity(freq, victim, aggressors, product_type)
                r['Risk'] = risk_symbol
                r['Severity'] = severity
            elif r.get('Risk') == '✓':
                r['Risk'] = '✅'  # Convert old safe symbol to new emoji
                r['Severity'] = 1
        
        # Create unique key based on actual mathematical content
        freq = r.get('Frequency_MHz', 0)
        aggressors = tuple(sorted(r.get('Aggressors', '').split(', '))) if r.get('Aggressors') else ()
        victims = r.get('Victims', '')
        
        # For mathematical uniqueness, ignore descriptive Product_Subtype differences
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
        # Sort by severity (high to low), then by signal priority, then by other factors
        severity = r.get('Severity', 0)
        # Convert severity to sort priority (higher severity = lower sort value = appears first)
        severity_priority = 6 - severity if severity > 0 else 10  # Risk items first, then safe items
        signal_priority = get_signal_level_priority(r)
        freq = r.get('Frequency_MHz', 0)
        return (severity_priority, signal_priority, str(r.get('Type')), str(r.get('Formula')), freq)
    
    deduped.sort(key=sort_key)
    
    # Filter out physically invalid frequencies (negative or zero)
    valid_results = []
    invalid_count = 0
    
    for result in deduped:
        freq = result.get('Frequency_MHz', 0)
        if freq > 0:  # Only positive frequencies are physically meaningful in RF
            valid_results.append(result)
        else:
            invalid_count += 1
    
    # Add note about filtered frequencies if any were removed
    if invalid_count > 0:
        overlap_alerts.append(f"Note: {invalid_count} products with invalid frequencies (≤ 0 MHz) were filtered out")
    
    return valid_results, overlap_alerts


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


def assess_risk_severity(frequency: float, victim_code: str, aggressors: str, product_type: str) -> Tuple[str, int]:
    """
    Assess risk severity based on frequency, victim, and interference type.
    Returns (risk_symbol, severity_level) where severity_level is 1-5 (5 = most critical).
    """
    # Critical frequency bands for different services (match band definitions exactly)
    critical_bands = {
        # GPS/GNSS (high precision navigation) - match bands.py definitions
        'GNSS_L1': (1559.0, 1610.0, 5),  # Full GNSS L1/E1 band (expanded range)
        'GNSS_L2': (1210.0, 1250.0, 5),  # Full GNSS L2 band (expanded range)
        'GNSS_L5': (1160.0, 1195.0, 4),  # Full GNSS L5/E5 band (expanded range)
        
        # ISM bands (unlicensed, high interference potential)
        'ISM_24': (2400.0, 2500.0, 4),   # 2.4 GHz ISM (BLE, Wi-Fi, etc.)
        'ISM_58': (5725.0, 5875.0, 3),   # 5.8 GHz ISM
        'WiFi_24': (2400.0, 2495.0, 4),  # Wi-Fi 2.4 GHz
        'WiFi_5': (5150.0, 5925.0, 3),   # Wi-Fi 5/6 GHz (expanded)
        'BLE_ISM': (2402.0, 2485.0, 4),  # BLE in ISM band
        
        # Public Safety (critical communications)
        'FirstNet': (755.0, 770.0, 5),   # FirstNet uplink (expanded)
        'PublicSafety': (758.0, 780.0, 5), # Public safety bands (expanded)
        
        # Cellular uplinks (interference affects base stations)
        'Cellular_UL': (820.0, 900.0, 4), # Cellular uplinks (expanded)
        'LTE_Low': (700.0, 900.0, 3),     # LTE low bands  
        'LTE_Mid': (1700.0, 2200.0, 3),   # LTE mid bands
        'LTE_High': (2300.0, 2700.0, 2),  # LTE high bands
    }
    
    # Start with conservative default severity
    severity = 1  # Start conservative like GitHub version
    risk_symbol = "🔵"  # Default to low risk (blue) for products with victims
    
    # Assess victim criticality - more conservative matching
    victim_criticality = {
        'GNSS': 5, 'GPS': 5,  # Any GNSS reference is critical
        'LTE_B13': 5, 'LTE_B14': 5,  # Public safety LTE bands
        'BLE': 3,     # BLE less aggressive than before
        'WiFi': 3,    # WiFi less aggressive
        'Wi-Fi': 3,   # Alternative Wi-Fi spelling
        'HaLow': 2,   # Wi-Fi HaLow
    }
    
    # Get victim base severity - only for real victims (not GENERIC)
    for victim_pattern, crit_level in victim_criticality.items():
        if victim_pattern.upper() in victim_code.upper():
            severity = max(severity, crit_level)
            break
    
    # Check if frequency falls in critical bands - more conservative like GitHub
    for band_name, (low, high, band_severity) in critical_bands.items():
        if low <= frequency <= high:
            severity = max(severity, band_severity)
            # GPS interference is always critical but don't double-boost
            if 'GNSS' in band_name and 'GNSS' in victim_code.upper():
                severity = 5  # Set to critical for GPS interference
            break
    
    # Product type severity modifiers - more conservative like GitHub version
    if product_type == '3H':  # 3rd harmonics 
        severity = min(severity + 1, 5)  # Conservative modifier
    elif product_type == '2H':  # 2nd harmonics
        severity = min(severity + 1, 5)  # Conservative modifier
    elif product_type == 'IM2':  # IM2 products
        severity = min(severity + 1, 5)
    elif product_type == 'IM3':  # IM3 products
        severity = min(severity + 1, 5)
    elif product_type in ['IM4', 'IM5', 'IM7']:  # Higher order typically weaker
        severity = max(severity, 1)  # Don't reduce below 1
    
    # Aggressor analysis - conservative approach
    if ',' in aggressors or ' and ' in aggressors.lower():
        severity = min(severity + 1, 5)  # Multiple aggressors = higher risk
    
    # Special critical cases - only for actual public safety bands
    if 'LTE_B13' in aggressors or 'LTE_B14' in aggressors:
        severity = min(severity + 1, 5)
    
    # ISM band coexistence issues - more conservative
    if ('BLE' in victim_code.upper() and 'WIFI' in aggressors.upper()) or \
       ('WIFI' in victim_code.upper() and 'BLE' in aggressors.upper()):
        if 2400 <= frequency <= 2500:
            severity = min(severity + 1, 5)  # Conservative ISM boost
    
    # GPS interference - conservative boost only for actual GPS victims
    if any(gps_term in victim_code.upper() for gps_term in ['GNSS', 'GPS']) and any(gps_freq in str(frequency) for gps_freq in ['1575', '1227', '1176']):
        severity = min(severity + 1, 5)  # GPS victims get conservative boost
    
    # Determine risk symbol based on severity
    if severity >= 5:
        risk_symbol = "🔴"  # Critical - Red circle
    elif severity >= 4:
        risk_symbol = "🟠"  # High - Orange circle  
    elif severity >= 3:
        risk_symbol = "🟡"  # Medium - Yellow circle
    elif severity >= 2:
        risk_symbol = "🔵"  # Low - Blue circle
    else:
        risk_symbol = "✅"  # Very Low/Safe - Green check
    
    return risk_symbol, severity


def assess_risk_severity_quantitative(
    interference_power_dbm: float,
    victim_sensitivity_dbm: float,
    desensitization_db: float,
    victim_code: str,
    product_type: str
) -> Tuple[str, int, str]:
    """
    PhD-level quantitative risk assessment based on actual power levels.

    This replaces the frequency-only approach with proper RF engineering metrics:
    - Primary driver: Desensitization (I/N method)
    - Secondary: Margin above sensitivity
    - Modifier: Victim criticality (GNSS gets stricter thresholds)

    Args:
        interference_power_dbm: Interference power at victim RX input (dBm)
        victim_sensitivity_dbm: Victim receiver sensitivity (dBm)
        desensitization_db: Calculated receiver desensitization (dB)
        victim_code: Victim band code (e.g., 'GNSS_L1', 'WiFi_2G')
        product_type: Interference product type (e.g., 'IM3', '2H')

    Returns:
        (risk_symbol, severity 1-5, reason_string)
    """
    # Calculate interference margin for additional context
    margin_db = victim_sensitivity_dbm - interference_power_dbm

    # GNSS/GPS thresholds (most sensitive receivers, safety-critical)
    # Based on 3GPP TS 36.101 and GPS receiver performance standards
    if 'GNSS' in victim_code.upper() or 'GPS' in victim_code.upper():
        if desensitization_db >= 8.0:
            return ('🔴', 5, f'GPS dead zone ({desensitization_db:.1f}dB desense, {interference_power_dbm:.0f}dBm)')
        elif desensitization_db >= 3.0:
            return ('🟠', 4, f'GPS acquisition degraded ({desensitization_db:.1f}dB desense)')
        elif desensitization_db >= 1.0:
            return ('🟡', 3, f'GPS tracking affected ({desensitization_db:.1f}dB desense)')
        elif desensitization_db >= 0.5:
            return ('🔵', 2, f'Minor GPS impact ({desensitization_db:.1f}dB desense)')
        else:
            return ('✅', 1, f'Negligible ({desensitization_db:.2f}dB)')

    # Public Safety bands (FirstNet, LTE B13/B14)
    elif any(ps in victim_code.upper() for ps in ['B13', 'B14', 'FIRSTNET', 'PUBLIC']):
        if desensitization_db >= 6.0:
            return ('🔴', 5, f'Public safety critical ({desensitization_db:.1f}dB desense)')
        elif desensitization_db >= 3.0:
            return ('🟠', 4, f'Public safety degraded ({desensitization_db:.1f}dB desense)')
        elif desensitization_db >= 1.0:
            return ('🟡', 3, f'Public safety impacted ({desensitization_db:.1f}dB desense)')
        elif desensitization_db >= 0.5:
            return ('🔵', 2, f'Minor public safety impact ({desensitization_db:.1f}dB)')
        else:
            return ('✅', 1, f'Negligible ({desensitization_db:.2f}dB)')

    # Standard wireless technologies (WiFi, LTE, BLE, etc.)
    else:
        if desensitization_db >= 12.0:
            return ('🔴', 5, f'Receiver saturation ({desensitization_db:.1f}dB desense, {interference_power_dbm:.0f}dBm)')
        elif desensitization_db >= 6.0:
            return ('🟠', 4, f'Significant degradation ({desensitization_db:.1f}dB desense)')
        elif desensitization_db >= 3.0:
            return ('🟡', 3, f'Performance loss ({desensitization_db:.1f}dB desense)')
        elif desensitization_db >= 1.0:
            return ('🔵', 2, f'Minor degradation ({desensitization_db:.1f}dB desense)')
        else:
            return ('✅', 1, f'Negligible ({desensitization_db:.2f}dB)')


def calculate_desensitization(
    interference_power_dbm: float,
    noise_floor_dbm: float
) -> float:
    """
    Calculate receiver desensitization using standard I/N method.

    Formula: Desens_dB = 10 × log₁₀(1 + I/N)

    Where:
    - I = Interference power (linear)
    - N = Noise floor power (linear)

    Args:
        interference_power_dbm: Interference power at victim input (dBm)
        noise_floor_dbm: Receiver noise floor (dBm)

    Returns:
        Desensitization in dB (increase in effective noise floor)
    """
    import math

    if interference_power_dbm <= noise_floor_dbm - 20:
        # Interference > 20 dB below noise floor = negligible
        return 0.0

    # I/N ratio in linear terms
    i_over_n_linear = 10 ** ((interference_power_dbm - noise_floor_dbm) / 10.0)

    # Standard desensitization formula
    desensitization_db = 10 * math.log10(1 + i_over_n_linear)

    return desensitization_db


def get_victim_noise_floor(victim_code: str, bandwidth_hz: float = None) -> float:
    """
    Get estimated noise floor for different receiver types.

    Noise floor = kTB + NF = -174 dBm/Hz + 10*log10(BW) + NF

    Args:
        victim_code: Victim band code
        bandwidth_hz: Optional bandwidth override

    Returns:
        Estimated noise floor in dBm
    """
    import math

    # Technology-specific defaults
    # Format: (bandwidth_hz, noise_figure_db)
    tech_params = {
        'GNSS': (2e6, 2.0),     # 2 MHz, 2 dB NF (GPS front-end)
        'GPS': (2e6, 2.0),
        'LTE': (10e6, 6.0),    # 10 MHz, 6 dB NF
        'WIFI': (20e6, 6.0),   # 20 MHz, 6 dB NF
        'WI-FI': (20e6, 6.0),
        'BLE': (1e6, 8.0),     # 1 MHz, 8 dB NF
        'BLUETOOTH': (1e6, 8.0),
        'HALOW': (1e6, 7.0),   # 1 MHz, 7 dB NF
        'LORA': (125e3, 6.0),  # 125 kHz, 6 dB NF
        'ZIGBEE': (2e6, 8.0),  # 2 MHz, 8 dB NF
    }

    # Find matching technology
    bw_hz = 10e6  # Default 10 MHz
    nf_db = 6.0   # Default 6 dB NF

    for tech, (default_bw, default_nf) in tech_params.items():
        if tech in victim_code.upper():
            bw_hz = default_bw
            nf_db = default_nf
            break

    if bandwidth_hz is not None:
        bw_hz = bandwidth_hz

    # Calculate noise floor: -174 + 10*log10(BW) + NF
    thermal_noise = -174.0 + 10 * math.log10(bw_hz)
    noise_floor = thermal_noise + nf_db

    return noise_floor
