# IField - Information Field Matrix GUI

Projekt `IField` je Python aplikácia so grafickým používateľským rozhraním (GUI) pre prácu s informačnými poľami a maticami. Používa Tkinter na tvorbu rozhrania a siqolib knižnicu pre logiku a nástroje.

## 📋 Popis

IField poskytuje nástroje na:
- Vytváranie a správu informačných matíc (InfoFieldMatrix)
- Grafické zobrazenie a manipuláciu s datami
- Prácu s bodmi v poli (ipoint) a maticami polí (imatrix)
- Logovanie a monitorovanie operácií

## 📁 Štruktúra projektu

```
IField/
├── src/                                      # Zdrojový kód
│   ├── main.py                               # Hlavný vstupný bod aplikácie
│   ├── idata/                                # Dátový balíček (Info bázové triedy)
│   │   ├── __init__.py
│   │   ├── idata.py                          # InfoData - matica bodov (základná trieda)
│   │   ├── ipoint.py                         # InfoPoint - jednotlivý bod v poli
│   │   ├── imarkov.py                        # IMarkov - n-rozmerný Markovov analyzátor
│   │   ├── iseries.py                        # ISeries - časový rad
│   │   ├── icurve.py                         # ICurve - krivka
│   │   ├── iftion.py                         # IFtion - funkcia
│   │   ├── ivector.py                        # IVector - vektor
│   │   ├── ipoint_gui.py                     # GUI pre body
│   │   ├── idata_gui.py                      # GUI pre matice
│   │   ├── idata_data_gui.py                 # GUI pre dáta matíc
│   │   ├── idata_display_gui.py              # GUI pre zobrazovanie matíc
│   │   └── idata_method_gui.py               # GUI pre metódy matíc
│   └── ifield/                               # IField balíček (aplikačná logika)
│       ├── __init__.py
│       ├── model.py                          # Informačný model
│       ├── ifield_matrix.py                  # InfoFieldMatrix
│       ├── ifield_line.py                    # InfoFieldLine
│       ├── model_gui.py                      # GUI pre model
│       ├── ifield_matrix_gui.py              # GUI pre IField matice
│       └── ifield_line_gui.py                # GUI pre IField čiary
├── test/                                     # Testovací kód (pytest)
│   ├── conftest.py                           # Pytest konfigurácia a fixtures
│   ├── README.md                             # Dokumentácia testov
│   ├── idata/                                # Testy pre idata balíček
│   │   ├── test_idata.py                     # Testy InfoData (13 testov)
│   │   ├── test_imarkov.py                   # Testy IMarkov (20 testov) ✅
│   │   ├── test_ipoint.py                    # Testy InfoPoint (11 testov) ✅
│   │   └── test_iseries.py                   # Testy ISeries (8 testov)
│   └── ifield/                               # Testy pre ifield balíček (budúcnosť)
├── Old/                                      # Staré verzie a deprecated kód
├── pytest.ini                                # Pytest konfigurácia
├── README.md                                 # Tento súbor
└── install-cheat.md                          # Návod na inštaláciu
```

## 🚀 Spustenie

### Požiadavky
- Python 3.x
- tkinter (zvyčajne súčasť Pythonu)
- siqolib knižnica

### Spuštenie aplikácie

```bash
cd src
python main.py
```

Aplikácia spustí GUI okno s testom triedy `IFieldMatrixGui`.

## 🧪 Testovanie

Projekt používa **pytest** na spúšťanie jednotkových testov.

### Test štatistika
- **Celkem testov**: 52
- **Passar**: 49 (94%)
- **Chybujúcich**: 3 (ISeries API mismatch)
- **Pokryté moduly**: idata, imarkov, ipoint, iseries

### Spustenie testov

```bash
# Všetky testy
pytest

# Testy len pre idata balíček
pytest test/idata/ -v

# Konkrétny modul
pytest test/idata/test_imarkov.py -v

# S coverage reportom
pytest test/idata/ --cov=src/idata --cov-report=html

# V VS Code
# - Otvoriť Testing panel (ľavá bočná lišta)
# - Alebo: Ctrl+Shift+P -> "Test: Run Tests"
```

### Kľúčové testy

#### IMarkov (20/20 passar ✅)
- Inicializácia a konfigurácia n-rozmerného Markovovho analyzátora
- Výpočet podmienených pravdepodobností
- Inkrementálna aktualizácia Shannon entropie
- Spracovanie pozorovania pre jednotlivé a množné dimenzie
- Hraničné prípady (nulové pravdepodobnosti, veľké dimenzie)

