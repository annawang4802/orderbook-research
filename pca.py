import pandas as pd
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

files = [
    path for path in Path(".").rglob("*.parquet")
    if path.name.startswith(("binance_", "kraken_"))
]

# Read each Parquet file into a DataFrame
dfs = [pd.read_parquet(path) for path in files]

# Combine all DataFrames vertically
df = pd.concat(dfs, ignore_index=True)

features = [
    "best_bid", "best_ask", "mid_price", "spread",
    "microprice", "imbalance", "bid_depth", "ask_depth"
]
for (exchange, symbol), group in df.groupby(["exchange", "symbol"]):
    X = group[features]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    pca = PCA(n_components=0.95)
    X_pca = pca.fit_transform(X_scaled)

    print(
        exchange, symbol,
        "Components:", X_pca.shape[1],
        "Variance:", pca.explained_variance_ratio_.sum()
    )


