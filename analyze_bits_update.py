#!/usr/bin/env python
"""
Analýza: Je potrebné aktualizovať pro a bits pre VŠETKY body
alebo stačí iba pre pozorovaný bod?

Hypotéza: Ak aktualizujem iba aktívny bod, ostatné body majú
zastaranú pro hodnotu, čo spôsobuje chybu v bits.
"""

import sys
sys.path.insert(0, 'src')

from idata.imarkov import IMarkov
import math

print("="*80)
print("ANALÝZA: Aktualizovanie pro a bits - iba aktívny bod vs. všetky body")
print("="*80)

# Sekvencia na testovanie
sequence = [1, 2, 1, 2, 1, 2, 1]

# Scenario 1: Aktuálna implementácia (všetky body)
print("\n1. AKTUÁLNA IMPLEMENTÁCIA (všetky body)")
print("-" * 80)
mrk_all = IMarkov(name="all_points", dim=1)

for i, val in enumerate(sequence):
    mrk_all.observe(val)
    bits_current = mrk_all.bits
    totObs = mrk_all.totObs

    # Vypočítaj Shannon entropy manuálne
    bits_manual = 0.0
    for point in mrk_all.points:
        pro = point._vals['pro']
        if pro > 0:
            bits_manual += -pro * math.log2(pro)

    print(f"Step {i+1}: observe({val}), totObs={totObs:2d}, bits={bits_current:8.4f}, manual_bits={bits_manual:8.4f}, diff={abs(bits_current-bits_manual):8.6f}")

    # Vypíš detaily bodov
    for j, point in enumerate(mrk_all.points):
        print(f"       Point {j}: pos={point.pos('x')}, obs={point._vals['obs']:2d}, pro={point._vals['pro']:.4f}, bit={point._vals['bit']:.4f}")

print(f"\nFINAL bits (all_points): {mrk_all.bits:.6f}")
print(f"FINAL manual bits:       {bits_manual:.6f}")
print(f"ERROR:                   {abs(mrk_all.bits - bits_manual):.8f}")

# Scenario 2: Iba aktívny bod (hypotetický - potrebujeme upraviť kód)
print("\n" + "="*80)
print("2. POROVNANIE: Shannon entropy axiomy")
print("="*80)
print("\nShannon entropy ma tieto vlastnosti:")
print("  S = -SUM(p_i * log2(p_i))  ... suma cez VSETKY mozne stavy")
print("")
print("Klucove: Shannon entropy zavisi od VSETKYCH p_i, nie iba od zmeny")
print("")
print("Ked sa zmeni totObs zo N na N+1:")
print("  - Aktivny bod: obs_a vzrastie -> pro_a = obs_a/(N+1)")
print("  - Ostatne body: obs_i ostava -> pro_i = obs_i/(N+1) < obs_i/N")
print("")
print("Vsetky p_i sa zmenili, vsetky sa musia aktualizovat!")

# Scenario 3: Konkrétny príklad
print("\n" + "="*80)
print("3. KONKRÉTNY PRÍKLAD: Čo sa stane, ak aktualizujem iba aktívny bod?")
print("="*80)

sequence_simple = [1, 1, 2]

print("\nSekvencia: [1, 1, 2]")
print("\nKrok 1: observe(1)")
mrk_test = IMarkov(name="test", dim=1)
mrk_test.observe(1)
p1_after_obs1 = mrk_test.points[0]._vals['pro']
bits_after_obs1 = mrk_test.bits
print(f"  Point 1: obs=1, pro=1.0, bit=-1.0*log2(1.0)=0.0")
print(f"  Shannon entropy S = 0.0")

print("\nKrok 2: observe(1)")
print("  SPRAVNE (vsetky body):")
print("    totObs: 1 -> 2")
print("    Point 1: pro = 2/2 = 1.0, bit = -1.0*log2(1.0) = 0.0")
print("    Shannon entropy S = 0.0")
mrk_test.observe(1)
bits_after_obs2_correct = mrk_test.bits
print(f"  KOREKTNE: bits = {bits_after_obs2_correct:.4f}")

print("\nKrok 3: observe(2)")
print("  SPRAVNE (vsetky body):")
print("    totObs: 2 -> 3")
print("    Point 1: obs=2, pro = 2/3 = 0.667, bit = -0.667*log2(0.667) = 0.390")
print("    Point 2: obs=1, pro = 1/3 = 0.333, bit = -0.333*log2(0.333) = 0.528")
print("    Shannon entropy S = 0.390 + 0.528 = 0.918")
mrk_test.observe(2)
bits_after_obs3_correct = mrk_test.bits

# Manuálny výpočet
bits_manual_obs3 = 0
for point in mrk_test.points:
    pro = point._vals['pro']
    if pro > 0:
        bits_manual_obs3 += -pro * math.log2(pro)

print(f"  KOREKTNE (vsetky body): bits = {bits_after_obs3_correct:.4f}")
print(f"  MANUALNY VYPOCET:       bits = {bits_manual_obs3:.4f}")

print("\n" + "="*80)
print("4. ZÁVER")
print("="*80)
print("\n✅ Aktualizovanie pro a bits pre VSETKY body JE NUTNE")
print("\nDuvod:")
print("  1. Shannon entropy S = -SUM(p_i * log2(p_i)) zavisi od VSETKYCH p_i")
print("  2. Ked sa zmeni totObs, vsetky p_i sa zmenili (p_i = obs_i / totObs)")
print("  3. Bits prispevok kazdeho bodu sa musi recalc: bit_i = -p_i * log2(p_i)")
print("  4. Inkrementalna aktualizacia: Delta_S_i = new_bit_i - old_bit_i")
print("  5. Celkova zmena: Delta_S_total = SUM(Delta_S_i) pre VSETKY body")
print("\n❌ Keby som aktualizoval len aktivny bod:")
print("  - Ostatne body by mali zastaranou pro (obs_i / N namiesto obs_i / (N+1))")
print("  - Ich bits prispevky by boli nespravne")
print("  - Chyba by sa KUMULOVALA s kazdym novym pozorovanim")
print("  - Final Shannon entropy by bola nespravna")
print("\nEfektivita vs. Spravnost:")
print("  - Aktualizovanie vsetkych bodov: O(pocet_bodov)")
print("  - Napr. len 100 roznych hodnot = iba 100 aktualizacii")
print("  - Stoji za to pre matematicku korektnost")
