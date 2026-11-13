import pandas as pd

df = pd.read_parquet("orderbook_0.parquet")
print(df.head())
print(df.shape)

print("Shape:", df.shape)

# Check missing values
print("Missing values:")
print(df.isnull().sum())

# Check timestamps are chronological
print("Timestamps ordered:", df["timestamp"].is_monotonic_increasing)

# Check for invalid negative spreads
print("Negative spreads:", (df["spread"] < 0).sum())

# Check imbalance is between -1 and 1
print("Invalid imbalance:", (~df["imbalance"].between(-1, 1)).sum())

# Check duplicate update IDs
print("Duplicate update IDs:", df["update_id"].duplicated().sum())