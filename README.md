# Karolínin certifikát k maturitě

Statická HTML stránka pro NFC tag na zlaté krabičce s 9 mincemi Český lev (1/25 oz, 2022-2023).

**Předáno:** 19.05.2026
**Live URL:** https://ouzo83.github.io/karolina-mince/

## Struktura

- `index.html` - jediná stránka, self-contained (HTML + CSS + JS, žádné dependencies)
- `scripts/update_fallback.py` - Python script, updatuje FALLBACK hodnoty (cena zlata, kurz USD/CZK)
- `.github/workflows/update-fallback.yml` - běží 1× měsíčně, spustí Python script a commitne změny

## Jak to funguje

Stránka při načtení v prohlížeči:
1. Pokusí se stáhnout živý kurz USD/CZK z ČNB API (https://api.cnb.cz)
2. Pokusí se stáhnout živou spot cenu zlata (gold-api.com / goldprice.org)
3. Pokud cokoliv selže (CORS, offline, výpadek API), použije FALLBACK hodnoty hardcoded v JS

FALLBACK hodnoty se aktualizují automaticky 1× měsíčně přes GitHub Action.

## Klíčové konstanty (kdyby bylo třeba upravit ručně)

V `index.html` hledej:
- `const FALLBACK` - hodnoty pro offline fallback
- `const NUM_COINS = 9` - počet mincí
- `const INVESTED = 25889` - celková investovaná částka
- `<div class="hero-date">` - datum maturity
- `<div class="letter">` - text dopisu

## Manuální spuštění aktualizace

```
pip install yfinance requests
python scripts/update_fallback.py
git add index.html
git commit -m "manual update"
git push
```

Nebo přes GitHub UI: Actions → "Update fallback values" → Run workflow

## OPSEC

Repo je veřejné kvůli GitHub Pages free tier. Neobsahuje žádné osobní informace
mimo křestní jméno a obecné finanční částky. Žádné údaje o uložení mincí,
adresy ani bankovní informace.
