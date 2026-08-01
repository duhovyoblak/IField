---
applyTo:
  - src/idata/imarkov.py
---

# IMarkov Analyzer - Koncept a Architektúra

## Úvod

IMarkov je **n-rozmerný Markovov analyzátor** na analýzu a generovanie sekvenčných dát. Vychádza z teórie náhodných procesov a reprezentuje závislosť medzi po sebe nasledujúcimi pozorovaniami.

## Základná Štruktúra

### self.points - Slovník Možných Hodnôt

**DÔLEŽITÉ**: `self.points` NEOBSAHUJE históriu pozorovaní, ale slovník **všetkých pozorovaných hodnôt** na tejto dimenzii.

- Každý `point` v `self.points` reprezentuje **JEDNU povolenou hodnotu pozorovania**
- Identifikátor: os `'x'` (axe value)
- Štatistika: počet pozorovaní v `_vals['obs']`

**Príklad (dim=1)**:
```
points = {
    InfoPoint(pos='x'=1): _vals['obs']=45,   _vals['mrk']=IMarkov(dim=2)
    InfoPoint(pos='x'=2): _vals['obs']=38,   _vals['mrk']=IMarkov(dim=2)
    InfoPoint(pos='x'=5): _vals['obs']=17,   _vals['mrk']=IMarkov(dim=2)
}
```

Nepredstavuje sekvenciu [1, 2, 5, 1, ...], ale: "Videli sme hodnotu 1 trikrát, hodnotu 2 dvakrát, atď."

### self.actVals - Posuvné Okno

Jedná sa o **posuvné okno dĺžky `dim`** najnovších pozorovaní:

```
dim=3, pozorovania: [1, 2, 5, 3, 4]
Po pozorovaní 1: actVals = [1]
Po pozorovaní 2: actVals = [1, 2]
Po pozorovaní 5: actVals = [1, 2, 5]
Po pozorovaní 3: actVals = [2, 5, 3]  <- posledných 3 hodnôt
Po pozorovaní 4: actVals = [5, 3, 4]  <- posledných 3 hodnôt
```

## Hierarchia Dimenzií

IMarkov tvorí **reťazec vnorených Markovov** podľa dimenzií:

```
IMarkov(dim=1)  - sleduje jednotlivé hodnoty: [1], [2], [5], ...
    └─ pre každú hodnotu x:
        IMarkov(dim=2)  - sleduje páry: [x, n], kde n je nasledujúca hodnota
            └─ pre každú páru [x, n]:
                IMarkov(dim=3)  - sleduje trojice: [x, n, m], ...
```

Vyjadruje: **"Aká je pravdepodobnosť hodnoty X po pozorovaní sekvencie [a, b, c]?"**

## Operácie s Pozorovaniami

### `observe(val: int)`

Keď sa pozoruje nová hodnota `val`:

1. **Posun okna**: `self.actVals = self.actVals[-(dim-1):] + [val]`
   - Zahodiť najstaršiu hodnotu, pridať novú

2. **Aktivovanie bodov**: `moveFwd(val)` → `_activate(actVals)`
   - Prejsť hierarchiou dimenzií
   - Nájsť/vytvoriť InfoPoints pre daný reťazec

3. **Zvýšenie počítadla**: `_vals['obs'] += 1` pre každý aktivovaný bod
   - **DÔLEŽITÉ**: Nepridáva sa NOVÝ bod, ale zvýši sa počítadlo existujúceho

4. **Aktualizovanie štatistík** pre každý bod v reťazci:
   - **Podmienená pravdepodobnosť**: `condPro = obs[bodna] / totObs[parent]`
   - **Spoločná pravdepodobnosť**: `pro = P(X_1) * P(X_2|X_1) * ... * P(X_i|...)`
     - Reprezentuje pravdepodobnosť **celého reťazca** od dimenzie 1 až po aktuálnu dimenziu
   - **Self-information bodu**: `bit = -pro * log2(pro)` (počet bitov na kódovanie)
   - **Entropia objektu**: `self.bits` sa **inkrementálne aktualizuje** (iba zmena, nie prepočet):
     ```
     oldBit = -oldPro * log2(oldPro)
     newBit = -newPro * log2(newPro)
     self.bits += (newBit - oldBit)
     ```
   - **Bezpečnosť**: Všetky `log2()` majú ochranu `if > 0` aby sa vyhnuli `log(0)`

### `_getPoint(val, create=False)` - Kľúčová Metóda

Nájde alebo vytvorí InfoPoint s osou `'x' == val`:

- **Ak bod existuje**: vrátí existujúci `InfoPoint`
- **Ak neexistuje a `create=True`**:
  - Vytvorí **nový** `InfoPoint` (prvýkrát pozorovaná hodnota)
  - Vytvorí `child IMarkov(dim-1)` pre ďalšiu dimenziu
  - Inicializuje `_vals['pro'] = 0` a `_vals['bit'] = 0`
- **Ak neexistuje a `create=False`**: vrátí `None`

**BODOVÝ BOD**: `initAdd()` sa volá len pri prvom pozorovaní hodnoty, nie pri každom pozorovaní!

## Príklad: Analýza Sekvencie

**Vstup**: pozorovania [1, 2, 1, 2, 1] s dim=2

### Priebeh observe():

