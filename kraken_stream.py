import asyncio
import websockets
import json
from orderbook import OrderBook
from features import (
    calculate_orderbook_metrics,
    calculate_liquidity_features,
    calculate_depth
)
from recorder import Recorder
from datetime import datetime, timezone
from decimal import Decimal 
from kraken_checksum import calculate_checksum
from normalizer import OrderBookNormalizer

URL = "wss://ws.kraken.com/v2"

async def main(symbol):
    async with websockets.connect(URL) as websocket:
        print("Connected to Kraken!")

        subscription = {
            "method": "subscribe",
            "params": {
                "channel": "book",
                "symbol": [symbol],
                "depth": 10,
                "snapshot": True
            }
        }

        await websocket.send(json.dumps(subscription))
        book = OrderBook()
        recorder = Recorder(symbol, "kraken")
        normalizer = OrderBookNormalizer()

        try:
            while True:
                message = await websocket.recv()
                data = json.loads(message,parse_float=Decimal)

                if data.get("channel") != "book":
                    continue

                if data["type"] == "snapshot":
                    snapshot = data["data"][0]

                    book.bids = {
                        level["price"]: level["qty"]
                        for level in snapshot["bids"]
                    }

                    book.asks = {
                        level["price"]: level["qty"]
                        for level in snapshot["asks"]
                    }
                elif data["type"] == "update":
                    for level in data["data"][0]["bids"]:
                        book.update_bid(level["price"],level["qty"])
                    for level in data["data"][0]["asks"]:
                        book.update_ask(level["price"],level["qty"])
                
                # Keep only the 10 highest bid prices
                while len(book.bids) > 10:
                    del book.bids[min(book.bids)]

                # Keep only the 10 lowest ask prices
                while len(book.asks) > 10:
                    del book.asks[max(book.asks)]
                
                top_bids = sorted(book.bids, reverse=True)
                top_asks = sorted(book.asks)

                # Validate checksum
                expected_checksum = data["data"][0]["checksum"]
                actual_checksum = calculate_checksum(book.bids, book.asks)

                if actual_checksum != expected_checksum:
                    print("Checksum mismatch!")
                    break
                print("Checksum OK!")

                # Convert Decimal values to floats for feature calculations
                bids = {float(p): float(q) for p, q in book.bids.items()}
                asks = {float(p): float(q) for p, q in book.asks.items()}

                
                # Calculate features
                best_bid, best_ask, mid_price, spread = calculate_orderbook_metrics(bids, asks)

                microprice, imbalance = calculate_liquidity_features(bids, asks)

                bid_depth, ask_depth = calculate_depth(bids, asks)

                # Create record
                features = {
                    "best_bid": best_bid,
                    "best_ask": best_ask,
                    "mid_price": mid_price,
                    "spread": spread,
                    "microprice": microprice,
                    "imbalance": imbalance,
                    "bid_depth": bid_depth,
                    "ask_depth": ask_depth
                }

                record = normalizer.normalize_record(
                    exchange="kraken",
                    symbol=symbol,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    features=features
                )
                recorder.records.append(record)

                print("\n--- Kraken Order Book Features ---")
                for key, value in record.items():
                    print(f"{key}: {value}")

                if len(recorder.records) >= 1000:
                    recorder.save()

                
        finally:
            if recorder.records:
                recorder.save()
        
            

if __name__ == "__main__":
    asyncio.run(main("BTC/USD"))