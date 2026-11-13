import requests

def get_snapshot(symbol="BTCUSDT"):
    url = "https://api.binance.com/api/v3/depth"

    response = requests.get(
        url,
        params={"symbol": symbol, "limit": 1000},
        timeout=10
    )
    response.raise_for_status()
    return response.json()


snapshot = get_snapshot()
print(snapshot["lastUpdateId"])
print(snapshot["bids"][:3])
print(snapshot["asks"][:3])

bids= {}
for price, quantity in snapshot["bids"]:
    bids[float(price)] = float(quantity)

asks= {}
for price, quantity in snapshot["asks"]:
    asks[float(price)] = float(quantity)
print(len(asks))