```
observe(1):
  - Okno: [1]
  - Aktivuje: point(x=1) v IMarkov(dim=1)
  - obs[1] = 1, pro[1] = 1/1 = 1.0
  - bit[1] = -1.0 * log2(1.0) = 0
  - mrk[1] (dim=2): createNov, bits = 0
  - actVals = [1]

observe(2):
  - Okno: [1, 2]
  - Aktivuje: point(x=1) v dim=1, potom point(x=2) v dim=2(parent=1)
  - Dim1: obs[1] = 2, pro[1] = 2/2 = 1.0 (marginálna P)
  - Dim2: obs[2|1] = 1, condPro = 1/1 = 1.0
           → pro[1→2] = 1.0 * 1.0 = 1.0 (spoločná P reťazca [1,2])
           → bit[1→2] = 0
  - actVals = [1, 2]

observe(1):
  - Okno: [2, 1]
  - Aktivuje: point(x=2) v dim=1, potom point(x=1) v dim=2(parent=2)
  - Dim1: obs[2] = 1, pro[2] = 1/3 ≈ 0.33
           → bit[2] = -0.33 * log2(0.33) ≈ 0.52
  - Dim2: obs[1|2] = 1, condPro = 1/1 = 1.0
           → pro[2→1] = 0.33 * 1.0 = 0.33 (spoločná P reťazca [2,1])
           → bit[2→1] = 0.52
  - actVals = [2, 1]

observe(2):
  - Okno: [1, 2]
  - Dim1: obs[1] = 3, pro[1] = 3/4 = 0.75
           → oldBit[1] = 1.0 → newBit[1] ≈ 0.31 → zmena ≈ -0.69
  - Dim2: obs[2|1] = 2, condPro = 2/3 ≈ 0.67
           → pro[1→2] = 0.75 * 0.67 ≈ 0.5
           → zmena bits[dim=2] ≈ 1.0
  - actVals = [1, 2]

observe(1):
  - Okno: [2, 1]
  - Dim1: obs[2] = 2, pro[2] = 2/5 = 0.4
  - Dim2: obs[1|2] = 2, condPro = 2/2 = 1.0
           → pro[2→1] = 0.4 * 1.0 = 0.4
  - actVals = [2, 1]
```

**Finálny výsledok**:
- Hodnota `1`: 3 pozorovania, pro = 0.6
- Hodnota `2`: 2 pozorovania, pro = 0.4
- Po hodnote `1` nasleduje `2`: 2-krát (pro[1→2] ≈ 0.67)
- Po hodnote `2` nasleduje `1`: 2-krát (pro[2→1] = 1.0)

## Metrika: Shannon Entropy (self.bits)

**Poznámka**: Mená `pro`, `bit` a `bits` sú historicky orientované a nie sú ideálne, ale zmenili by sa všetky referencie v kóde.

### Spoločná pravdepodobnosť (`point._vals['pro']`)

Každý bod v hierarchii drží **spoločnú pravdepodobnosť reťazca** od dimenzie 1 až po jeho dimenziu:

$$pro[X_1, X_2, ..., X_i] = P(X_1) \times P(X_2|X_1) \times ... \times P(X_i|...)$$

Príklad s dim=2:
- Dim 1: `pro[1] = P(X₁=1)` = 0.6
- Dim 2: `pro[1→2] = P(X₁=1) × P(X₂=2|X₁=1)` = 0.6 × 0.67 = 0.4

### Self-Information bodu (`point._vals['bit']`)

Počet bitov potrebných na kódovanie daného bodu:

$$bit = -pro \times \log_2(pro)$$

- **Fyzikálny zmysel**: Informačný obsah daného reťazca
- Minimum: 0 (pravdepodobnosť = 1.0, istota)
- Maximum: v oblasti 0.5 (maximálna neistota)

### Shannon Entropy objektu (`self.bits`)

**Suma self-information všetkých bodov v objektu**:

$$H = \sum_{\text{všetky body}} bit_i = \sum_{\text{všetky body}} -pro_i \times \log_2(pro_i)$$

**Aktualizácia**: Aby sa vyhnulo zotrvačnému prepočítavaniu všetkých bodov, `self.bits` sa aktualizuje **inkrementálne** počas `observe()`:

```python
oldBit = -oldPro * log2(oldPro)
newBit = -newPro * log2(newPro)
self.bits += (newBit - oldBit)
```

- Zložitosť: O(dim) namiesto O(dim × počet_bodov)
- Výsledok je presne ten istý

**Fyzikálny zmysel**: Entropia distribúcie všetkých pozorovaných reťazcov v danom Markovom objektu

## Dôležité Pravidlá

1. ✅ `self.points` = **slovník možných hodnôt**, nie história
2. ✅ `_getPoint(val, create=True)` = vytvorí bod len prvýkrát
3. ✅ `observe()` = zvýši `_vals['obs']` existujúceho bodu
4. ✅ Vnorené Markovove objekty = umožňujú analýzu závislostí
5. ✅ `actVals` = aktuálne okno posledných `dim` hodnôt
6. ✅ `pro` = **spoločná pravdepodobnosť reťazca**, nie marginálna
   - Dim 1: `pro = P(X₁)`
   - Dim 2: `pro = P(X₁) × P(X₂|X₁)`
   - atď.
7. ✅ `self.bits` = **inkrementálne aktualizovaná entropia**
   - Iba zmeny sa pripočítavajú, nie prepočet
   - O(dim) operácií namiesto O(dim × bodov)

## Časti Kódu

- `__init__()`: Inicializácia s dimenziou
- `observe(val)`: Hlavná operácia - analýza pozorovania
  - Inkrementálna aktualizácia `bits` a `pro`
  - Bezpečnosť pred `log(0)`
- `moveFwd(val)`: Posun okna a aktivovanie bodov
- `_activate(actVals)`: Rekurzívne aktivovanie cez dimenzie
- `_getPoint(val, create)`: Nájdenie/vytvorenie bodu
- `generate()`: Generovanie nasledujúcej hodnoty (stub)
