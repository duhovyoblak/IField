---
owner: P. Horanský
language: sk
scope: global
---

# Copilot Inštrukcie - Editovanie zdrojového kódu

## Po vykonaní zmien v kóde:
- Skontroluj za sebou vykonané zmeny
- Aktualizuj docstringy a komentáre
- Použi statickú analýzu kódu na zmenený kód
- Skotroluj, či nevznikol mŕtvy kód a ak áno, odstráň ho
- Pri menších ucelených zmenách zvýš patch hodnotu verzie v premennej modulu _VER, npr. '3.3.0' -> '3.3.1'
- Pri väčších zmenách mi navrhni zvýšenie minor verzie a aktualizuj README.md

## Premenovanie triedy
- Kontroluj potenciálny konflikt s existujúcimi triedami ak bude trieda premenovaná
- Premenuj aj odkazy na triedu v komentároch
- Navrhni premenovanie *.py suboru
- Uprav vsetky importy vo vsetkych suboroch projektu

## Premenovanie metódy
- Kontroluj potenciálny konflikt s existujúcimi metódami ak bude metóda premenovaná
- Premenuj aj odkazy na metódu v pouzití loggera, napr. logger.info(f'{who}.<názov_metódy>: ...
- Premenuj aj odkazy na metódu v komentároch
