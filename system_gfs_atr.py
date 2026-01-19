
# ----------------------------------------- keep ratio 1:2.5 
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

class AngelGFSBacktester:
    def __init__(self, symbol):
        self.symbol = symbol
        self.strategy_name = "GFS (ATR 1:2.5 Ratio)" 
        self.capital = 100000  
        
        # Risk: 2% of Capital per trade
        self.risk_pct_capital = 0.02 
        self.risk_amount = self.capital * self.risk_pct_capital 
        
        self.input_dir = "data/history_cache"
        self.output_dir = "Backtest/GFS_ATR_2.5"
        
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
        self.df = None
        self.trades_list = []

    def calculate_rsi(self, series, period=14):
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).fillna(0)
        loss = (-delta.where(delta < 0, 0)).fillna(0)
        avg_gain = gain.ewm(com=period-1, min_periods=period, adjust=False).mean()
        avg_loss = loss.ewm(com=period-1, min_periods=period, adjust=False).mean()
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    def calculate_atr(self, df, period=14):
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        return true_range.rolling(window=period).mean()

    def get_data(self):
        path = os.path.join(self.input_dir, f"{self.symbol}.csv")
        if not os.path.exists(path):
            print(f"❌ Error: File not found at {path}")
            return None
        
        print(f"📂 Loading {self.symbol}...")
        df = pd.read_csv(path)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        if df['timestamp'].dt.tz is not None:
            df['timestamp'] = df['timestamp'].dt.tz_localize(None)
        df.set_index('timestamp', inplace=True)
        
        # 25 Year Filter
        cutoff_date = datetime.now() - timedelta(days=365*25)
        if df.index[0] < cutoff_date:
            df = df[df.index >= cutoff_date]
            
        return df

    def prepare_indicators(self, df):
        # Daily
        df['rsi_d'] = self.calculate_rsi(df['close'])
        df['sma_20'] = df['close'].rolling(window=20).mean()
        df['atr'] = self.calculate_atr(df)
        
        # Weekly
        weekly_df = df.resample('W-FRI').agg({'close': 'last'})
        weekly_df['rsi_w'] = self.calculate_rsi(weekly_df['close'])
        weekly_df['rsi_w'] = weekly_df['rsi_w'].shift(1)
        
        # Monthly
        monthly_df = df.resample('ME').agg({'close': 'last'})
        monthly_df['rsi_m'] = self.calculate_rsi(monthly_df['close'])
        monthly_df['rsi_m'] = monthly_df['rsi_m'].shift(1)
        
        df = df.join(weekly_df['rsi_w'], how='left')
        df = df.join(monthly_df['rsi_m'], how='left')
        df.ffill(inplace=True)
        df.dropna(inplace=True)
        return df

    def run(self):
        self.df = self.get_data()
        if self.df is None: return
        self.df = self.prepare_indicators(self.df)
        print(f"🚀 Running GFS (Target 5x ATR)...")
        
        position = False
        current_trade = {}
        
        for i in range(1, len(self.df)):
            curr_date = self.df.index[i]
            row = self.df.iloc[i]
            
            # --- EXIT LOGIC ---
            if position:
                entry_price = current_trade['Entry Price']
                sl_price = current_trade['Stop Loss Price']
                target_price = current_trade['Target Price']
                
                exit_price = None
                exit_reason = ""
                
                if row['low'] <= sl_price:
                    exit_price = row['open'] if row['open'] < sl_price else sl_price
                    exit_reason = "Stop Loss (2x ATR)"
                elif row['high'] >= target_price:
                    exit_price = row['open'] if row['open'] > target_price else target_price
                    exit_reason = "Target (5x ATR)"
                
                if exit_price:
                    quantity = current_trade['Quantity']
                    total_sell_value = quantity * exit_price
                    total_buy_value = quantity * entry_price
                    pnl = total_sell_value - total_buy_value
                    roi_pct = (pnl / total_buy_value) * 100
                    
                    self.trades_list.append({
                        "ENTRY DATE": current_trade['Entry Date'],
                        "ENTRY PRICE": round(entry_price, 2),
                        "QUANTITY": quantity,
                        "TOTAL BUY VALUE": round(total_buy_value, 2),
                        "EXIT PRICE": round(exit_price, 2),
                        "EXIT DATE": curr_date.strftime("%d/%m/%Y"), 
                        "EXIT REASON": exit_reason,
                        "TOTAL SELL VALUE": round(total_sell_value, 2),
                        "P&L": round(pnl, 2),
                        "ROI %": round(roi_pct, 2),
                        "STRATEGY": self.strategy_name
                    })
                    position = False
                    continue

            # --- BUY LOGIC ---
            if not position:
                # Trend Filter
                if (row['rsi_m'] > 60) and (row['rsi_w'] > 60):
                    # Relaxed RSI Range
                    if (row['rsi_d'] >= 35) and (row['rsi_d'] <= 65):
                        # SMA Gap
                        if (abs(row['close'] - row['sma_20']) / row['sma_20']) <= 0.05:
                            
                            entry_price = row['close']
                            atr_value = row['atr']
                            
                            # --- MODIFIED RATIO 1:2.5 ---
                            sl_price = entry_price - (2 * atr_value)  # Risk = 2 ATR
                            target_price = entry_price + (5 * atr_value) # Reward = 5 ATR
                            
                            risk_per_share = entry_price - sl_price
                            quantity = int(self.risk_amount / risk_per_share)
                            if quantity < 1: quantity = 1
                            
                            current_trade = {
                                "Entry Date": curr_date.strftime("%d/%m/%Y"),
                                "Entry Price": entry_price,
                                "Stop Loss Price": sl_price,
                                "Target Price": target_price,
                                "Quantity": quantity
                            }
                            position = True

        # --- SAVE & REPORT ---
        if self.trades_list:
            cols = ["ENTRY DATE", "ENTRY PRICE", "QUANTITY", "TOTAL BUY VALUE", "EXIT PRICE", 
                    "EXIT DATE", "EXIT REASON", "TOTAL SELL VALUE", "P&L", "ROI %", "STRATEGY"]
            results_df = pd.DataFrame(self.trades_list)[cols]
            file_name = f"{self.output_dir}/{self.symbol}_GFS_2_5_result.csv"
            results_df.to_csv(file_name, index=False)
            
            total_profit = results_df['P&L'].sum()
            total_trades = len(results_df)
            winning_trades = len(results_df[results_df['P&L'] > 0])
            target_hits = len(results_df[results_df['EXIT REASON'] == "Target (5x ATR)"])
            sl_hits = len(results_df[results_df['EXIT REASON'] == "Stop Loss (2x ATR)"])
            win_ratio = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
            
            print("\n" + "="*60)
            print(f"📊 FINANCIAL REPORT: {self.symbol} (Ratio 1:2.5)")
            print("="*60)
            print(f"1️⃣  Total Trades        : {total_trades}")
            print(f"2️⃣  Total Profit        : ₹{total_profit:,.2f}")
            print(f"3️⃣  Win Ratio           : {win_ratio:.2f}%")
            print(f"4️⃣  Target Hits (1:2.5) : {target_hits}")
            print(f"5️⃣  SL Hits             : {sl_hits}")
            print("="*60)
            print(f"💾 Saved to: {file_name}")
            
            self.plot_results(self.df, self.trades_list)
        else:
            print("❌ No trades generated.")

    def plot_results(self, df, trades):
        fig, ax = plt.subplots(figsize=(18, 8))
        plot_data = df.tail(1250) 
        if plot_data.empty: return

        ax.plot(plot_data.index, plot_data['close'], label='Price', color='black', alpha=0.6)
        ax.plot(plot_data.index, plot_data['sma_20'], label='20 SMA', color='orange', linestyle='--')

        for trade in trades:
            entry_ts = pd.to_datetime(trade['ENTRY DATE'], format="%d/%m/%Y")
            exit_ts = pd.to_datetime(trade['EXIT DATE'], format="%d/%m/%Y")
            
            if entry_ts >= plot_data.index[0]:
                color = 'green' if trade['P&L'] > 0 else 'red'
                ax.axvspan(entry_ts, exit_ts, color=color, alpha=0.1)
                
                ax.annotate(f"Buy", xy=(entry_ts, trade['ENTRY PRICE']), 
                            xytext=(0, -15), textcoords='offset points', arrowprops=dict(arrowstyle='->', color='blue'), fontsize=7)
                
                roi_label = f"{trade['ROI %']:.1f}%"
                ax.annotate(roi_label, xy=(exit_ts, trade['EXIT PRICE']), 
                            xytext=(0, 15), textcoords='offset points', arrowprops=dict(arrowstyle='->', color=color), fontsize=7, color=color, fontweight='bold')

        ax.set_title(f"{self.symbol} - GFS Ratio 1:2.5 (Target 5x ATR)", fontsize=16)
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        chart_path = f"{self.output_dir}/{self.symbol}_GFS_2_5_chart.png"
        plt.savefig(chart_path, dpi=150, bbox_inches='tight')
        print(f"✅ Chart Saved: {chart_path}")
        plt.close()

