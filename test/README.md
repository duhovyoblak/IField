# IField Unit Tests

Jednotkové testy pre Python package `idata` a ostatné moduly projektu IField.

## Štruktúra

```
test/
├── conftest.py              # Pytest konfigurácia a fixtures
├── README.md                # Táto dokumentácia
├── idata/                   # Testy pre idata package
│   ├── __init__.py
│   ├── test_idata.py        # Testy pre InfoData modul
│   ├── test_imarkov.py      # Testy pre IMarkov modul
│   ├── test_ipoint.py       # Testy pre InfoPoint modul
│   └── test_iseries.py      # Testy pre ISeries modul
└── ifield/                  # Testy pre ifield package (budúcnosť)

## Inštalácia závislostí

```bash
pip install pytest pytest-cov
```

## Spustenie testov

### V VS Code

- Otvoriť command palette: `Ctrl+Shift+P` (Windows/Linux) alebo `Cmd+Shift+P` (Mac)
- Nájsť: "Python: Discover Tests"
- Alebo kliknúť na ikonu testing v Activity Bar

### V terminále

```bash
# Všetky testy
pytest

# Testy iba pre idata package
pytest test/idata/

# Testy s verbóznym výstupom
pytest test/idata/ -v

# Konkrétny test súbor
pytest test/idata/test_imarkov.py

# Konkrétna test trieda
pytest test/idata/test_imarkov.py::TestIMarkovInit

# Konkrétny test
pytest test/idata/test_imarkov.py::TestIMarkovInit::test_imarkov_creation

# S coverage reportom
pytest test/idata/ --cov=src --cov-report=html
```

## Test Moduly

### `test/idata/test_imarkov.py`

Testy pre n-rozmerný Markovov analyzátor:

- **TestIMarkovInit**: Inicializácia a konfigurácia
- **TestIMarkovObserve**: Pozorovanie a aktualizácia dát
  - Jednotlivé a množné pozorovania
  - Výpočet pravdepodobností
  - Inkrementálna aktualizácia entropie
- **TestIMarkovReset**: Reset a zmena dimenzie
- **TestIMarkovInfo**: Informačné metódy
- **TestIMarkovEdgeCases**: Hraničné prípady a chyby

Najdôležitejšie testy:
- `test_probability_calculation_single_dim` - Správnosť výpočtu pravdepodobnosti
- `test_conditional_probability_dim2` - Podmienené pravdepodobnosti
- `test_entropy_update_incremental` - Inkrementálna aktualizácia entropie

### `test/idata/test_ipoint.py`

Testy pre InfoPoint (jednotlivý dátový bod):

- **TestIPointInit**: Vytvorenie a inicializácia
- **TestIPointValues**: Správa hodnôt
- **TestIPointComparison**: Porovnávanie bodov
- **TestIPointEdgeCases**: Hraničné prípady

### `test/idata/test_idata.py`

Testy pre InfoData (základnú triedu):

- **TestInfoDataInit**: Inicializácia
- **TestInfoDataPoints**: Správa bodov
- **TestInfoDataSchema**: Schéma a osi
- **TestInfoDataInfo**: Informačné metódy
- **TestInfoDataReset**: Reset
- **TestInfoDataIntegration**: Integračné testy
- **TestInfoDataEdgeCases**: Hraničné prípady

### `test/idata/test_iseries.py`

Testy pre ISeries (časový rad):

- **TestISeriesInit**: Inicializácia
- **TestISeriesDataManagement**: Správa dát
- **TestISeriesInfo**: Informačné metódy
- **TestISeriesEdgeCases**: Hraničné prípady

## Fixtures

V `conftest.py` sú dostupné nasledujúce fixtures:

```python
@pytest.fixture
def idata_instance():
    """Свежа InfoData inštancia."""

@pytest.fixture
def imarkov_instance():
    """Свежа IMarkov inštancia (dim=1)."""

@pytest.fixture
def ipoint_instance():
    """Свежа InfoPoint inštancia."""

@pytest.fixture
def iseries_instance():
    """Свежа ISeries inštancia."""
```

Použitie:
```python
def test_something(imarkov_instance):
    imarkov_instance.observe(1)
    assert imarkov_instance.totObs == 1
```

## Pravidlá pre testy

1. **Izolácia**: Každý test by mal byť nezávislý
2. **Názvy**: Test metódy majú začínať `test_`
3. **Skupiny**: Testy sú organizované v triedach `Test*`
4. **Fixtures**: Používať fixtures z `conftest.py`
5. **Assertions**: Jasné a špecifické assert príkazy
6. **Dokumentácia**: Docstring pre každý test

## Pokrytie kódu

```bash
# Generovanie HTML reportu
pytest --cov=src --cov-report=html

# Otvoriť report
open htmlcov/index.html  # Na Macu
start htmlcov/index.html  # Na Windowse
```

## CI/CD Integrácia

Testy možno integrovať s:
- **GitHub Actions**: `.github/workflows/tests.yml`
- **GitLab CI**: `.gitlab-ci.yml`
- **Jenkins**: `Jenkinsfile`

Príklad GitHub Actions:
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r requirements.txt pytest
      - run: pytest
```

## Troubleshooting

### Import Error: `No module named 'idata'`

Overovať, že `sys.path` v `conftest.py` obsahuje `src/` adresár.

### Tests niet discovered

V VS Code:
1. Command palette → "Python: Discover Tests"
2. Alebo skúsiť restart VS Code

### Testy zdania starého kódu

```bash
# Vymazať cache
rm -rf __pycache__ .pytest_cache

# Opätovne spustiť
pytest
```

## Ďalej

- Pridať testy pre `iftion.py` (funkčný modul)
- Pridať testy pre `icurve.py`
- Dodať integračné testy
- Nastaviť code coverage policy
