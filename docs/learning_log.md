10 Nov — L2 Order Book & WebSocket

Implemented mid-price, spread, microprice, imbalance and depth.

Implemented order book updates: replace quantity or remove level if quantity = 0.

Connected successfully to Binance WebSocket.

Learned sum(), min(), max(), dictionary methods, JSON parsing and basic async/await.

12 Nov
**Key Python concepts**
- `async` / `await`: allow asynchronous tasks to run without blocking one another.
- `asyncio.create_task()`: runs the WebSocket receiver concurrently with the main function.
- `asyncio.Queue`: FIFO structure for passing messages between asynchronous tasks; `await queue.get()` waits for new messages.
- `try/finally`: guarantees cleanup when leaving the block, including cancellation of the receiver.
- `break` / `continue`: `break` exits the innermost loop; `continue` skips to its next iteration.
- Nested `while True` loops: inner loop processes live updates; a sequence gap breaks to the outer loop, which fetches a new snapshot.
- Dictionary comprehension: creates and populates a dictionary directly, without initialising `{}` first.

**Key lessons**
- A WebSocket message is a dictionary containing update IDs (`U`, `u`) and lists of bid/ask changes (`b`, `a`).
- Each message may update multiple price levels.
- REST provides the initial book; WebSocket supplies incremental changes.
- The latest WebSocket message does not contain the entire order book, so missing updates require resynchronisation.

**OOP & encapsulation**
- `class Recorder`: groups data (`self.records`) and methods (`add_record`, `save`) into one object.
- Encapsulation: manage data through object methods rather than modifying it directly.
- Modularisation: separate responsibilities across `orderbook.py`, `features.py` and `recorder.py`.

**Python concepts**
- `return` vs `break`: `return` exits a function; `break` exits a loop.
- `f"orderbook_{n}.parquet"`: f string. inserts a variable into a filename.
- `Path(filename).exists()`: checks whether a file already exists.
- `while`: repeatedly checks for an unused filename.

**Pandas & Parquet**
- `pd.DataFrame(self.records)`: converts a list of dictionaries into a table.
- `df.to_parquet(filename, index=False)`: saves a DataFrame to disk.
- `df.head()`: displays the first five rows.
- `df.shape`: returns (rows, columns).

**Memory & persistence**
- RAM is temporary; data disappears when the program stops.
- Batch saving reduces disk writes and prevents unlimited memory growth.
- `finally` saves remaining observations during normal or handled shutdown, but cannot guarantee recovery after a forced termination.