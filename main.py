from data.angel_interface import AngelOneProvider
from core.analysis import ImpactZoneAnalyzer
from core.visualizer import ChartPlotter
from strategies.scanner import NiftyScanner
import time
import pandas as pd
# using .env for credentials 
from dotenv import load_dotenv
import os

load_dotenv()
# REPLACE THESE WITH YOUR ACTUAL DETAILS
API_KEY = os.getenv("API_KEY")
CLIENT_ID = os.getenv("CLIENT_ID")
PASSWORD = os.getenv("PASSWORD")
TOTP_KEY = os.getenv("TOTP_KEY")

# def main():
#     print("🤖 Bot Started...")
    
#     # 1. Initialize the Class
#     provider = AngelOneProvider(API_KEY, CLIENT_ID, PASSWORD,TOTP_KEY)
    
#     # 2. Test the function
#     # Token "3045" is SBIN (State Bank of India)
#     # Check if login worked before fetching
#     if hasattr(provider, 'auth_token'):
#        df = provider.get_candle_history("3045", interval="ONE_DAY")
        
#     if df is not None and not df.empty:
#             # -----------------------------------------------------
#             # STEP 2: CALCULATE ZONES (The "Math")
#             # -----------------------------------------------------
#             print("🧠 Analyzing Market Structure...")
#             levels = ImpactZoneAnalyzer.find_focused_levels(df, interval_type="daily")
            
#             # -----------------------------------------------------
#             # STEP 3: DRAW CHART (The "Visual")
#             # -----------------------------------------------------
#             print(f"📉 Plotting {len(levels)} Impact Zones...")
#             ChartPlotter.plot_impact_zones(df, levels, symbol_name="SBIN")
        
#     else:
#         print("Skipping data fetch due to login failure.")

# if __name__ == "__main__":
#     main()

#  ----------------------------------------------------------------------------------- GETTING 200 LIST 

# import time
# from data.angel_interface import AngelOneProvider
# from core.analysis import ImpactZoneAnalyzer
# from strategies.scanner import NiftyScanner
# # IMPORT THE NEW TOOL
# from utils.token_manager import TokenManager

# def main():
#     print("🤖 Market Scanner Bot Started...")
    
#     # 1. Login
#     provider = AngelOneProvider(API_KEY, CLIENT_ID, PASSWORD, TOTP_KEY)
    
#     if hasattr(provider, 'auth_token'):
        
#         # 2. Get Stocks (First 200 NSE Equity Stocks)
#         # Set limit=None to scan ALL 2000+ stocks (Warning: Takes ~20 mins)
#         stock_map = TokenManager.get_nifty_tokens(limit=200)
        
#         scanner = NiftyScanner(provider)
#         matches = []
        
#         print(f"🚀 Starting Scan on {len(stock_map)} stocks...")
#         print("Press Ctrl+C to stop scanning anytime.\n")
        
#         count = 0
#         try:
#             for token, symbol in stock_map.items():
#                 count += 1
#                 clean_name = symbol.replace('-EQ', '')
                
#                 # Print progress on same line
#                 print(f"[{count}/{len(stock_map)}] Scanning {clean_name}...", end="\r")
                
#                 try:
#                     # Run your scanner logic
#                     result = scanner.scan_stock(token, clean_name)
                    
#                     if result:
#                         print(f"\n✨ FOUND: {result['symbol']} | Daily RSI: {result['daily_rsi']}")
#                         matches.append(result)
                        
#                     # ⚠️ CRITICAL: RATE LIMIT PROTECTION
#                     # Angel One allows ~3 requests per second.
#                     # We are safe with 0.35s delay.
#                     time.sleep(0.35) 
                    
#                 except Exception as e:
#                     # Ignore errors for single stocks and continue
#                     continue
                    
#         except KeyboardInterrupt:
#             print("\n🛑 Scan Stopped by User.")

#         # 3. Final Report
#         print("\n" + "="*40)
#         print(f"SCAN REPORT: Found {len(matches)} stocks")
#         print("="*40)
#         for m in matches:
#             print(f"{m['symbol']} | M:{m['monthly_rsi']} W:{m['weekly_rsi']} D:{m['daily_rsi']}")

#     else:
#         print("Login Failed.")

# if __name__ == "__main__":
#     main()

#  ----------------------------------------------------------------------------------- GETTING 500 LIST 
import time
from data.angel_interface import AngelOneProvider
from core.analysis import ImpactZoneAnalyzer
from strategies.scanner import NiftyScanner
# IMPORT THE NEW TOOL
from utils.token_manager import TokenManager

# def main():
#     print("🤖 Market Scanner Bot Started...")
    
