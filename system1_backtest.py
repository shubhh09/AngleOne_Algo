
# ----------------------------------------------------------------------------

#updated code for get exect data in csv 

# import pandas as pd
# import numpy as np
# import os
# import matplotlib.pyplot as plt
# import matplotlib.dates as mdates

# class AngelSystem1Backtester:
#     def __init__(self, symbol):
#         self.symbol = symbol
#         self.strategy_name = "System 1" 
#         self.capital = 100000  # Starting Capital
#         self.risk_per_trade = 1000  
        
#         self.input_dir = "data/history_cache"
#         self.output_dir = "Backtest/System1"
        
#         if not os.path.exists(self.output_dir):
#             os.makedirs(self.output_dir)
            
#         self.df = None
#         self.trades_list = []

#     def calculate_rsi(self, series, period=14):
#         # Kite/TradingView Formula (Wilder's Smoothing)
#         delta = series.diff()
#         gain = (delta.where(delta > 0, 0)).fillna(0)
#         loss = (-delta.where(delta < 0, 0)).fillna(0)
        
#         avg_gain = gain.ewm(com=period-1, min_periods=period, adjust=False).mean()
#         avg_loss = loss.ewm(com=period-1, min_periods=period, adjust=False).mean()
        
#         rs = avg_gain / avg_loss
#         return 100 - (100 / (1 + rs))

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
#         df['sma_20'] = df['close'].rolling(window=20).mean()
#         df['rsi_d'] = self.calculate_rsi(df['close'])
        
#         weekly_df = df.resample('W-FRI').agg({'close': 'last'})
#         weekly_df['rsi_w'] = self.calculate_rsi(weekly_df['close'])
#         weekly_df['rsi_w'] = weekly_df['rsi_w'].shift(1)
        
#         df = df.join(weekly_df['rsi_w'], how='left')
#         df['rsi_w'] = df['rsi_w'].ffill()
#         df.dropna(inplace=True)
#         return df

#     def run(self):
#         self.df = self.get_data()
#         if self.df is None: return
        
#         self.df = self.prepare_indicators(self.df)
#         print(f"🚀 Running Backtest with Exact Formulas...")
        
#         position = False
#         current_trade = {}
        
#         for i in range(1, len(self.df)):
#             curr_date = self.df.index[i]
#             row = self.df.iloc[i]
#             prev_row = self.df.iloc[i-1]
            
#             # --- SELL LOGIC ---
#             if position:
#                 # Exit if Low touches 20 SMA
#                 if row['low'] <= row['sma_20']:
                    
#                     # Logic: If Open < SMA, sell at Open. Else sell at SMA.
#                     if row['open'] < row['sma_20']:
#                         exit_price = row['open']
#                     else:
#                         exit_price = row['sma_20']
                    
#                     quantity = current_trade['Quantity']
#                     entry_price = current_trade['Entry Price']
                    
#                     # Calculations
#                     total_sell_value = quantity * exit_price
#                     pnl = total_sell_value - (quantity * entry_price)
                    
#                     self.trades_list.append({
#                         "ENTRY DATE": current_trade['Entry Date'],
#                         "ENTRY PRICE": round(entry_price, 2),
#                         "STOP LOSS": round(current_trade['Stop Loss'], 2),
#                         "RISK PER SHARE": round(current_trade['Risk Per Share'], 2),
#                         "RISK PER TRADE": self.risk_per_trade,
#                         "QUANTITY": quantity,
#                         "TOTAL BUY VALUE": round(current_trade['Total Buy Value'], 2),
#                         "EXIT PRICE": round(exit_price, 2),
#                         "EXIT DATE": curr_date.strftime("%d/%m/%Y"), # DD/MM/YYYY
#                         "TOTAL SELL VALUE": round(total_sell_value, 2),
#                         "P&L": round(pnl, 2),
#                         "STRATEGY": self.strategy_name
#                     })
#                     position = False
#                     continue

#             # --- BUY LOGIC ---
#             if not position:
#                 if row['rsi_w'] > 60:
#                     # RSI Crossover
#                     if (prev_row['rsi_d'] < 60) and (row['rsi_d'] >= 60):
                        
#                         if row['close'] > row['sma_20']:
#                             entry_price = row['close']
#                             stop_loss = row['sma_20']
                            
#                             risk_per_share = entry_price - stop_loss
#                             if risk_per_share <= 0: risk_per_share = 0.05
                            
#                             quantity = int(self.risk_per_trade / risk_per_share)
#                             if quantity < 1: quantity = 1
                            
#                             total_buy_value = quantity * entry_price
                            
