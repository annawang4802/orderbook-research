class OrderBookNormalizer:
    def normalize_binance(self, bids, asks):
        normalized_bids = {}
        normalized_asks = {}
        for data in bids:
            normalized_bids[float(data[0])] = float(data[1])
        for data in asks:
            normalized_asks[float(data[0])] = float(data[1])

        return normalized_bids, normalized_asks

    def normalize_kraken(self, bids, asks):
        normalized_bids = {}
        normalized_asks = {}
        for data in bids:
            normalized_bids[float(data["price"])] = float(data["qty"])
        for data in asks:
            normalized_asks[float(data["price"])] = float(data["qty"])
        return normalized_bids, normalized_asks
    
    def normalize_record(self, exchange, symbol, timestamp, features):
        return {
            "exchange": exchange,
            "symbol": symbol,
            "timestamp": timestamp,
            **features
        }