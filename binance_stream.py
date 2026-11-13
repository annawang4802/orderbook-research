import asyncio
import websockets
import json
from snapshot import get_snapshot
from orderbook import OrderBook
from features import (
    calculate_orderbook_metrics,
    calculate_liquidity_features,
    calculate_depth
)
from recorder import Recorder
from datetime import datetime, timezone
from normalizer import OrderBookNormalizer

async def receive_updates(websocket, queue):
    while True:
        message = await websocket.recv()
        data = json.loads(message)
        await queue.put(data)

async def main(symbol):
    URL = f"wss://stream.binance.com:443/ws/{symbol.lower()}@depth"

    async with websockets.connect(URL, open_timeout=10) as websocket:
        print(f"Connected to Binance: {symbol}", flush=True)

    
    async with websockets.connect(URL) as websocket:
        print("Connected to Binance!")

        queue = asyncio.Queue()

        # Start receiving WebSocket updates
        receiver = asyncio.create_task(
            receive_updates(websocket, queue)
        )

        recorder = Recorder(symbol, "binance")

        normalizer = OrderBookNormalizer()

        try:
            # Outer loop: Fetch a fresh REST snapshot whenever resynchronisation is needed
            while True:
                # Fetch REST snapshot while WebSocket keeps receiving
                snapshot = await asyncio.to_thread(get_snapshot,symbol)
                lastUpdateId = snapshot["lastUpdateId"]

                book = OrderBook()
                # Initialise local order book
                book.bids, book.asks = normalizer.normalize_binance(
                    snapshot["bids"],
                    snapshot["asks"]
                )
                previous_u = lastUpdateId
                synchronised = False

                # Inner loop: Continuously process live WebSocket updates
                # If a gap is detected, break exits this loop and returns to the outer loop
                while True:
                    message = await queue.get()

                    # 1. Skip updates already included in the REST snapshot/book
                    if message["u"] <= previous_u:
                        continue

                    # 2. Check for missing updates
                    if message["U"] > previous_u + 1:
                        print("Missing updates — need to resynchronise!")
                        break

                    # 3. Apply bid updates
                    for price, quantity in message["b"]:
                        book.update_bid(float(price), float(quantity))

                    # 4. Apply ask updates
                    for price, quantity in message["a"]:
                        book.update_ask(float(price), float(quantity))

                    # 5. Remember the latest processed update ID
                    previous_u = message["u"]

                    if book.bids and book.asks:
                        metrics = calculate_orderbook_metrics(book.bids, book.asks)
                        print("Metrics:", metrics)

                        microprice, imbalance = calculate_liquidity_features(book.bids, book.asks)
                        bid_depth, ask_depth = calculate_depth(book.bids, book.asks)

                        print("Microprice:", microprice)
                        print("Imbalance:", imbalance)
                        print("Bid depth:", bid_depth)
                        print("Ask depth:", ask_depth)
                        print("Symbol:", symbol)

                        best_bid, best_ask, mid_price, spread = metrics

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
                            exchange="binance",
                            symbol=symbol,
                            timestamp=datetime.now(timezone.utc).isoformat(),
                            features=features
                        )

                        print("Normalized record:", record)

                        
                        recorder.add_record(record)
                        if len(recorder.records) == 1000:
                            recorder.save()

                        print("Records collected:", len(recorder.records))

                    
                    if not synchronised:
                        synchronised = True
                        print("Initial synchronisation successful!")

                    print("Latest update ID:", previous_u)
                            

        finally:
            recorder.save()
            receiver.cancel()
            try:
                await receiver
            except asyncio.CancelledError:
                pass
        

async def run_all():
    await asyncio.gather(
        main("BTCUSDT"),
        main("ETHUSDT"),
        main("SOLUSDT")
    )


if __name__ == "__main__":
    asyncio.run(run_all())
