### L2 Order Book — Data Infrastructure Implementation

**Data representation**

`bids` and `asks` are dictionaries mapping price → aggregated quantity.

**Data sources**
- REST (`/api/v3/depth`): initial snapshot, up to 1,000 price levels per side.
- WebSocket (`btcusdt@depth`): continuous incremental order book updates.

## Data collection

> **REST API:** fetch the initial snapshot (up to 1,000 levels per side)
> **WebSocket:** receive continuous incremental bid/ask updates
> **Relevant fields:** `b` (bids), `a` (asks), `U`/`u` (update IDs), `lastUpdateId` (REST snapshot version)
> Convert price/quantity strings to floats and store as `price → quantity`

**Synchronisation workflow**
1. Open WebSocket and start receiving messages into an `asyncio.Queue`.
2. Fetch REST snapshot concurrently and initialise `bids` / `asks`.
3. Discard WebSocket messages with `u <= lastUpdateId`.
4. Check that the first applicable message covers `lastUpdateId + 1`.
5. Apply bid/ask changes using `update_orderbook()`.
6. Track `previous_u` and detect gaps in subsequent messages.
7. On a gap, restart synchronisation using a fresh REST snapshot. (break inner loop => outer loop)

**Update rules**
- Positive quantity: replace existing quantity or insert a new price level.
- Zero quantity: remove the price level.
- Updates are applied in WebSocket message order.

**Features**

Best bid/ask, mid-price, spread, microprice, order book imbalance and bid/ask depth.

Microprice and imbalance use quantities at the best price levels only; depth sums all supplied levels.


**Remaining limitations**
- WebSocket receiver failure and reconnection handling.
- Robust validation of sequence continuity and recovery.
- Testing edge cases and sustained operation.
- Potential use of `Decimal` instead of floats for price precision.

**Feature engineering**

Calculate best bid/ask, mid-price, spread, microprice, order book imbalance and bid/ask depth from the synchronised L2 order book. Feature calculations are separated into `features.py` for modularity.

**Data recording**
- Each valid processed update generates a timestamped observation containing the update ID and calculated features.
- A `Recorder` class accumulates observations in memory.
- Previously collected observations are retained during resynchronisation; recording resumes after valid updates.

**Parquet storage**
- Convert observations into pandas DataFrames.
- Save every 1,000 observations as a separate Parquet file.
- Use incrementing batch numbers and check existing filenames to avoid overwriting.
- Clear records from memory only after successful saving.
- Save remaining observations during shutdown.

### Cross-Exchange Integration & Dynamic Asset Selection

**Data sources**
- Binance and Kraken L2 order book data collected through WebSockets.
- Exchange-specific messages converted into a common format using `normalizer.py`.
- Preserve `exchange`, `symbol` and `timestamp` to distinguish observations across markets.

**Dynamic asset selection**
- Retrieve Binance 24-hour price performance and select the top 20 performing assets available on both exchanges.
- Implement daily reselection (every 24 hours), cancelling existing streams and restarting with the updated asset list.

**Remaining limitations**
- Daily reshuffling implemented but not yet tested over a full cycle.
- Kraken data collection and persistence across selected assets require further verification.

### PCA Dimensionality Reduction

**Objective**

Reduce redundancy among correlated L2 features while retaining at least 95% of total variance.

**Implementation (`pca.py`)**
1. Load and concatenate recorded Parquet files using pandas.
2. Group observations by `(exchange, symbol)` to process each market independently.
3. Select 8 numerical order book features.
4. Standardise using `StandardScaler` (zero mean, unit variance for non-constant features).
5. Apply `PCA(n_components=0.95)` separately to each group.
6. Report the number of principal components and total explained variance.

**Results**
- Most groups reduced from 8 features to 2–4 principal components.
- Example: Binance INJUSDT reduced from 8 to 4 components, retaining 96.64% variance.

**Limitations**
- Small sample sizes; results are preliminary.
- PCA currently runs as a separate analysis script rather than automatically during recording.
- Future predictive modelling requires chronological train/test splitting

