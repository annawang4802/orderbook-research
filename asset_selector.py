
import requests


def get_24h_performance():
    url = "https://api.binance.com/api/v3/ticker/24hr"
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    return response.json()


def get_kraken_pairs():
    url = "https://api.kraken.com/0/public/AssetPairs"
    response = requests.get(url, timeout=15)
    response.raise_for_status()

    data = response.json()

    if data["error"]:
        raise RuntimeError(data["error"])

    return data["result"]


def select_top_20(tickers, kraken_pairs):
    kraken_symbols = {}

    for pair in kraken_pairs.values():
        wsname = pair.get("wsname", "")

        if not wsname.endswith("/USD"):
            continue

        base = wsname.split("/")[0]

        if base == "XBT":
            base = "BTC"

        kraken_symbols[base] = wsname

    eligible = []

    for ticker in tickers:
        symbol = ticker["symbol"]

        if not symbol.endswith("USDT"):
            continue

        base = symbol[:-4]

        if base not in kraken_symbols:
            continue

        eligible.append(ticker)

    ranked = sorted(
        eligible,
        key=lambda x: float(x["priceChangePercent"]),
        reverse=True
    )

    return [
        {
            "asset": ticker["symbol"][:-4],
            "binance_symbol": ticker["symbol"],
            "kraken_symbol": kraken_symbols[ticker["symbol"][:-4]],
            "return_24h": float(ticker["priceChangePercent"])
        }
        for ticker in ranked[:20]
    ]


if __name__ == "__main__":
    tickers = get_24h_performance()
    kraken_pairs = get_kraken_pairs()

    top_20 = select_top_20(tickers, kraken_pairs)

    for i, asset in enumerate(top_20, start=1):
        print(
            f"{i}. {asset['asset']} | "
            f"Binance: {asset['binance_symbol']} | "
            f"Kraken: {asset['kraken_symbol']} | "
            f"24h return: {asset['return_24h']:.2f}%"
        )
