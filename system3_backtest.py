# This is a legendary strategy known as "The Double Seven", popularized by quant researcher Larry Connors and Cesar Alvarez. It is famous for its robust performance
#  and remarkably high win rates (often 70%+) on indices and large-cap stocks.
# import pandas as pd
# import numpy as np
# import os
# import matplotlib.pyplot as plt
# import matplotlib.dates as mdates

# class AngelSystem3Backtester:
#     def __init__(self, symbol):
#         self.symbol = symbol
#         self.strategy_name = "System 3 (Double Seven)" 
#         self.capital = 100000  # Starting Capital
#         self.risk_per_trade = 1000  
        
#         self.input_dir = "data/history_cache"
#         self.output_dir = "Backtest/System3"
        
#         if not os.path.exists(self.output_dir):
#             os.makedirs(self.output_dir)
            
#         self.df = None
#         self.trades_list = []

#     def get_data(self):
#         path = os.path.join(self.input_dir, f"{self.symbol}.csv")
#         if not os.path.exists(path):
#             print(f"❌ Error: File not found at {path}")
#             return None

#         print(f"📂 Loading {self.symbol} from Angel One Cache...")
#         df = pd.read_csv(path)
#         df['timestamp'] = pd.to_datetime(df['timestamp'])
        
#         if df['timestamp'].dt.tz is not None:
#             df['timestamp'] = df['timestamp'].dt.tz_localize(None)
            
#         df.set_index('timestamp', inplace=True)
#         return df

#     def prepare_indicators(self, df):
#         # 1. Trend Filter
#         df['sma_200'] = df['close'].rolling(window=200).mean()
        
#         # 2. Double 7 Indicators (Price Action)
#         # Lowest Close of last 7 days (Shifted 1 to avoid lookahead)
#         df['min_7'] = df['close'].rolling(window=7).min().shift(1)
        
#         # Highest Close of last 7 days (Shifted 1 to avoid lookahead)
#         df['max_7'] = df['close'].rolling(window=7).max().shift(1)
        
#         df.dropna(inplace=True)
#         return df

#     def run(self):
#         self.df = self.get_data()
#         if self.df is None: return
        
#         self.df = self.prepare_indicators(self.df)
#         print(f"🚀 Running System 3 (Double Seven)...")
        
#         position = False
#         current_trade = {}
        
#         for i in range(1, len(self.df)):
#             curr_date = self.df.index[i]
#             row = self.df.iloc[i]
#             prev_row = self.df.iloc[i-1]
            
#             # --- SELL LOGIC (Exit on 7-Day High) ---
#             if position:
#                 # Rule: Close > Highest Close of last 7 days
#                 if row['close'] > row['max_7']:
                    
#                     exit_price = row['close']
#                     quantity = current_trade['Quantity']
#                     entry_price = current_trade['Entry Price']
                    
#                     total_sell_value = quantity * exit_price
#                     total_buy_value = quantity * entry_price
#                     pnl = total_sell_value - total_buy_value
#                     roi_pct = (pnl / total_buy_value) * 100
                    
#                     self.trades_list.append({
#                         "ENTRY DATE": current_trade['Entry Date'],
#                         "ENTRY PRICE": round(entry_price, 2),
#                         "STOP LOSS": "N/A", # Mean Reversion often uses time-stops or no fixed SL
#                         "RISK PER SHARE": "N/A",
#                         "RISK PER TRADE": self.risk_per_trade,
#                         "QUANTITY": quantity,
#                         "TOTAL BUY VALUE": round(total_buy_value, 2),
#                         "EXIT PRICE": round(exit_price, 2),
#                         "EXIT DATE": curr_date.strftime("%d/%m/%Y"), 
#                         "TOTAL SELL VALUE": round(total_sell_value, 2),
#                         "P&L": round(pnl, 2),
#                         "STRATEGY": self.strategy_name,
#                         "ROI %": round(roi_pct, 2)
#                     })
#                     position = False
#                     continue

#             # --- BUY LOGIC (Double 7 Entry) ---
#             if not position:
#                 # 1. Trend Filter: Close > 200 SMA
#                 if row['close'] > row['sma_200']:
                    
#                     # 2. Entry Trigger: Close < Lowest Close of last 7 days
#                     if row['close'] < row['min_7']:
                        