#                             current_trade = {
#                                 "Entry Date": curr_date.strftime("%d/%m/%Y"), # DD/MM/YYYY
#                                 "Entry Price": entry_price,
#                                 "Stop Loss": stop_loss,
#                                 "Risk Per Share": risk_per_share,
#                                 "Quantity": quantity,
#                                 "Total Buy Value": total_buy_value
#                             }
#                             position = True

#         # --- SAVE & REPORT ---
#         if self.trades_list:
#             cols = ["ENTRY DATE", "ENTRY PRICE", "STOP LOSS", "RISK PER SHARE", "RISK PER TRADE", 
#                     "QUANTITY", "TOTAL BUY VALUE", "EXIT PRICE", "EXIT DATE", "TOTAL SELL VALUE", "P&L", "STRATEGY"]
            
#             results_df = pd.DataFrame(self.trades_list)[cols]
#             file_name = f"{self.output_dir}/{self.symbol}_angel_result.csv"
#             results_df.to_csv(file_name, index=False)
            
#             total_profit = results_df['P&L'].sum()
#             avg_capital = results_df['TOTAL BUY VALUE'].mean()
#             avg_gain = results_df['P&L'].mean()
            
#             print("\n" + "="*60)
#             print(f"📊 FINANCIAL REPORT: {self.symbol}")
#             print("="*60)
#             print(f"1️⃣  Total Trades        : {len(results_df)}")
#             print(f"2️⃣  Total Profit        : ₹{total_profit:,.2f}")
#             print("="*60)
#             print(f"💾 CSV Saved: {file_name}")
            
#             self.plot_results_vertical_with_rsi()
#         else:
#             print("❌ No trades generated.")

#     def plot_results_vertical_with_rsi(self):
#         fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(100, 15), sharex=True, gridspec_kw={'height_ratios': [3, 1]})
#         plot_data = self.df
#         if plot_data.empty: return
        
#         # Plot Price
#         ax1.plot(plot_data.index, plot_data['close'], label='Price', color='black', alpha=0.6)
#         ax1.plot(plot_data.index, plot_data['sma_20'], label='20 SMA', color='orange', linestyle='--')

#         for trade in self.trades_list:
#             entry_ts = pd.to_datetime(trade['ENTRY DATE'], format="%d/%m/%Y")
#             exit_ts = pd.to_datetime(trade['EXIT DATE'], format="%d/%m/%Y")
#             entry_price = trade['ENTRY PRICE']
#             exit_price = trade['EXIT PRICE']
#             pnl = trade['P&L']

#             shade_color = 'green' if pnl > 0 else 'red'
#             ax1.axvspan(entry_ts, exit_ts, color=shade_color, alpha=0.1)

#             ax1.annotate(f"{entry_price}", xy=(entry_ts, entry_price), xytext=(0, -40), textcoords='offset points', ha='center', va='top', rotation='vertical', color='green', fontweight='bold', fontsize=9, arrowprops=dict(arrowstyle='->', color='green', lw=1))
#             sell_color = 'green' if pnl > 0 else 'red'
#             ax1.annotate(f"{exit_price}", xy=(exit_ts, exit_price), xytext=(0, 40), textcoords='offset points', ha='center', va='bottom', rotation='vertical', color=sell_color, fontweight='bold', fontsize=9, arrowprops=dict(arrowstyle='->', color=sell_color, lw=1))

#         ax1.set_ylabel("Price (₹)")
#         ax1.grid(True, linestyle='--', alpha=0.5)
#         ax1.set_title(f"{self.symbol} - Full History Crossover Strategy", fontsize=16, fontweight='bold')

#         ax2.plot(plot_data.index, plot_data['rsi_d'], color='purple', label='RSI')
#         ax2.axhline(60, color='red', linestyle='--')
#         ax2.fill_between(plot_data.index, plot_data['rsi_d'], 60, where=(plot_data['rsi_d'] >= 60), color='green', alpha=0.3)
#         ax2.set_ylabel("RSI")
#         ax2.set_ylim(0, 100)
#         ax2.grid(True, alpha=0.3)

#         fig.autofmt_xdate()
        
#         # Save Chart
#         chart_path = f"{self.output_dir}/{self.symbol}_full_history_rsi_chart.png"
#         import matplotlib as mpl
#         mpl.rcParams['agg.path.chunksize'] = 10000
        
#         print("💾 Saving huge image file...")
#         plt.savefig(chart_path, dpi=150, bbox_inches='tight')
#         print(f"✅ Full History Chart saved to: {chart_path}")
#         print("👉 NOTE: Open this image in a Web Browser to scroll horizontally.")
#         plt.close()

