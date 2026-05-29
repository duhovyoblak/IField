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
│   │   ├── ipoint.py                         # InfoPoint - základný bod v poli
│   │   ├── imatrix.py                        # InfoMatrix - matica bodov
│   │   ├── ipoint_gui.py                     # GUI pre body
│   │   ├── imatrix_gui.py                    # GUI pre matice
│   │   ├── imatrix_data_gui.py               # GUI pre dáta matíc
│   │   ├── imatrix_display_gui.py            # GUI pre zobrazenie matíc
│   │   └── imatrix_method_gui.py             # GUI pre metódy matíc
│   ├── ifield/                               # IField balíček (aplikačná logika)
│   │   ├── __init__.py
│   │   ├── imatrix.py                        # InfoFieldMatrix - IField-špecifická matica
│   │   ├── imatrix_gui.py                    # GUI pre IField matice
│   │   ├── imodel.py                         # Informačný model
│   │   └── imodel_gui.py                     # GUI pre model
├── test/                                     # Testovací kód
├── Old/                                      # Staré verzie a deprecated kód
└── README.md                                 # Tento súbor
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

## 🔧 Kľúčové komponenty

### Architektúra

Projekt je organizovaný do dvoch Python balíčkov:

#### `idata` balíček - Dátové štruktúry
Základné triedy bez špecifickej aplikačnej logiky:
- **InfoPoint** (`ipoint.py`) - Jednotlivý bod v informačnom poli s hodnotami a polohou
- **InfoMatrix** (`imatrix.py`) - Matica InfoPoint objektov s osami a podmaticami
- **GUI komponenty** - Grafické rozhrania pre zobrazenie a editáciu dát

#### `ifield` balíček - Aplikačná logika
IField-špecifické implementácie:
- **InfoFieldMatrix** (`imatrix.py`) - Rozšírenie InfoMatrix s komplexnými hodnotami a dynamikou polí
- **IFieldMatrixGui** (`imatrix_gui.py`) - Špecializované GUI pre IField matice
- **InfoModel** (`imodel.py`) - Informačný model pre úlohy
- **InfoModelGui** (`imodel_gui.py`) - GUI pre prácu s modelom

### main.py
Hlavný vstupný bod aplikácie. Inicializuje:
- Tkinter okno
- SiqoLogger pre loggovanie (úroveň: INFO)
- InfoFieldMatrix dátovú štruktúru
- IFieldMatrixGui grafické rozhranie

### Importy
- Z balíčka `idata`: `from idata.imatrix import InfoMatrix`
- Z balíčka `ifield`: `from ifield.imatrix import InfoFieldMatrix`
- Relatívne importy v balíčkoch: `from .imatrix import InfoFieldMatrix`

## 📝 Vývojové poznámky

- **Architektúra**: 2-balíčková štruktúra (`idata` + `ifield`) s entry pointom `main.py`
- **Logger**: Nastavený na úroveň `INFO`, frameDepth = 2
- **Minimálna veľkosť okna**: 600x300 pixelov
- **Balkóny**: Projekt používa `siqolib` knižnicu - pozri `d:\GitHub\siqolib`
- **Importy**: Všetky importy sú typu `from idata.xxx import YYY` alebo `from .imatrix import InfoFieldMatrix` (relatívne v balíčkoch)
- **Staré súbory**: Pôvodné súbory `siqo_*.py` a `ifield_*.py` boli migrované do balíčkov. Staré verzie sú v adresári `Old/`

## 👤 Vlastník

P. Horanský

## 📄 Licencia

Bude doplnené podľa potreby.
