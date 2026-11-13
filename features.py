def calculate_orderbook_metrics(bids:dict[float,float],asks:dict[float,float])-> tuple[float,float,float,float]:
    best_bid = 0
    best_ask = float('inf')
    mid_price = 0
    spread = 0
    for i in bids:
        best_bid = max(i,best_bid)
    
    for j in asks:
        best_ask = min(j, best_ask)
    
    mid_price = (best_ask + best_bid) / 2
    spread = best_ask - best_bid
    
    return best_bid, best_ask, mid_price, spread

def calculate_liquidity_features(bids: dict[float, float], asks: dict[float, float]) -> tuple[float, float]:
    best_bid, best_ask, mid_price, spread = calculate_orderbook_metrics(bids, asks)
    best_bid_quantity = bids[best_bid]
    best_ask_quantity = asks[best_ask]
    if best_bid_quantity + best_ask_quantity == 0:
        raise ValueError("Total quantity cannot be zero")
    microprice = (best_bid*best_ask_quantity+ best_ask*best_bid_quantity)/(best_ask_quantity+best_bid_quantity)
    imbalance = (best_bid_quantity-best_ask_quantity)/(best_bid_quantity+best_ask_quantity)
    return microprice, imbalance

def calculate_depth(bids, asks, n=10):
    top_bids = sorted(bids, reverse=True)[:n]
    top_asks = sorted(asks)[:n]

    bid_depth = sum(bids[p] for p in top_bids)
    ask_depth = sum(asks[p] for p in top_asks)

    return bid_depth, ask_depth
