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
├── src/                              # Hlavný zdrojový kód
│   ├── main.py                       # Hlavný vstupný bod aplikácie
│   ├── imodel.py                     # Model informačných polí
│   ├── imodel_gui.py                 # GUI pre model
│   ├── ifield_imatrix.py             # Implementácia matíc IField
│   ├── ifield_imatrix_gui.py         # GUI pre IField matice
│   ├── siqo_imatrix.py               # SIQO maticové operácie
│   ├── siqo_imatrix_gui.py           # GUI pre SIQO matice
│   ├── siqo_imatrix_data_gui.py      # GUI pre dáta SIQO matíc
│   ├── siqo_imatrix_display_gui.py   # GUI pre zobrazenie SIQO matíc
│   ├── siqo_imatrix_method_gui.py    # GUI pre metódy SIQO matíc
│   ├── siqo_ipoint.py                # SIQO body v poli
│   ├── siqo_ipoint_gui.py            # GUI pre SIQO body
│   ├── idata/                        # Dáta a datové štruktúry
│   └── ifield/                       # Modul IField
├── test/                             # Testovací kód
├── Old/                              # Staré verzie a deprecated kód
└── README.md                         # Tento súbor
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

### main.py
Hlavný vstupný bod aplikácie. Inicializuje:
- Tkinter okno
- SiqoLogger pre loggovanie
- InfoFieldMatrix dátovú štruktúru
- IFieldMatrixGui grafické rozhranie

### IFieldMatrix
Trieda reprezentujúca maticu informačných polí.

### IFieldMatrixGui
GUI komponenta pre interakciu s InfoFieldMatrix v Tkinter aplikácii.

### SIQO komponenty
Sada SIQO-špecifických tried pre:
- Prácu s maticami (`siqo_imatrix*.py`)
- Prácu s bodmi (`siqo_ipoint*.py`)

## 📝 Vývojové poznámky

- Logger je nastavený na úroveň `INFO`
- Aplikácia má minimálnu veľkosť okna: 600x300 pixelov
- Projekt používa siqolib knižnicu - pozri `d:\GitHub\siqolib`

## 👤 Vlastník

P. Horanský

## 📄 Licencia

Bude doplnené podľa potreby.