if __name__ == "__main__":
    backtester = AngelGFSBacktester("HINDALCO")
    backtester.run()
    
# NIFTY_50_BY_WEIGHT = [
#     "RELIANCE",     # ~9.6% Weight
#     "HDFCBANK",     # ~6.9%
#     "BHARTIARTL",   # ~6.0%
#     "TCS",          # ~5.6%
#     "ICICIBANK",    # ~4.9%
#     "SBIN",         # ~4.6%
#     "INFY",         # ~3.1%
#     "BAJFINANCE",   # ~2.9%
#     "HINDUNILVR",   # ~2.7%
#     "LT",           # ~2.6%
#     "MARUTI",       # ~2.5%
#     "M&M",          # ~2.2%
#     "HCLTECH",      # ~2.2%
#     "ITC",          # ~2.0%
#     "KOTAKBANK",    # ~2.0%
#     "SUNPHARMA",    # ~2.0%
#     "AXISBANK",     # ~1.9%
#     "TITAN",        # ~1.8%
#     "ULTRACEMCO",   # ~1.8%
#     "NTPC",         # ~1.6%
#     "ADANIPORTS",   # ~1.6%
#     "BAJAJFINSV",   # ~1.6%
#     "ONGC",         # ~1.5%
#     "BEL",          # ~1.5%
#     "JSWSTEEL",     # ~1.4%
#     "ETERNAL",      # ~1.4% (Zomato)
#     "ADANIENT",     # ~1.4%
#     "WIPRO",        # ~1.3%
#     "ASIANPAINT",   # ~1.3%
#     "BAJAJ-AUTO",   # ~1.3%
#     "COALINDIA",    # ~1.3%
#     "NESTLEIND",    # ~1.2%
#     "POWERGRID",    # ~1.2%
#     "TATASTEEL",    # ~1.2%
#     "HINDALCO",     # ~1.0%
#     "SBILIFE",      # ~1.0%
#     "EICHERMOT",    # ~1.0%
#     "GRASIM",       # ~0.9%
#     "SHRIRAMFIN",   # ~0.9%
#     "INDIGO",       # ~0.9%
#     "JIOFIN",       # ~0.9%
#     "HDFCLIFE",     # ~0.8%
#     "TECHM",        # ~0.8%
#     "TRENT",        # ~0.7%
#     "TMPV",         # ~0.6% (Tata Motors)
#     "TATACONSUM",   # ~0.6%
#     "CIPLA",        # ~0.6%
#     "APOLLOHOSP",   # ~0.5%
#     "MAXHEALTH",    # ~0.5%
#     "DRREDDY"       # ~0.5%
# ]