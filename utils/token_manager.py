# --------------------------------------------------------- WORKING ONLY FOR GET 200 LIST 
# import requests
# import json
# import os
# import pandas as pd

# class TokenManager:
#     # Official URL from Angel One
#     JSON_URL = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
#     FILE_PATH = "data/OpenAPIScripMaster.json"

#     @staticmethod
#     def get_nifty_tokens(limit=200):
#         """
#         Downloads master file and returns a dict of Top 'limit' NSE Stocks.
#         """
#         # 1. Check if file exists, else download
#         if not os.path.exists(TokenManager.FILE_PATH):
#             print("⏳ Downloading Scrip Master (This happens once)...")
#             response = requests.get(TokenManager.JSON_URL)
#             if response.status_code == 200:
#                 with open(TokenManager.FILE_PATH, "w") as f:
#                     f.write(response.text)
#                 print("✅ Download Complete.")
#             else:
#                 print("❌ Failed to download Scrip Master.")
#                 return {}

#         # 2. Load JSON into DataFrame
#         print("📂 Loading Token List...")
#         with open(TokenManager.FILE_PATH, "r") as f:
#             data = json.load(f)
            
#         df = pd.DataFrame(data)
        
#         # 3. FILTER LOGIC: Get only NSE Equity (Series 'EQ')
#         # We filter for: "NSE" segment, "-EQ" in symbol, and no strange instruments
#         mask = (df['exch_seg'] == 'NSE') & \
#                (df['symbol'].str.endswith('-EQ')) & \
#                (df['instrumenttype'] == '')
               
#         filtered_df = df[mask].copy()
        
#         # 4. Sorting / Limiting (Optional)
#         # Since we don't know "Market Cap" from this JSON, we return the list.
#         # If you want SPECIFIC Nifty 200, you usually need a separate list of names.
#         # For now, we return the first 'limit' stocks or ALL if limit is None.
        
#         if limit:
#             filtered_df = filtered_df.head(limit)
            
#         # Convert to Dictionary: {"RELIANCE-EQ": "2885", ...}
#         token_map = dict(zip(filtered_df['token'], filtered_df['symbol']))
        
#         print(f"✅ Loaded {len(token_map)} stocks for scanning.")
#         return token_map

# --------------------------------------------------------- WORKING ONLY FOR GET 500 LIST 
import requests
import json
import os
import pandas as pd
import io

class TokenManager:
    # 1. Angel One Master
    ANGEL_URL = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
    ANGEL_FILE = "data/OpenAPIScripMaster.json"
    
    # 2. Local File Paths (We look for these FIRST)
    # Save your downloaded CSVs in the 'data' folder with these names:
    LOCAL_FILES = {
        "NIFTY 50": "data/ind_nifty50list.csv",
        "NIFTY 500": "data/ind_nifty500list.csv"
    }

    # 3. Online URLs (Backup if local file is missing)
    ONLINE_URLS = {
        "NIFTY 50": "https://www.niftyindices.com/IndexConstituent/ind_nifty50list.csv",
        "NIFTY 500": "https://www.niftyindices.com/IndexConstituent/ind_nifty500list.csv"
    }

    @staticmethod
    def get_angel_master_data():
        if not os.path.exists("data"): os.makedirs("data")
        
        if not os.path.exists(TokenManager.ANGEL_FILE):
            print("⏳ Downloading Angel One Master List...")
            try:
                r = requests.get(TokenManager.ANGEL_URL)
                with open(TokenManager.ANGEL_FILE, "w") as f:
                    f.write(r.text)
            except Exception as e:
                print(f"❌ Angel Master Download Failed: {e}")
                return []
        
        with open(TokenManager.ANGEL_FILE, "r") as f:
            return json.load(f)

    @staticmethod
    def get_market_categories():
        category_map = {}
        all_symbols = set()
        
        print("\n🌍 Loading Market Data...")

        # Loop through our configured lists (50 and 500)
        for index_name, local_path in TokenManager.LOCAL_FILES.items():
            df = None
            
            # A. TRY LOCAL FILE FIRST
            if os.path.exists(local_path):
                print(f"   📂 Loading Local File: {index_name}...", end=" ")
                try:
                    df = pd.read_csv(local_path)
                    print("✅ OK")
                except Exception as e:
                    print(f"❌ Read Error: {e}")

            # B. RETRY DOWNLOAD IF LOCAL FAILS
            if df is None:
                url = TokenManager.ONLINE_URLS[index_name]
                print(f"   ⬇️  Downloading {index_name}...", end=" ")
                try:
                    # Added verify=False to bypass SSL errors and timeout=30s
                    headers = {'User-Agent': 'Mozilla/5.0'}
                    r = requests.get(url, headers=headers, timeout=30) 
                    
                    if r.status_code == 200:
                        df = pd.read_csv(io.StringIO(r.content.decode('utf-8')))
                        
                        # Optional: Save it locally for next time
                        df.to_csv(local_path, index=False)
                        print("✅ Downloaded & Saved")
                    else:
                        print(f"❌ Failed (HTTP {r.status_code})")
                except Exception as e:
                    print(f"❌ Timeout/Error: {e}")

            # C. PROCESS THE DATA (If we got it)
            if df is not None:
                df.columns = df.columns.str.strip() # Clean headers
                if 'Symbol' in df.columns:
                    symbols = set(df['Symbol'].tolist())
                    all_symbols.update(symbols)
                    for s in symbols:
                        category_map.setdefault(s, []).append(index_name)

        # Map to Angel Tokens
        if not all_symbols:
            print("⚠️ NO SYMBOLS FOUND. Using Fallback list.")
            all_symbols = ["RELIANCE", "SBIN", "TCS", "INFY", "HDFCBANK", "ICICIBANK"]

        angel_data = TokenManager.get_angel_master_data()
        token_map = {}
        
        print(f"⚙️ Mapping {len(all_symbols)} symbols...", end=" ")
        for item in angel_data:
            if item['exch_seg'] == 'NSE' and item['symbol'].endswith('-EQ'):
                clean_name = item['symbol'].replace('-EQ', '')
                if clean_name in all_symbols:
                    token_map[item['token']] = clean_name

        print(f"Done.\n✅ READY TO SCAN: {len(token_map)} STOCKS.\n")
        return token_map, category_map