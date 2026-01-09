#ON RUNNING THIS CODE IT WILL UPDATE FILE FOR NIFTY 500 MONTHLY CANDLE FOR CUP PATTERN THEN RUN python strategy_cup.py 
import os
import time
import requests
import pandas as pd
import io
import json
import pyotp
from datetime import datetime, timedelta
from SmartApi import SmartConnect
from dotenv import load_dotenv

# ==========================================
# ⚙️ CONFIGURATION & CREDENTIALS
# ==========================================
# Make sure your .env file is in the same folder
load_dotenv()
API_KEY = os.getenv("API_KEY")
CLIENT_ID = os.getenv("CLIENT_ID")
PASSWORD = os.getenv("PASSWORD")
TOTP_KEY = os.getenv("TOTP_KEY")

CACHE_DIR = "data/history_cache"
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

# ==========================================
# 🧠 CLASS: ANGEL ONE PROVIDER (The Engine)
# ==========================================
class AngelOneBot:
    def __init__(self, api_key, client_code, password, totp_key):
        self.api = SmartConnect(api_key=api_key)
        self.client_code = client_code
        self.password = password
        self.totp_key = totp_key
        self.login()

    def login(self):
        try:
            print("🔐 Logging in...")
            totp = pyotp.TOTP(self.totp_key).now()
            data = self.api.generateSession(self.client_code, self.password, totp)
            if data['status']:
                print("✅ Login Successful")
                self.auth_token = data['data']['jwtToken']
            else:
                print(f"❌ Login Failed: {data['message']}")
        except Exception as e:
            print(f"❌ Login Error: {e}")

    def get_market_map(self):
        """
        1. Downloads Official NIFTY 500 List.
        2. Downloads Angel One Master List.
        3. Maps them together to get tokens.
        """
        print("\n🌍 Updating NIFTY 500 Stock List...")
        
        # A. Download Nifty 500 from NSE
        nifty_url = "https://www.niftyindices.com/IndexConstituent/ind_nifty500list.csv"
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        try:
            r = requests.get(nifty_url, headers=headers, timeout=10)
            if r.status_code == 200:
                nifty_df = pd.read_csv(io.StringIO(r.content.decode('utf-8')))
                nifty_symbols = set(nifty_df['Symbol'].tolist())
                print(f"   ✅ Fetched {len(nifty_symbols)} symbols from NSE.")
            else:
                print("   ⚠️ Failed to fetch Nifty 500. Using fallback list.")
                nifty_symbols = {"RELIANCE", "TCS", "INFY", "HDFCBANK", "SBIN"} # Fallback
        except Exception as e:
            print(f"   ❌ Network Error: {e}")
            return {}

        # B. Download Angel Master
        angel_url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
        try:
            r = requests.get(angel_url, timeout=15)
            angel_data = r.json()
        except:
            print("   ❌ Failed to download Angel Master.")
            return {}

        # C. Map Symbols to Tokens
        token_map = {}
        print("⚙️  Mapping symbols to tokens...")
        
        for item in angel_data:
            # Filter for NSE Equity
            if item['exch_seg'] == 'NSE' and item['symbol'].endswith('-EQ'):
                clean_sym = item['symbol'].replace('-EQ', '')
                if clean_sym in nifty_symbols:
                    token_map[item['token']] = clean_sym
                    
        print(f"✅ Ready to scan {len(token_map)} stocks.\n")
        return token_map

    def fetch_and_update_history(self, token, symbol):
        """
        Smart Function:
        1. Checks if we already have data from TODAY.
        2. If old or missing, downloads full 25-year history.
        3. Saves it to CSV.
        """
        file_path = os.path.join(CACHE_DIR, f"{symbol}.csv")
        today_str = datetime.now().strftime("%Y-%m-%d")

        # 1. SMART CHECK: Do we need to update?
        if os.path.exists(file_path):
            file_time = os.path.getmtime(file_path)
            file_date = datetime.fromtimestamp(file_time).strftime("%Y-%m-%d")
            
            # If file was modified TODAY, skip it (It's already fresh)
            if file_date == today_str:
                return "SKIPPED (Already Updated)"

        # 2. DOWNLOAD (If needed)
        # Logic: 25 Years of History -> Processed to Monthly
        all_dfs = []
        years = 25
        end_date = datetime.now()
        start_date = end_date - timedelta(days=years*365)
        
        current_from = start_date
        
        while current_from < end_date:
            current_to = current_from + timedelta(days=1500) # 4-year chunks
            if current_to > end_date: current_to = end_date
            
            params = {
                "exchange": "NSE",
                "symboltoken": token,
                "interval": "ONE_DAY", 
                "fromdate": current_from.strftime("%Y-%m-%d %H:%M"),
                "todate": current_to.strftime("%Y-%m-%d %H:%M")
            }
            
            try:
                time.sleep(0.2) # Safety delay
                response = self.api.getCandleData(params)
                if response and response.get('data'):
                    chunk = pd.DataFrame(response['data'], columns=["timestamp", "open", "high", "low", "close", "volume"])
                    all_dfs.append(chunk)
            except:
                pass
            
            current_from = current_to + timedelta(days=1)

        # 3. SAVE DATA
        if all_dfs:
            try:
                full_df = pd.concat(all_dfs)
                
                # Cleanup Types
                cols = ["open", "high", "low", "close", "volume"]
                full_df[cols] = full_df[cols].apply(pd.to_numeric, errors='coerce')
                full_df['timestamp'] = pd.to_datetime(full_df['timestamp'])
                
                # Sort & Dedup
                full_df.sort_values('timestamp', inplace=True)
                full_df.drop_duplicates(subset=['timestamp'], inplace=True)
                
                # Save Raw Daily Data (You can resample to monthly later if needed)
                full_df.to_csv(file_path, index=False)
                
                return f"UPDATED ({len(full_df)} days)"
            except Exception as e:
                return f"ERROR: {e}"
        else:
            return "NO DATA FOUND"

# ==========================================
# 🚀 MAIN EXECUTION BLOCK
# ==========================================
def main():
    print("🤖 DAILY MARKET UPDATER STARTED...")
    
    bot = AngelOneBot(API_KEY, CLIENT_ID, PASSWORD, TOTP_KEY)
    
    if hasattr(bot, 'auth_token'):
        # 1. Get List
        stock_map = bot.get_market_map()
        
        # 2. Loop & Update
        total = len(stock_map)
        count = 0
        
        print(f"🚀 Starting Update for {total} stocks...")
        print("   (Data saved to: data/history_cache/)")
        
        try:
            for token, symbol in stock_map.items():
                count += 1
                status = bot.fetch_and_update_history(token, symbol)
                
                # Pretty Print
                print(f"[{count}/{total}] {symbol:<15} : {status}")
                
                # If we actually downloaded (not skipped), sleep a bit
                if "UPDATED" in status:
                    time.sleep(0.3)
                    
        except KeyboardInterrupt:
            print("\n🛑 Stopped by User.")

    print("\n✅ All Done. Files are ready for use.")

if __name__ == "__main__":
    main()