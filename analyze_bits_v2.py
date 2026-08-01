#!/usr/bin/env python
"""
Analyze: Is it necessary to update pro and bits for ALL points
or just for the observed point?

Hypothesis: If I update only the active point, other points have
outdated pro values, which causes an error in bits.
"""

import sys
sys.path.insert(0, 'src')

from idata.imarkov import IMarkov
import math

print("="*80)
print("ANALYSIS: Updating pro and bits - only active point vs. all points")
print("="*80)

# Sequence to test
sequence = [1, 2, 1, 2, 1, 2, 1]

# Scenario 1: Current implementation (all points)
print("\n1. CURRENT IMPLEMENTATION (all points)")
print("-" * 80)
mrk_all = IMarkov(name="all_points", dim=1)

for i, val in enumerate(sequence):
    mrk_all.observe(val)
    bits_current = mrk_all.bits
    totObs = mrk_all.totObs

    # Calculate Shannon entropy manually
    bits_manual = 0.0
    for point in mrk_all.points:
        pro = point._vals['pro']
        if pro > 0:
            bits_manual += -pro * math.log2(pro)

    print(f"Step {i+1}: observe({val}), totObs={totObs:2d}, bits={bits_current:8.4f}, manual_bits={bits_manual:8.4f}, diff={abs(bits_current-bits_manual):8.6f}")

    # Print point details
    for j, point in enumerate(mrk_all.points):
        print(f"       Point {j}: pos={point.pos('x')}, obs={point._vals['obs']:2d}, pro={point._vals['pro']:.4f}, bit={point._vals['bit']:.4f}")

print(f"\nFINAL bits (all_points): {mrk_all.bits:.6f}")
print(f"FINAL manual bits:       {bits_manual:.6f}")
print(f"ERROR:                   {abs(mrk_all.bits - bits_manual):.8f}")

# Scenario 2: Mathematical explanation
print("\n" + "="*80)
print("2. COMPARISON: Shannon entropy axioms")
print("="*80)
print("\nShannon entropy has these properties:")
print("  S = -SUM(p_i * log2(p_i))  ... sum over ALL possible states")
print("")
print("KEY: Shannon entropy depends on ALL p_i, not just the change")
print("")
print("When totObs changes from N to N+1:")
print("  - Active point: obs_a increases -> pro_a = obs_a/(N+1)")
print("  - Other points: obs_i stays same -> pro_i = obs_i/(N+1) < obs_i/N")
print("")
print("ALL p_i changed, so ALL must be updated!")

# Scenario 3: Concrete example
print("\n" + "="*80)
print("3. CONCRETE EXAMPLE: What happens if I update only the active point?")
print("="*80)

sequence_simple = [1, 1, 2]

print("\nSequence: [1, 1, 2]")
print("\nStep 1: observe(1)")
mrk_test = IMarkov(name="test", dim=1)
mrk_test.observe(1)
p1_after_obs1 = mrk_test.points[0]._vals['pro']
bits_after_obs1 = mrk_test.bits
print(f"  Point 1: obs=1, pro=1.0, bit=-1.0*log2(1.0)=0.0")
print(f"  Shannon entropy S = 0.0")

print("\nStep 2: observe(1)")
print("  CORRECT (all points):")
print("    totObs: 1 -> 2")
print("    Point 1: pro = 2/2 = 1.0, bit = -1.0*log2(1.0) = 0.0")
print("    Shannon entropy S = 0.0")
mrk_test.observe(1)
bits_after_obs2_correct = mrk_test.bits
print(f"  CORRECT: bits = {bits_after_obs2_correct:.4f}")

print("\nStep 3: observe(2)")
print("  CORRECT (all points):")
print("    totObs: 2 -> 3")
print("    Point 1: obs=2, pro = 2/3 = 0.667, bit = -0.667*log2(0.667) = 0.390")
print("    Point 2: obs=1, pro = 1/3 = 0.333, bit = -0.333*log2(0.333) = 0.528")
print("    Shannon entropy S = 0.390 + 0.528 = 0.918")
mrk_test.observe(2)
bits_after_obs3_correct = mrk_test.bits

# Manual calculation
bits_manual_obs3 = 0
for point in mrk_test.points:
    pro = point._vals['pro']
    if pro > 0:
        bits_manual_obs3 += -pro * math.log2(pro)

print(f"  CORRECT implementation: bits = {bits_after_obs3_correct:.4f}")
print(f"  MANUAL calculation:     bits = {bits_manual_obs3:.4f}")

print("\n" + "="*80)
print("4. CONCLUSION")
print("="*80)
print("\nOK: Updating pro and bits for ALL points IS NECESSARY")
print("\nReason:")
print("  1. Shannon entropy S = -SUM(p_i * log2(p_i)) depends on ALL p_i")
print("  2. When totObs changes, all p_i changed (p_i = obs_i / totObs)")
print("  3. Bits contribution of each point must be recalc: bit_i = -p_i * log2(p_i)")
print("  4. Incremental update: Delta_S_i = new_bit_i - old_bit_i")
print("  5. Total change: Delta_S_total = SUM(Delta_S_i) for ALL points")
print("\nNOT OK: If I update only the active point:")
print("  - Other points would have outdated pro (obs_i / N instead of obs_i / (N+1))")
print("  - Their bits contributions would be wrong")
print("  - ERROR WOULD ACCUMULATE with each new observation")
print("  - Final Shannon entropy would be incorrect")
print("\nEfficiency vs. Correctness:")
print("  - Updating all points: O(number_of_points)")
print("  - E.g. only 100 different values = only 100 updates")
print("  - Worth it for mathematical correctness")
print("\n" + "="*80)
print("MATHEMATICAL PROOF")
print("="*80)
print("\nLet's say we have:")
print("  - Point 1: obs_1 = 2, pro_1 = 2/3")
print("  - Point 2: obs_2 = 1, pro_2 = 1/3")
print("  - totObs = 3, bits = -(2/3)*log2(2/3) - (1/3)*log2(1/3) = 0.9183")
print("\nNow observe(Point1 again):")
print("  - totObs becomes 4")
print("  - Point 1: new_obs_1 = 3, new_pro_1 = 3/4 = 0.75")
print("  - Point 2: obs_2 = 1 (unchanged), but pro_2 MUST change to 1/4 = 0.25")
print("\nIF I DON'T UPDATE POINT 2:")
print("  - Point 2 still thinks pro_2 = 1/3 (WRONG!)")
print("  - Point 2 bits = -(1/3)*log2(1/3) = 0.5283 (WRONG, should be -0.25*log2(0.25)=0.5)")
print("  - Total bits would be wrong")
print("\nCORRECT UPDATES:")
print("  - Point 1: new_bit_1 = -0.75*log2(0.75) = 0.3113")
print("  - Point 2: new_bit_2 = -0.25*log2(0.25) = 0.5")
print("  - Total = 0.8113")
print("\n" + "="*80)
