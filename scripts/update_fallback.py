"""
Updatuje FALLBACK hodnoty v index.html aktualni cenou zlata a kurzem USD/CZK.
Spousti se automaticky 1x mesicne pres GitHub Actions.
"""
import re
import sys
from datetime import datetime
from pathlib import Path

import requests
import yfinance as yf


def get_gold_usd_per_oz() -> float:
    """Spot cena zlata v USD za trojskou unci (Gold Futures GC=F)."""
    ticker = yf.Ticker("GC=F")
    hist = ticker.history(period="5d")
    if hist.empty:
        raise RuntimeError("yfinance returned no data for GC=F")
    return float(hist["Close"].iloc[-1])


def get_usd_czk() -> float:
    """Kurz USD/CZK z CNB API."""
    url = "https://api.cnb.cz/cnbapi/exrates/daily?lang=EN"
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    data = r.json()
    for rate in data["rates"]:
        if rate["currencyCode"] == "USD":
            amount = rate.get("amount", 1)
            return float(rate["rate"]) / amount
    raise RuntimeError("USD rate not found in CNB response")


def update_html(html_path: Path, gold_usd: int, usd_czk: float, coin_price: int) -> bool:
    """Najde FALLBACK objekt v index.html a nahradi hodnoty. Vraci True pokud byla zmena."""
    content = html_path.read_text(encoding="utf-8")

    today = datetime.now().strftime("%Y-%m-%d")
    new_fallback = (
        "const FALLBACK = {\n"
        f"    goldUsd: {gold_usd},      // USD za trojskou unci (auto-updated {today})\n"
        f"    usdCzk: {usd_czk:.2f},       // kurz USD/CZK\n"
        f"    coinPriceCzk: {coin_price}  // odhad ceny 1/25 oz Cesky lev (spot + 30% premium)\n"
        "  };"
    )

    pattern = r"const FALLBACK = \{[^}]+\};"
    new_content, n = re.subn(pattern, new_fallback, content, count=1)
    if n == 0:
        raise RuntimeError("FALLBACK object not found in index.html")

    if new_content == content:
        return False

    html_path.write_text(new_content, encoding="utf-8")
    return True


def main():
    print("Fetching gold spot price (GC=F)...")
    gold_usd = round(get_gold_usd_per_oz())
    print(f"  Gold: {gold_usd} USD/oz")

    print("Fetching USD/CZK rate from CNB...")
    usd_czk = round(get_usd_czk(), 2)
    print(f"  USD/CZK: {usd_czk}")

    # Cena mince = spot * (1/25 oz) * kurz * 1.30 premium (CM marze na frakcnich mincich)
    coin_price = round(gold_usd * (1 / 25) * usd_czk * 1.30)
    print(f"  Coin price (estimate): {coin_price} CZK")

    html_path = Path(__file__).parent.parent / "index.html"
    changed = update_html(html_path, gold_usd, usd_czk, coin_price)

    if changed:
        print("OK - index.html updated")
        sys.exit(0)
    else:
        print("No changes (values identical)")
        sys.exit(0)


if __name__ == "__main__":
    main()
