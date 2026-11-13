class OrderBook:
    def __init__(self):
        self.bids = {}
        self.asks = {}
    
    def update_bid(self, price, quantity):
        if quantity == 0:
            self.bids.pop(price, None)
        else:
            self.bids[price] = quantity
    
    def update_ask(self, price, quantity):
        if quantity == 0:
            self.asks.pop(price, None)
        else:
            self.asks[price] = quantity




    









