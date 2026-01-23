# GET CUP PATTERN FOR ALL 2000+ STOCKS FROM YAHOO FINANCE API -- INDIVIDUALLY FILE FOR ONLY NIFTY 2000+ STOCKS -- RUN THESE AND GET ALL CUP PATTERN STOCKS 

import yfinance as yf
import pandas as pd
import os
import time
from datetime import datetime, timedelta
from utils.token_manager import TokenManager
from colorama import Fore, Style, init

# <--- NEW: Import your Telegram Bot --->
from telegram.telegram_alert import TelegramBot

# Initialize colors
init(autoreset=True)

class FullMarketScanner:
    def __init__(self):
        self.cache_dir = "data/cache"
        self.results_file = "cup_patterns_found_yahoo.csv"
        
        # <--- NEW: Initialize Bot --->
        self.bot = TelegramBot()

        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def get_stock_list(self):
        """Fetch all NSE Equity stocks from Angel Master."""
        print(f"{Fore.YELLOW}🌍 Fetching Master Stock List...{Style.RESET_ALL}")
        angel_data = TokenManager.get_angel_master_data()
        
        stock_list = []
        for item in angel_data:
            if item['exch_seg'] == 'NSE' and \
               item['symbol'].endswith('-EQ') and \
               "TEST" not in item['symbol']:
                
                symbol = item['symbol'].replace('-EQ', '')
                token = item['token']
                stock_list.append((token, symbol))
                
        print(f"✅ Found {len(stock_list)} Stocks to Scan.")
        return stock_list

    def fetch_data(self, token, symbol):
        """
        Tries to load data from Cache first.
        If missing, downloads from Yahoo Finance.
        """
        cache_path = os.path.join(self.cache_dir, f"{token}_MONTHLY.csv")
        
        # 1. CHECK CACHE
        if os.path.exists(cache_path):
            try:
                df = pd.read_csv(cache_path)
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                return df
            except:
                pass # Corrupt file, re-download

        # 2. DOWNLOAD FROM YAHOO
        try:
            yf_symbol = f"{symbol}.NS"
            # Auto-adjust=True fixes Splits/Bonuses automatically
            df = yf.download(yf_symbol, period="max", interval="1mo", progress=False, auto_adjust=True)
            
            if df is None or df.empty or len(df) < 60: # Need 5 years min
                return None

            # Flatten MultiIndex (Fix for new yfinance versions)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            # Format Columns
            df.reset_index(inplace=True)
            df.columns = [c.lower() for c in df.columns]
            if 'date' in df.columns: df.rename(columns={'date': 'timestamp'}, inplace=True)
            
            # Keep only needed columns
            req_cols = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
            if not all(c in df.columns for c in req_cols): return None
            
            final_df = df[req_cols]
            
            # Save to Cache
            final_df.to_csv(cache_path, index=False)
            return final_df

        except Exception:
            return None

    def detect_patterns(self, df):
        """
        Checks for:
        1. Multi-Year Cup Breakout (>5 Yrs)
        2. Cup & Handle
        """
        if df is None: return None
        
        current_price = df['close'].iloc[-1]
        current_date = df['timestamp'].iloc[-1]
        
        # --- LOGIC: FIND ANCIENT HIGH (> 5 Years Ago) ---
        five_years_ago = current_date - timedelta(days=365*5)
        ancient_df = df[df['timestamp'] < five_years_ago]
        
        if ancient_df.empty: return None
        
        ancient_high_idx = ancient_df['high'].idxmax()
        left_lip = ancient_df['high'].loc[ancient_high_idx]
        left_lip_date = ancient_df['timestamp'].loc[ancient_high_idx]
        
        # Age Calculation
        age_years = round((current_date - left_lip_date).days / 365, 1)
        if age_years < 5.0: return None

        # --- LOGIC: VIRGIN CHECK (Price never crossed high in between) ---
        check_end = current_date - timedelta(days=90)
        mask = (df['timestamp'] > left_lip_date) & (df['timestamp'] < check_end)
        intermediate = df.loc[mask]
        
        if not intermediate.empty:
            mid_high = intermediate['high'].max()
            if mid_high > (left_lip * 1.02): return None # Failed pattern

        # --- LOGIC: PATTERN CLASSIFICATION ---
        
        # 1. CLASSIC CUP (Near Breakout)
        dist_pct = ((current_price - left_lip) / left_lip) * 100
        
        if -15 <= dist_pct <= 10:
            return {
                "Pattern": "CLASSIC CUP (5yr+)",
                "Target_High": round(left_lip, 2),
                "Age_Years": age_years,
                "Distance_Pct": round(dist_pct, 1),
                "Status": "BREAKOUT" if dist_pct > 0 else "NEAR RESISTANCE"
            }
            
        # 2. CUP & HANDLE (Recent Handle Formation)
        # Look for a recent peak (Right Lip) in last 2 years
        two_yrs_ago = current_date - timedelta(days=730)
        recent_df = df[df['timestamp'] > two_yrs_ago]
        
        if not recent_df.empty:
            right_lip = recent_df['high'].max()
            
            # Is Right Lip aligned with Ancient Left Lip? (+/- 15%)
            if 0.85 * left_lip < right_lip < 1.15 * left_lip:
                
                # Check if we are currently in a "Handle" (pullback from right lip)
                handle_drop = ((right_lip - current_price) / right_lip) * 100
                
                if 2 <= handle_drop <= 15: # Handle depth 2-15%
                    return {
                        "Pattern": "CUP & HANDLE",
                        "Target_High": round(right_lip, 2),
                        "Age_Years": age_years,
                        "Distance_Pct": round(-handle_drop, 1), # Negative means below handle top
                        "Status": "FORMING HANDLE"
                    }

        return None

    def run(self):
        print(f"{Fore.GREEN}🚀 STARTING FULL MARKET SCAN (Yahoo Finance + Cup Logic)...{Style.RESET_ALL}")
        
        stocks = self.get_stock_list()
        matches = []
        
        print(f"💾 Results will be saved to: {self.results_file}\n")
        
        for i, (token, symbol) in enumerate(stocks):
            # Progress bar
            print(f"[{i+1}/{len(stocks)}] Scanning {symbol:<15} ...", end="\r")
            
            # 1. Fetch
            df = self.fetch_data(token, symbol)
            
            # 2. Analyze
            if df is not None:
                result = self.detect_patterns(df)
                
                if result:
                    result['Symbol'] = symbol
                    result['Current_Price'] = round(df['close'].iloc[-1], 2)
                    matches.append(result)
                    
                    # Print Match
                    c = Fore.GREEN if "BREAKOUT" in result['Status'] else Fore.CYAN
                    print(f"✨ {c}FOUND: {symbol:<12} | {result['Pattern']} | {result['Age_Years']} Yr Base{Style.RESET_ALL}   ")

            # Tiny sleep to be polite to Yahoo
            if i % 20 == 0: time.sleep(0.2)

        # --- SAVE RESULTS ---
        print("\n" + "="*60)
        if matches:
            results_df = pd.DataFrame(matches)
            
            # Reorder columns
            cols = ['Symbol', 'Pattern', 'Status', 'Current_Price', 'Target_High', 'Distance_Pct', 'Age_Years']
            results_df = results_df[cols]
            
            # Save to CSV
            results_df.to_csv(self.results_file, index=False)
            
            print(f"✅ SCAN COMPLETE. Found {len(matches)} stocks.")
            print(f"📂 Data saved to '{self.results_file}'")
            print("="*60)
            print(results_df.head(10).to_string()) # Show preview

        # ... (Existing code above) ...
            
            # --- IMPROVED TELEGRAM REPORT (Grouped) ---
            print(f"\n📤 Sending Detailed Report to Telegram...")
            
            # 1. SEPARATE THE LISTS
            # Filter rows containing "BREAKOUT"
            breakouts = results_df[results_df['Status'].str.contains("BREAKOUT")]
            # Filter rows NOT containing "BREAKOUT" (Handles/Near)
            watchlist = results_df[~results_df['Status'].str.contains("BREAKOUT")]

            # --- MESSAGE 1: BREAKOUTS (Actionable) ---
            if not breakouts.empty:
                msg = f"🚀 **BREAKOUT ALERT** ({len(breakouts)} Stocks)\n"
                msg += "Strategy: Cup Pattern (>5 Yr)\n\n"
                msg += "```\n"
                # Showing TARGET for breakouts
                msg += f"{'SYMBOL':<10} {'PRICE':<8} {'TARGET':<8}\n"
                msg += "-"*28 + "\n"
                
                for _, row in breakouts.iterrows():
                     # Format Target to remove decimal if clean
                     tgt = f"{row['Target_High']:.1f}"
                     msg += f"{row['Symbol'][:10]:<10} {row['Current_Price']:<8} {tgt:<8}\n"
                msg += "```"
                self.bot.send_msg(msg)

            # --- MESSAGE 2: WATCHLIST (Forming) ---
            if not watchlist.empty:
                msg = f"👀 **WATCHLIST (Forming)** ({len(watchlist)} Stocks)\n"
                msg += "Status: Cup/Handle Forming\n\n"
                msg += "```\n"
                # Showing DISTANCE % for watchlist (How far to breakout)
                msg += f"{'SYMBOL':<10} {'PRICE':<8} {'DIST%':<6}\n"
                msg += "-"*26 + "\n"
                
                # Limit to top 20 to avoid spamming
                for _, row in watchlist.head(20).iterrows():
                     dist = f"{row['Distance_Pct']}%"
                     msg += f"{row['Symbol'][:10]:<10} {row['Current_Price']:<8} {dist:<6}\n"
                
                if len(watchlist) > 20:
                    msg += f"... +{len(watchlist)-20} more in CSV"
                msg += "```"
                self.bot.send_msg(msg)
            
            print("✅ Telegram Messages Sent.")
            
        else:
            print("❌ Scan Complete. No patterns found matching strict criteria.")

if __name__ == "__main__":
    scanner = FullMarketScanner()
    scanner.run()