#                         entry_price = row['close']
                        
#                         # Position Sizing: Since we don't have a tight stop loss, 
#                         # we can't use "Risk/Share". We use Fixed Capital Allocation (e.g. 10% of equity)
#                         # OR we assume a standard volatility risk.
#                         # For consistency with your previous code, let's buy a fixed value chunk.
#                         # Let's allocate ₹25,000 per trade (25% of capital) for safety.
#                         allocation = 25000 
#                         quantity = int(allocation / entry_price)
#                         if quantity < 1: quantity = 1
                        
#                         total_buy_value = quantity * entry_price
                        
#                         current_trade = {
#                             "Entry Date": curr_date.strftime("%d/%m/%Y"),
#                             "Entry Price": entry_price,
#                             "Quantity": quantity,
#                             "Total Buy Value": total_buy_value
#                         }
#                         position = True

#         # --- SAVE & REPORT ---
#         if self.trades_list:
#             cols = ["ENTRY DATE", "ENTRY PRICE", "QUANTITY", "TOTAL BUY VALUE", "EXIT PRICE", 
#                     "EXIT DATE", "TOTAL SELL VALUE", "P&L", "ROI %", "STRATEGY"]
#             results_df = pd.DataFrame(self.trades_list)[cols]
#             file_name = f"{self.output_dir}/{self.symbol}_angel_result.csv"
#             results_df.to_csv(file_name, index=False)
            
#             # Stats
#             total_profit = results_df['P&L'].sum()
#             avg_capital = results_df['TOTAL BUY VALUE'].mean()
            
#             # Win Ratio
#             total_trades = len(results_df)
#             winning_trades = len(results_df[results_df['P&L'] > 0])
#             losing_trades = len(results_df[results_df['P&L'] <= 0])
#             win_ratio = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
            
#             print("\n" + "="*60)
#             print(f"📊 FINANCIAL REPORT: {self.symbol} (Double Seven)")
#             print("="*60)
#             print(f"1️⃣  Total Trades        : {total_trades}")
#             print(f"2️⃣  Total Profit        : ₹{total_profit:,.2f}")
#             print(f"3️⃣  Avg Capital Used    : ₹{avg_capital:,.2f}")
#             print(f"4️⃣  Win Ratio           : {win_ratio:.2f}%")
#             print(f"5️⃣  Winning Trades      : {winning_trades} ({win_ratio:.2f}%)")
#             print(f"6️⃣  Losing Trades       : {losing_trades}")
#             print("="*60)
#             print(f"💾 Saved to: {file_name}")
            
#             self.plot_results(self.df, self.trades_list)
#         else:
#             print("❌ No trades generated.")

#     def plot_results(self, df, trades):
#         fig, ax = plt.subplots(figsize=(18, 8))
        
#         ax.plot(df.index, df['close'], label='Price', color='black', alpha=0.6, linewidth=0.8)
#         ax.plot(df.index, df['sma_200'], label='200 SMA', color='blue', linestyle='--', linewidth=1.2)

#         for trade in trades:
#             entry_ts = pd.to_datetime(trade['ENTRY DATE'], format="%d/%m/%Y")
#             exit_ts = pd.to_datetime(trade['EXIT DATE'], format="%d/%m/%Y")
#             roi = trade['ROI %']
            
#             if entry_ts >= df.index[0]:
#                 color = 'green' if trade['P&L'] > 0 else 'red'
#                 ax.axvspan(entry_ts, exit_ts, color=color, alpha=0.1)
                
#                 # Markers
#                 ax.annotate(f"Buy\n{trade['ENTRY PRICE']}", xy=(entry_ts, trade['ENTRY PRICE']), 
#                             xytext=(0, -25), textcoords='offset points', rotation='vertical',
#                             ha='center', va='top', color='blue', fontsize=7, arrowprops=dict(arrowstyle='->', color='blue', lw=0.8))
                
#                 ax.annotate(f"{trade['EXIT PRICE']}\n({roi:+.1f}%)", xy=(exit_ts, trade['EXIT PRICE']), 
#                             xytext=(0, 25), textcoords='offset points', rotation='vertical',
#                             ha='center', va='bottom', color=color, fontsize=7, arrowprops=dict(arrowstyle='->', color=color, lw=0.8))

