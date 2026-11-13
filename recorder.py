import pandas as pd
from pathlib import Path

class Recorder:
    def __init__(self, symbol, exchange):
        self.records = []
        self.batch_number = 0
        self.symbol = symbol
        self.exchange = exchange

    def add_record(self, record):
        self.records.append(record)
    
    def save(self):
        if not self.records:
            return 
        df = pd.DataFrame(self.records)
        while Path(f"orderbook_{self.batch_number}.parquet").exists():
            self.batch_number += 1
        df.to_parquet(f"{self.exchange}_{self.symbol}_{self.batch_number}.parquet", index=False)
        self.batch_number +=1
        self.records =[]
        
    