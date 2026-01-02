from models.candle import Candle
from datetime import datetime

class MarketDataService:
    def __init__(self, broker):
        self.broker = broker

    def get_candles(self, params):
        raw = self.broker.get_candles(params)
        candles = []

        for row in raw["data"]:
            candle = Candle(
                time=datetime.fromisoformat(row[0]),
                open=float(row[1]),
                high=float(row[2]),
                low=float(row[3]),
                close=float(row[4]),
                volume=int(row[5])
            )
            candles.append(candle)

        return candles