#     # 1. Login
#     provider = AngelOneProvider(API_KEY, CLIENT_ID, PASSWORD, TOTP_KEY)
    
#     if hasattr(provider, 'auth_token'):
        
#         # 2. Get Stocks (First 200 NSE Equity Stocks)
#         # Set limit=None to scan ALL 2000+ stocks (Warning: Takes ~20 mins)
#         stock_map, cat_map = TokenManager.get_market_categories()
        
#         scanner = NiftyScanner(provider)
#         matches = []
        
#         print(f"🚀 Starting Scan on {len(stock_map)} stocks...")
#         print("Press Ctrl+C to stop scanning anytime.\n")
        
#         count = 0
#         try:
#             for token, symbol in stock_map.items():
#                 count += 1
#                 clean_name = symbol.replace('-EQ', '')
                
#                 # Print progress on same line
#                 print(f"[{count}/{len(stock_map)}] Scanning {clean_name}...", end="\r")
                
#                 try:
#                     # Run your scanner logic
#                     result = scanner.scan_stock(token, clean_name)
                    
#                     if result:
#                         print(f"\n✨ FOUND: {result['symbol']} | Daily RSI: {result['daily_rsi']}")
#                         matches.append(result)
                        
#                     # ⚠️ CRITICAL: RATE LIMIT PROTECTION
#                     # Angel One allows ~3 requests per second.
#                     # We are safe with 0.35s delay.
#                     time.sleep(0.35) 
                    
#                 except Exception as e:
#                     # Ignore errors for single stocks and continue
#                     continue
                    
#         except KeyboardInterrupt:
#             print("\n🛑 Scan Stopped by User.")

#         # 3. Final Report
#         print("\n" + "="*40)
#         print(f"SCAN REPORT: Found {len(matches)} stocks")
#         print("="*40)
#         for m in matches:
#             print(f"{m['symbol']} | M:{m['monthly_rsi']} W:{m['weekly_rsi']} D:{m['daily_rsi']}")

#     else:
#         print("Login Failed.")

# if __name__ == "__main__":
#     main()
#----------------------------------------------------- FINDING GAP BETWEEN SMA AND CLOSE PRICE
import time
from data.angel_interface import AngelOneProvider
from core.analysis import ImpactZoneAnalyzer
from strategies.scanner import NiftyScanner
from utils.token_manager import TokenManager


def main():
    print("🤖 Market Scanner Bot Started...")
    
    # 1. Login
    provider = AngelOneProvider(API_KEY, CLIENT_ID, PASSWORD, TOTP_KEY)
    
    if hasattr(provider, 'auth_token'):
        
        # 2. Get Stocks 
        stock_map, cat_map = TokenManager.get_market_categories()
        
        scanner = NiftyScanner(provider)
        matches = []
        
        print(f"🚀 Starting Scan on {len(stock_map)} stocks...")
        print("Press Ctrl+C to stop scanning anytime.\n")
        
        count = 0
        try:
            for token, symbol in stock_map.items():
                count += 1
                clean_name = symbol.replace('-EQ', '')
                
                print(f"[{count}/{len(stock_map)}] Scanning {clean_name}...", end="\r")
                
                try:
                    # Run scanner (Now includes SMA logic)
                    result = scanner.scan_stock(token, clean_name)
                    
                    if result:
                        # Add Indices info for display
                        indices = ", ".join(cat_map.get(clean_name, []))
                        result['indices'] = indices
                        
                        matches.append(result)
                        
                        # 🟢 PRINT SMA GAP LIVE
                        print(f"\n✨ FOUND: {clean_name} | RSI: {result['daily_rsi']} | SMA Gap: {result['sma_gap']}%")
                        
                    # Rate Limit
                    time.sleep(0.35) 
                    
                except Exception as e:
                    continue
                    
        except KeyboardInterrupt:
            print("\n🛑 Scan Stopped by User.")

        # 3. Final Report
        print("\n" + "="*90)
        print(f"SCAN REPORT: Found {len(matches)} stocks")
        print("="*90)
        
        # 🟢 UPDATED COLUMNS
        print(f"{'SYMBOL':<15} {'RSI(D)':<8} {'PRICE':<10} {'20 SMA':<10} {'GAP %':<10} {'INDICES'}")
        print("-" * 90)
        
        for m in matches:
            # Color code the gap: Far (>5%) vs Near (<5%)
            gap_str = f"{m['sma_gap']}%"
            
            print(f"{m['symbol']:<15} {m['daily_rsi']:<8} {m['price']:<10} {m['sma_20']:<10} {gap_str:<10} {m['indices']}")

    else:
        print("Login Failed.")

if __name__ == "__main__":
    main()