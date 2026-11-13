import asyncio

from asset_selector import (
    get_24h_performance,
    get_kraken_pairs,
    select_top_20,
)

from binance_stream import main as stream_binance
from kraken_stream import main as stream_kraken


async def main():
    while True:
        # 1. Select top 20 assets
        tickers = await asyncio.to_thread(get_24h_performance)
        kraken_pairs = await asyncio.to_thread(get_kraken_pairs)

        top_20 = select_top_20(tickers, kraken_pairs)

        binance_symbols = [
            asset["binance_symbol"] for asset in top_20
        ]

        kraken_symbols = [
            asset["kraken_symbol"].replace("XBT/", "BTC/")
            for asset in top_20
        ]

        print("Binance:", binance_symbols)
        print("Kraken:", kraken_symbols)

        # 2. Start streaming
        tasks = [
            asyncio.create_task(stream_binance(symbol))
            for symbol in binance_symbols
        ] + [
            asyncio.create_task(stream_kraken(symbol))
            for symbol in kraken_symbols
        ]

        try:
            # 3. Stream for 24 hours
            await asyncio.sleep(24 * 60 * 60)

        finally:
            # 4. Stop existing streams
            for task in tasks:
                task.cancel()

            await asyncio.gather(*tasks, return_exceptions=True)

        # 5. Loop repeats → select new top 20

if __name__ == "__main__":
    asyncio.run(main())