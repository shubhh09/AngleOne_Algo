# FINDING CUP PATTERN IN NIFTY 500 USING ANGLE ONE API'S ----- TO UPDATE NIFTY 500 DATA USE --- python daily_nifty500_updater.py
import pandas as pd
import numpy as np
import os
from utils.token_manager import TokenManager
from datetime import datetime, timedelta
from colorama import Fore, Style, init

# Initialize colors for pretty printing
init(autoreset=True)

class LongTermCupScanner:
    
    def __init__(self):
        # Ensure this matches where your main.py saves data
        self.cache_dir = "data/cache" 
        
    def detect_5yr_plus_cup(self, df):
        """
        Scans for a Cup Pattern strictly longer than 5 Years.
        """
        # We need at least 5 years of data (approx 60 months)
        if len(df) < 60: return None 
        
        current_date = df['timestamp'].iloc[-1]
        current_price = df['close'].iloc[-1]
        
        # 1. Define "Ancient" History (> 5 Years Ago)
        five_years_ago = current_date - timedelta(days=365*5)
        ancient_df = df[df['timestamp'] < five_years_ago]
        
        if ancient_df.empty: return None
        
        # 2. Find the "Left Lip" (Highest High in ancient history)
        ancient_high_idx = ancient_df['high'].idxmax()
        left_lip_price = ancient_df['high'].loc[ancient_high_idx]
        left_lip_date = ancient_df['timestamp'].loc[ancient_high_idx]
        
        base_age_years = round((current_date - left_lip_date).days / 365, 1)
        if base_age_years < 5.0:
            return None

        # 3. The "Virgin" Check (Price never crossed high in the middle)
        check_date_end = current_date - timedelta(days=90)
        
        mask = (df['timestamp'] > left_lip_date) & (df['timestamp'] < check_date_end)
        intermediate_data = df.loc[mask]
        
        if not intermediate_data.empty:
            intermediate_high = intermediate_data['high'].max()
            if intermediate_high > (left_lip_price * 1.02):
                return None

        # 4. Current Proximity (Are we near the breakout?)
        dist_pct = ((current_price - left_lip_price) / left_lip_price) * 100
        
        if not (-25 <= dist_pct <= 10):
            return None 

        # 5. Calculate Depth
        cup_bottom = intermediate_data['low'].min()
        depth_pct = ((left_lip_price - cup_bottom) / left_lip_price) * 100
        
        # Status Label
        if current_price > left_lip_price:
            status = "BREAKOUT 🚀"
        elif dist_pct > -5:
            status = "READY TO GO ⚠️"
        else:
            status = "BUILDING RHS"

        return {
            "Symbol": "", 
            "Current": round(current_price, 2),
            "Target_High": round(left_lip_price, 2),
            "High_Date": left_lip_date.strftime('%Y-%b'),
            "Years": base_age_years,
            "Depth": round(depth_pct, 1),
            "Distance": round(dist_pct, 1),
            "Status": status
        }

    def run(self):
        print(f"\n{Fore.YELLOW}🏛️  SCANNING NIFTY 500 FOR HUGE CUPS (> 5 YEARS)...{Style.RESET_ALL}")
        
        # 1. Get All Stocks & Categories
        stock_map, cat_map = TokenManager.get_market_categories()
        
        # 2. FILTER FOR NIFTY 500
        target_map = {
            token: symbol 
            for token, symbol in stock_map.items() 
            if "NIFTY 500" in cat_map.get(symbol, [])
        }
        
        total_stocks = len(target_map)
        print(f"📋 Target List: {total_stocks} Stocks (Nifty 500)")
        
        if total_stocks < 400:
            print(f"{Fore.RED}⚠️ Warning: Only found {total_stocks} stocks. Did you download the Nifty 500 list in main.py?{Style.RESET_ALL}")

        matches = []
        count = 0
        missing_files = 0
        
        # 3. SCAN LOOP
        for token, symbol in target_map.items():
            clean_name = symbol.replace('-EQ', '')
            file_path = os.path.join(self.cache_dir, f"{token}_MONTHLY.csv")
            
            if os.path.exists(file_path):
                try:
                    df = pd.read_csv(file_path)
                    if 'timestamp' in df.columns:
                        df['timestamp'] = pd.to_datetime(df['timestamp'])
                        result = self.detect_5yr_plus_cup(df)
                        
                        if result:
                            result['Symbol'] = clean_name
                            matches.append(result)
                            # Live Print Match
                            c = Fore.GREEN if "BREAKOUT" in result['Status'] else Fore.CYAN
                            print(f"✨ {c}{clean_name:<12}{Style.RESET_ALL} | {result['Years']} Yr Base | Dist: {result['Distance']}%")
                except Exception:
                    pass
            else:
                missing_files += 1
            
            count += 1
            if count % 50 == 0:
                print(f"   ...scanned {count}/{total_stocks}...", end="\r")

        # 4. FINAL REPORT
        print("\n" + "="*100)
        print(f"✅ SCAN COMPLETE. Checked {count} stocks.")
        if missing_files > 0:
            print(f"{Fore.RED}⚠️  Skipped {missing_files} stocks because data was not downloaded yet.{Style.RESET_ALL}")
            print(f"👉 Run 'python main.py' to download the missing Nifty 500 history.")
        
        if matches:
            matches.sort(key=lambda x: x['Distance'], reverse=True)
            print("\n" + "="*100)
            print(f"{'SYMBOL':<15} {'STATUS':<15} {'PRICE':<10} {'HIGH (Yr)':<15} {'AGE (Yrs)':<10} {'DEPTH %':<8} {'DIST %'}")
            print("="*100)
            
            for m in matches:
                c = Fore.GREEN if "BREAKOUT" in m['Status'] else Fore.CYAN
                high_str = f"{m['Target_High']} ({m['High_Date'][:4]})"
                print(f"{c}{m['Symbol']:<15} {m['Status']:<15} {m['Current']:<10} {high_str:<15} {m['Years']:<10} {m['Depth']:<8} {m['Distance']}%{Style.RESET_ALL}")
            
            # Save results
            pd.DataFrame(matches).to_csv("nifty500_cups.csv", index=False)
            print(f"\n💾 Results saved to 'nifty500_cups.csv'")
        else:
            print("\n❌ No >5 Year Cups found near breakout level.")

# =========================================================
# 👇 THIS IS THE MISSING PART THAT MAKES IT RUN
# =========================================================
if __name__ == "__main__":
    scanner = LongTermCupScanner()
    scanner.run()