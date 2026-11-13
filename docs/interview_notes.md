### 📊 Order Book Research — Interview Talking Points

🔹 **Why L2 data?**

L2 data shows **aggregated liquidity at different price levels**, helping us study spreads, liquidity imbalance and short-term price dynamics.

🔹 **Why microprice rather than mid-price?**

Mid-price weights bid and ask equally. Microprice adjusts for **bid/ask quantity imbalance**, potentially capturing short-term directional pressure. Predictive power needs empirical validation.

🔹 **Why WebSockets?**

Enable **continuous real-time data collection** without repeatedly polling an API.

🔹 **Why maintain a local order book?**

WebSocket messages contain **incremental updates**, not complete snapshots. A synchronised local book lets us reconstruct the current state and calculate reliable features.

💡 **Potential Research Question**

*Does order book imbalance predict future mid-price movements out of sample?*