#         ax.set_title(f"{self.symbol} - System 3 (Double Seven Strategy)", fontsize=14, fontweight='bold')
#         ax.grid(True, alpha=0.3)
#         ax.legend(loc='upper left')
        
#         chart_path = f"{self.output_dir}/{self.symbol}_chart.png"
#         plt.savefig(chart_path, dpi=150, bbox_inches='tight')
#         print(f"✅ Chart Saved: {chart_path}")
#         print("👉 Open the image to see high-probability swing trades.")
#         plt.close()

# if __name__ == "__main__":
#     backtester = AngelSystem3Backtester("ICICIBANK")
#     backtester.run()

# --------------------------------------------------------

import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

class AngelSystem3Backtester:
    def __init__(self, symbol):
        self.symbol = symbol
        self.strategy_name = "System 3 (Double Seven)" 
        self.capital = 100000  
        self.risk_per_trade = 1000  
        
        self.input_dir = "data/history_cache"
        self.output_dir = "Backtest/System3"
        
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
        self.df = None
        self.trades_list = []

    def get_data(self):
        path = os.path.join(self.input_dir, f"{self.symbol}.csv")
        if not os.path.exists(path):
            print(f"❌ Error: File not found at {path}")
            return None

        print(f"📂 Loading {self.symbol} from Angel One Cache...")
        df = pd.read_csv(path)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        if df['timestamp'].dt.tz is not None:
            df['timestamp'] = df['timestamp'].dt.tz_localize(None)
            
        df.set_index('timestamp', inplace=True)
        return df

    def prepare_indicators(self, df):
        # 1. Trend Filter
        df['sma_200'] = df['close'].rolling(window=200).mean()
        
        # 2. Double 7 Indicators
        df['min_7'] = df['close'].rolling(window=7).min().shift(1)
        df['max_7'] = df['close'].rolling(window=7).max().shift(1)
        
        df.dropna(inplace=True)
        return df

    def run(self):
        self.df = self.get_data()
        if self.df is None: return
        
        self.df = self.prepare_indicators(self.df)
        print(f"🚀 Running System 3 (Double Seven)...")
        
        position = False
        current_trade = {}
        
        for i in range(1, len(self.df)):
            curr_date = self.df.index[i]
            row = self.df.iloc[i]
            prev_row = self.df.iloc[i-1]
            
            # --- SELL LOGIC ---
            if position:
                if row['close'] > row['max_7']:
                    exit_price = row['close']
                    quantity = current_trade['Quantity']
                    entry_price = current_trade['Entry Price']
                    
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
                        "TOTAL SELL VALUE": round(total_sell_value, 2),
                        "P&L": round(pnl, 2),
                        "ROI %": round(roi_pct, 2),
                        "STRATEGY": self.strategy_name
                    })
                    position = False
                    continue

            # --- BUY LOGIC ---
            if not position:
                if row['close'] > row['sma_200']:
                    if row['close'] < row['min_7']:
                        entry_price = row['close']
                        
                        # Fixed Allocation ~25k
                        allocation = 25000 
                        quantity = int(allocation / entry_price)
                        if quantity < 1: quantity = 1
                        
                        total_buy_value = quantity * entry_price
                        
                        current_trade = {
                            "Entry Date": curr_date.strftime("%d/%m/%Y"),
                            "Entry Price": entry_price,
                            "Quantity": quantity,
                            "Total Buy Value": total_buy_value
                        }
                        position = True

        # --- SAVE & REPORT ---
        if self.trades_list:
            cols = ["ENTRY DATE", "ENTRY PRICE", "QUANTITY", "TOTAL BUY VALUE", "EXIT PRICE", 
                    "EXIT DATE", "TOTAL SELL VALUE", "P&L", "ROI %", "STRATEGY"]
            results_df = pd.DataFrame(self.trades_list)[cols]
            file_name = f"{self.output_dir}/{self.symbol}_angel_result.csv"
            results_df.to_csv(file_name, index=False)
            
            total_profit = results_df['P&L'].sum()
            avg_capital = results_df['TOTAL BUY VALUE'].mean()
            
            total_trades = len(results_df)
            winning_trades = len(results_df[results_df['P&L'] > 0])
            losing_trades = len(results_df[results_df['P&L'] <= 0])
            win_ratio = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
            
            print("\n" + "="*60)
            print(f"📊 FINANCIAL REPORT: {self.symbol} (Double Seven)")
            print("="*60)
            print(f"1️⃣  Total Trades        : {total_trades}")
            print(f"2️⃣  Total Profit        : ₹{total_profit:,.2f}")
            print(f"3️⃣  Avg Capital Used    : ₹{avg_capital:,.2f}")
            print(f"4️⃣  Win Ratio           : {win_ratio:.2f}%")
            print(f"5️⃣  Winning Trades      : {winning_trades} ({win_ratio:.2f}%)")
            print(f"6️⃣  Losing Trades       : {losing_trades}")
            print("="*60)
            print(f"💾 Saved to: {file_name}")
            
            # GENERATE TWO CHARTS
            print("\n📈 Generating Charts...")
            self.plot_results(self.df, self.trades_list, full_history=True)
            self.plot_results(self.df, self.trades_list, full_history=False) # Recent 5 Years
        else:
            print("❌ No trades generated.")

    def plot_results(self, df, trades, full_history=True):
        # 1. Select Data Range
        if full_history:
            plot_data = df
            title_suffix = "Full History (25 Years)"
            fname_suffix = "FULL"
            fig_width = 30 # Extra wide for full history
        else:
            # Last 5 Years (approx 1250 trading days)
            plot_data = df.tail(1250)
            title_suffix = "Recent 5 Years (Zoomed)"
            fname_suffix = "RECENT"
            fig_width = 18

        if plot_data.empty: return

        # 2. Setup Plot
        fig, ax = plt.subplots(figsize=(fig_width, 10))
        
        ax.plot(plot_data.index, plot_data['close'], label='Price', color='black', alpha=0.6, linewidth=0.8)
        ax.plot(plot_data.index, plot_data['sma_200'], label='200 SMA', color='blue', linestyle='--', linewidth=1.2)

        start_date = plot_data.index[0]

        for trade in trades:
            entry_ts = pd.to_datetime(trade['ENTRY DATE'], format="%d/%m/%Y")
            exit_ts = pd.to_datetime(trade['EXIT DATE'], format="%d/%m/%Y")
            roi = trade['ROI %']
            
            # Only plot trades inside the visible range
            if entry_ts >= start_date:
                color = 'green' if trade['P&L'] > 0 else 'red'
                ax.axvspan(entry_ts, exit_ts, color=color, alpha=0.1)
                
                # Markers (Smaller Font for Full Chart)
                font_s = 6 if full_history else 8
                
                # Buy Label
                ax.annotate(f"Buy\n{trade['ENTRY PRICE']}\n{trade['ENTRY DATE']}", 
                            xy=(entry_ts, trade['ENTRY PRICE']), 
                            xytext=(0, -20), textcoords='offset points', rotation='vertical',
                            ha='center', va='top', color='blue', fontsize=font_s, 
                            arrowprops=dict(arrowstyle='->', color='blue', lw=0.5))
                
                # Sell Label
                ax.annotate(f"{trade['EXIT PRICE']}\n({roi:+.1f}%)\n{trade['EXIT DATE']}", 
                            xy=(exit_ts, trade['EXIT PRICE']), 
                            xytext=(0, 20), textcoords='offset points', rotation='vertical',
                            ha='center', va='bottom', color=color, fontsize=font_s, 
                            arrowprops=dict(arrowstyle='->', color=color, lw=0.5))

        ax.set_title(f"{self.symbol} - System 3 ({title_suffix})", fontsize=16, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper left')
        
        chart_path = f"{self.output_dir}/{self.symbol}_chart_{fname_suffix}.png"
        plt.savefig(chart_path, dpi=150, bbox_inches='tight')
        print(f"✅ Chart Saved: {chart_path}")
        plt.close()

if __name__ == "__main__":
    backtester = AngelSystem3Backtester("HINDALCO")
    backtester.run()

# Sorted by Nifty 50 Weightage (approx. Market Share)
# Top 5 stocks (Reliance, HDFC Bank, Airtel, TCS, ICICI) control ~33% of the index.

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