#### IPoint (11/11 passar ✅)
- Vytváranie bodov s typom `ipType`
- Správa pozícií a hodnôt
- Porovnávanie bodov
- Hraničné prípady (negatívne pozície, float hodnoty)

#### IData (13/13 passar ✅)
- Inicializácia dátovej štruktúry
- Správa bodov a schém
- Informačné metódy
- Reset a zmena dimenzie

#### ISeries (5/8 passar)
- Časový rad - API differences medzi testami a implementáciou

### Konfigurácia

- **pytest.ini** - Nastavenia pytest (test discovery, markery, atď.)
- **.vscode/settings.json** - VS Code integrácia (test discovery, verbose output)
- **.vscode/launch.json** - Debug konfigurácie pre testy

Podrobnosti: Pozri [test/README.md](test/README.md)

## 🔧 Kľúčové komponenty

### Architektúra

Projekt je organizovaný do dvoch Python balíčkov:

#### `idata` balíček - Dátové štruktúry
Základné triedy bez špecifickej aplikačnej logiky:
- **InfoPoint** (`ipoint.py`) - Jednotlivý bod v informačnom poli s hodnotami a polohou
  - Dynamická schéma pre rôzne typy bodov (`ipReal`, `ipComplex`, atď.)
  - Statické metódy na správu schémy

- **InfoData** (`idata.py`) - Matica InfoPoint objektov s osami a podmaticami
  - Základná trieda pre všetky dátové štruktúry
  - Hierarchická štruktúra s podmaticami
  - Schéma-driven prístup

- **IMarkov** (`imarkov.py`) - N-rozmerný Markovov analyzátor
  - Analýza sekvenčných dát s pravdepodobnostným modelom
  - Výpočet podmienených a joint pravdepodobností
  - Inkrementálna Shannon entropie (O(dim) miesto O(dim × points))
  - Vyhrnutá historická pamäť posledných `dim` pozorovaní

- **ISeries** (`iseries.py`) - Časový rad
  - Sekvencia dát s časovým rozmerom
  - Agregácia a analýza časových údajov

- **Ďalšie triedy**: ICurve, IVector, IFtion - špecializované dátové štruktúry
- **GUI komponenty** - Grafické rozhrania pre zobrazenie a editáciu dát

#### `ifield` balíček - Aplikačná logika
IField-špecifické implementácie:
- **InfoFieldMatrix** (`ifield_matrix.py`) - Rozšírenie InfoData s komplexnými hodnotami a dynamikou polí
- **InfoFieldLine** (`ifield_line.py`) - 1D informačné pole (čiara)
- **InfoModel** (`model.py`) - Informačný model pre úlohy
- **GUI komponenty** - Špecializované GUI pre IField matice a čiary

### main.py
Hlavný vstupný bod aplikácie. Inicializuje:
- Tkinter okno
- SiqoLogger pre loggovanie (úroveň: INFO)
- InfoFieldMatrix dátovú štruktúru
- IFieldMatrixGui grafické rozhranie

### Importy
- Z balíčka `idata`: `from idata.idata import InfoData`
- Z balíčka `ifield`: `from ifield.imatrix import InfoFieldMatrix`
- Relatívne importy v balíčkoch: `from .imatrix import InfoFieldMatrix`

## 📝 Vývojové poznámky

- **Architektúra**: 2-balíčková štruktúra (`idata` + `ifield`) s entry pointom `main.py`
- **Testovanie**: pytest s 52 testami, 49 passar (94%)
  - IMarkov: 100% passar (20/20) - Markovov analyzátor s incremental entropy
  - IPoint: 100% passar (11/11) - Body s typom a schémou
  - IData: 100% passar (13/13) - Základná dátová štruktúra
  - ISeries: 62.5% passar (5/8) - Časový rad (API issues)
- **Logger**: Nastavený na úroveň `INFO`, frameDepth = 2
- **Minimálna veľkosť okna**: 600x300 pixelov
- **Balkóny**: Projekt používa `siqolib` knižnicu - pozri `d:\GitHub\siqolib`
- **Importy**: Všetky importy sú typu `from idata.xxx import YYY` alebo `from .yyy import ZZZ` (relatívne v balíčkoch)
- **Staré súbory**: Pôvodné súbory boli migrované do balíčkov. Staré verzie sú v adresári `Old/`
- **Kľúčové opravy**:
  - IMarkov sliding window bug (dim=1 support)
  - IMarkov all-points probability update pre správnu entropiu
  - InfoPoint fixture s povinným `ipType` parametrom
- **VS Code integrácia**: Testing panel, debug konfigurácie, formátor Black, linter flake8

## 👤 Vlastník

P. Horanský

## 📄 Licencia

Bude doplnené podľa potreby.
