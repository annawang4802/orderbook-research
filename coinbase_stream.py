import asyncio
import websockets
import json

URL = "wss://ws-feed.exchange.coinbase.com"

async def main():
    async with websockets.connect(URL) as websocket:
        print("Connected to Coinbase!")

        subscription = {
            "type": "subscribe",
            "product_ids": ["BTC-USD"],
            "channels": ["level2"]
        }

        await websocket.send(json.dumps(subscription))

        message = await websocket.recv()
        data = json.loads(message)
        print(data)
if __name__ == "__main__":
    asyncio.run(main())