# from core.analysis import TechnicalAnalysis


# class NiftyScanner:
#     def __init__(self, provider):
#         self.provider = provider
#         print(f"DEBUG: Scanner received provider of type: {type(self.provider)}")
#         print(f"DEBUG: Does provider have 'get_candle_history'? {hasattr(self.provider, 'get_candle_history')}")
        
#     def scan_stock(self, token, symbol_name):
#         # 1. Fetch Daily Data (Get 500 days to ensure enough history for Monthly RSI)
#         df_daily = self.provider.get_candle_history(token, interval="ONE_DAY", days=700)
        
#         if df_daily is None or df_daily.empty:
#             return None

#         # 2. Resample Data
#         df_weekly = TechnicalAnalysis.resample_data(df_daily, timeframe='W') # Weekly
#         df_monthly = TechnicalAnalysis.resample_data(df_daily, timeframe='ME') # Monthly

#         # 3. Calculate RSI for all timeframes
#         # We use iloc[-1] to get the CURRENT value
        
#         # DAILY RSI
#         df_daily['rsi'] = TechnicalAnalysis.calculate_rsi(df_daily['close'])
#         daily_rsi = df_daily['rsi'].iloc[-1]

#         # WEEKLY RSI
#         df_weekly['rsi'] = TechnicalAnalysis.calculate_rsi(df_weekly['close'])
#         if len(df_weekly) < 14: return None # Not enough data
#         weekly_rsi = df_weekly['rsi'].iloc[-1]

#         # MONTHLY RSI
#         df_monthly['rsi'] = TechnicalAnalysis.calculate_rsi(df_monthly['close'])
#         if len(df_monthly) < 14: return None
#         monthly_rsi = df_monthly['rsi'].iloc[-1]

#         # 4. APPLY YOUR LOGIC
#         # Condition A: Monthly > 60 AND Weekly > 60
#         condition_trend = (monthly_rsi > 60) and (weekly_rsi > 60)
        
#         # Condition B: Daily is (38-42) OR (58-62)
#         cond_daily_pullback = (38 <= daily_rsi <= 42)
#         cond_daily_breakout = (58 <= daily_rsi <= 62)
        
#         if condition_trend and (cond_daily_pullback or cond_daily_breakout):
#             return {
#                 "symbol": symbol_name,
#                 "monthly_rsi": round(monthly_rsi, 2),
#                 "weekly_rsi": round(weekly_rsi, 2),
#                 "daily_rsi": round(daily_rsi, 2),
#                 "status": "MATCH FOUND 🚀"
#             }
        
#         return None

from core.analysis import TechnicalAnalysis
import pandas as pd

class NiftyScanner:
    def __init__(self, provider):
        self.provider = provider
        # Debug prints kept as per your request
        print(f"DEBUG: Scanner received provider of type: {type(self.provider)}")
        print(f"DEBUG: Does provider have 'get_candle_history'? {hasattr(self.provider, 'get_candle_history')}")
        
    def scan_stock(self, token, symbol_name):
        # 1. Fetch Daily Data 
        df_daily = self.provider.get_candle_history(token, interval="ONE_DAY", days=700)
        
        if df_daily is None or df_daily.empty:
            return None

        # 2. Resample Data
        df_weekly = TechnicalAnalysis.resample_data(df_daily, timeframe='W') 
        df_monthly = TechnicalAnalysis.resample_data(df_daily, timeframe='ME') 

        # 3. Calculate RSI 
        df_daily['rsi'] = TechnicalAnalysis.calculate_rsi(df_daily['close'])
        df_weekly['rsi'] = TechnicalAnalysis.calculate_rsi(df_weekly['close'])
        df_monthly['rsi'] = TechnicalAnalysis.calculate_rsi(df_monthly['close'])

        # Check Data Length for RSI
        if len(df_weekly) < 14 or len(df_monthly) < 14:
            return None

        # Get Current RSI Values
        try:
            daily_rsi = round(df_daily['rsi'].iloc[-1], 2)
            weekly_rsi = round(df_weekly['rsi'].iloc[-1], 2)
            monthly_rsi = round(df_monthly['rsi'].iloc[-1], 2)
            current_price = df_daily['close'].iloc[-1]
        except Exception:
            return None

        # 4. RSI FILTER LOGIC
        condition_trend = (monthly_rsi > 60) and (weekly_rsi > 60)
        cond_daily_pullback = (38 <= daily_rsi <= 42)
        cond_daily_breakout = (58 <= daily_rsi <= 62)
        
        # 5. SMA & GAP CALCULATION (Only if RSI Valid)
        if condition_trend and (cond_daily_pullback or cond_daily_breakout):
            
            # Calculate 20 SMA
            # We calculate it here to save processing time on failed stocks
            df_daily['sma_20'] = df_daily['close'].rolling(window=20).mean()
            
            # Get latest SMA value
            sma_20 = df_daily['sma_20'].iloc[-1]
            
            # Calculate Gap % ((Price - SMA) / SMA) * 100
            if pd.isna(sma_20) or sma_20 == 0:
                gap_pct = 0.0
            else:
                gap_pct = ((current_price - sma_20) / sma_20) * 100
            
            return {
                "symbol": symbol_name,
                "monthly_rsi": monthly_rsi,
                "weekly_rsi": weekly_rsi,
                "daily_rsi": daily_rsi,
                "status": "MATCH FOUND 🚀",
                # New Data Points
                "sma_20": round(sma_20, 2),
                "price": current_price,
                "sma_gap": round(gap_pct, 2)
            }
        
        return None