# if __name__ == "__main__":
#     backtester = AngelSystem1Backtester("SBIN")
#     backtester.run()

# ------------------------------------------------------- code with finding stock using system one with new logs

import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

class AngelSystem1Backtester:
    def __init__(self, symbol):
        self.symbol = symbol
        self.strategy_name = "System 1" 
        self.capital = 100000  # Starting Capital
        self.risk_per_trade = 1000  
        
        self.input_dir = "data/history_cache"
        self.output_dir = "Backtest/System1"
        
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
        self.df = None
        self.trades_list = []

    def calculate_rsi(self, series, period=14):
        # Kite/TradingView Formula (Wilder's Smoothing)
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).fillna(0)
        loss = (-delta.where(delta < 0, 0)).fillna(0)
        
        avg_gain = gain.ewm(com=period-1, min_periods=period, adjust=False).mean()
        avg_loss = loss.ewm(com=period-1, min_periods=period, adjust=False).mean()
        
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

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
        df['sma_20'] = df['close'].rolling(window=20).mean()
        df['rsi_d'] = self.calculate_rsi(df['close'])
        
        weekly_df = df.resample('W-FRI').agg({'close': 'last'})
        weekly_df['rsi_w'] = self.calculate_rsi(weekly_df['close'])
        weekly_df['rsi_w'] = weekly_df['rsi_w'].shift(1)
        
        df = df.join(weekly_df['rsi_w'], how='left')
        df['rsi_w'] = df['rsi_w'].ffill()
        df.dropna(inplace=True)
        return df

    def run(self):
        self.df = self.get_data()
        if self.df is None: return
        
        self.df = self.prepare_indicators(self.df)
        print(f"🚀 Running Backtest with Exact Formulas...")
        
        position = False
        current_trade = {}
        
        for i in range(1, len(self.df)):
            curr_date = self.df.index[i]
            row = self.df.iloc[i]
            prev_row = self.df.iloc[i-1]
            
            # --- SELL LOGIC ---
            if position:
                # Exit if Low touches 20 SMA
                if row['low'] <= row['sma_20']:
                    
                    # Logic: If Open < SMA, sell at Open. Else sell at SMA.
                    if row['open'] < row['sma_20']:
                        exit_price = row['open']
                    else:
                        exit_price = row['sma_20']
                    
                    quantity = current_trade['Quantity']
                    entry_price = current_trade['Entry Price']
                    
                    # Calculations
                    total_sell_value = quantity * exit_price
                    pnl = total_sell_value - (quantity * entry_price)
                    
                    self.trades_list.append({
                        "ENTRY DATE": current_trade['Entry Date'],
                        "ENTRY PRICE": round(entry_price, 2),
                        "STOP LOSS": round(current_trade['Stop Loss'], 2),
                        "RISK PER SHARE": round(current_trade['Risk Per Share'], 2),
                        "RISK PER TRADE": self.risk_per_trade,
                        "QUANTITY": quantity,
                        "TOTAL BUY VALUE": round(current_trade['Total Buy Value'], 2),
                        "EXIT PRICE": round(exit_price, 2),
                        "EXIT DATE": curr_date.strftime("%d/%m/%Y"), # DD/MM/YYYY
                        "TOTAL SELL VALUE": round(total_sell_value, 2),
                        "P&L": round(pnl, 2),
                        "STRATEGY": self.strategy_name
                    })
                    position = False
                    continue

            # --- BUY LOGIC ---
            if not position:
                if row['rsi_w'] > 60:
                    # RSI Crossover
                    if (prev_row['rsi_d'] < 60) and (row['rsi_d'] >= 60):
                        
                        if row['close'] > row['sma_20']:
                            entry_price = row['close']
                            stop_loss = row['sma_20']
                            
                            risk_per_share = entry_price - stop_loss
                            if risk_per_share <= 0: risk_per_share = 0.05
                            
                            quantity = int(self.risk_per_trade / risk_per_share)
                            if quantity < 1: quantity = 1
                            
                            total_buy_value = quantity * entry_price
                            
                            current_trade = {
                                "Entry Date": curr_date.strftime("%d/%m/%Y"), # DD/MM/YYYY
                                "Entry Price": entry_price,
                                "Stop Loss": stop_loss,
                                "Risk Per Share": risk_per_share,
                                "Quantity": quantity,
                                "Total Buy Value": total_buy_value
                            }
                            position = True

        # --- SAVE & REPORT ---
        if self.trades_list:
            cols = ["ENTRY DATE", "ENTRY PRICE", "STOP LOSS", "RISK PER SHARE", "RISK PER TRADE", 
                    "QUANTITY", "TOTAL BUY VALUE", "EXIT PRICE", "EXIT DATE", "TOTAL SELL VALUE", "P&L", "STRATEGY"]
            
            results_df = pd.DataFrame(self.trades_list)[cols]
            file_name = f"{self.output_dir}/{self.symbol}_angel_result.csv"
            results_df.to_csv(file_name, index=False)
            
            total_profit = results_df['P&L'].sum()
            avg_capital = results_df['TOTAL BUY VALUE'].mean()
            avg_gain = results_df['P&L'].mean()
            
            # --- NEW WIN RATIO LOGIC ---
            total_trades = len(results_df)
            winning_trades = len(results_df[results_df['P&L'] > 0])
            losing_trades = len(results_df[results_df['P&L'] <= 0])
            win_ratio = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
            
            print("\n" + "="*60)
            print(f"📊 FINANCIAL REPORT: {self.symbol}")
            print("="*60)
            print(f"1️⃣  Total Trades        : {total_trades}")
            print(f"2️⃣  Total Profit        : ₹{total_profit:,.2f}")
            print(f"3️⃣  Avg Capital Used    : ₹{avg_capital:,.2f}")
            print(f"4️⃣  Win Ratio           : {win_ratio:.2f}%")
            print(f"5️⃣  Winning Trades      : {winning_trades} ({win_ratio:.2f}%)")
            print(f"6️⃣  Losing Trades       : {losing_trades}")
            print("="*60)
            print(f"💾 CSV Saved: {file_name}")
            
            self.plot_results_vertical_with_rsi()
        else:
            print("❌ No trades generated.")

    def plot_results_vertical_with_rsi(self):
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(100, 15), sharex=True, gridspec_kw={'height_ratios': [3, 1]})
        plot_data = self.df
        if plot_data.empty: return
        
        # Plot Price
        ax1.plot(plot_data.index, plot_data['close'], label='Price', color='black', alpha=0.6)
        ax1.plot(plot_data.index, plot_data['sma_20'], label='20 SMA', color='orange', linestyle='--')

        for trade in self.trades_list:
            entry_ts = pd.to_datetime(trade['ENTRY DATE'], format="%d/%m/%Y")
            exit_ts = pd.to_datetime(trade['EXIT DATE'], format="%d/%m/%Y")
            entry_price = trade['ENTRY PRICE']
            exit_price = trade['EXIT PRICE']
            pnl = trade['P&L']

            shade_color = 'green' if pnl > 0 else 'red'
            ax1.axvspan(entry_ts, exit_ts, color=shade_color, alpha=0.1)

            ax1.annotate(f"{entry_price}", xy=(entry_ts, entry_price), xytext=(0, -40), textcoords='offset points', ha='center', va='top', rotation='vertical', color='green', fontweight='bold', fontsize=9, arrowprops=dict(arrowstyle='->', color='green', lw=1))
            sell_color = 'green' if pnl > 0 else 'red'
            ax1.annotate(f"{exit_price}", xy=(exit_ts, exit_price), xytext=(0, 40), textcoords='offset points', ha='center', va='bottom', rotation='vertical', color=sell_color, fontweight='bold', fontsize=9, arrowprops=dict(arrowstyle='->', color=sell_color, lw=1))

        ax1.set_ylabel("Price (₹)")
        ax1.grid(True, linestyle='--', alpha=0.5)
        ax1.set_title(f"{self.symbol} - Full History Crossover Strategy", fontsize=16, fontweight='bold')

        ax2.plot(plot_data.index, plot_data['rsi_d'], color='purple', label='RSI')
        ax2.axhline(60, color='red', linestyle='--')
        ax2.fill_between(plot_data.index, plot_data['rsi_d'], 60, where=(plot_data['rsi_d'] >= 60), color='green', alpha=0.3)
        ax2.set_ylabel("RSI")
        ax2.set_ylim(0, 100)
        ax2.grid(True, alpha=0.3)

        fig.autofmt_xdate()
        
        # Save Chart
        chart_path = f"{self.output_dir}/{self.symbol}_full_history_rsi_chart.png"
        import matplotlib as mpl
        mpl.rcParams['agg.path.chunksize'] = 10000
        
        print("💾 Saving huge image file...")
        plt.savefig(chart_path, dpi=150, bbox_inches='tight')
        print(f"✅ Full History Chart saved to: {chart_path}")
        print("👉 NOTE: Open this image in a Web Browser to scroll horizontally.")
        plt.close()

if __name__ == "__main__":
    backtester = AngelSystem1Backtester("HDFCBANK")
    backtester.run()
