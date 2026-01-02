# import time
# import pandas as pd
# import pyotp  # <--- NEW IMPORT
# from datetime import datetime, timedelta
# from SmartApi import SmartConnect 

# class AngelOneProvider:
#     # We added 'totp_key' here
#     def __init__(self, api_key, client_code, password, totp_key):
#         self.api = SmartConnect(api_key=api_key)
#         self.client_code = client_code
#         self.password = password
#         self.totp_key = totp_key # Save the key
#         self.login()

#     def login(self):
#         try:
#             # 1. Generate the 6-digit TOTP code automatically
#             totp = pyotp.TOTP(self.totp_key).now()
            
#             # 2. Pass it to generateSession
#             data = self.api.generateSession(self.client_code, self.password, totp)
            
#             if data['status']:
#                 print("✅ Login Successful")
#                 self.auth_token = data['data']['jwtToken']
#                 self.feed_token = self.api.getfeedToken()
#             else:
#                 print(f"❌ Login Failed: {data['message']}")
#         except Exception as e:
#             print(f"❌ Login Error: {e}")

#     # def get_candle_history(self, symbol_token, interval="FIVE_MINUTE"):
#     # def get_candle_history(self, symbol_token, interval="ONE_DAY"):
#     #     # ... (This part of the code remains the same as before) ...
#     #     to_date = datetime.now()
#     #     from_date = to_date - timedelta(days=30)
#     #     print("~~~~fromDate:- ",from_date)
        
#     #     params = {
#     #         "exchange": "NSE",
#     #         "symboltoken": symbol_token,
#     #         "interval": interval,
#     #         "fromdate": from_date.strftime("%Y-%m-%d %H:%M"),
#     #         "todate": to_date.strftime("%Y-%m-%d %H:%M")
#     #     }
        
#     #     try:
#     #         print(f"Fetching data for Token {symbol_token}...")
#     #         response = self.api.getCandleData(params)
#     #         if response and response.get('status') and response.get('data'):
#     #             columns = ["timestamp", "open", "high", "low", "close", "volume"]
#     #             df = pd.DataFrame(response['data'], columns=columns)
#     #             df['close'] = df['close'].astype(float)
#     #             print("--- Historical Data Loaded ---")
#     #             print(df[['timestamp', 'close']].tail(5))
#     #             return df
#     #         else:
#     #             print("⚠️ No data returned.")
#     #             return None
#     #     except Exception as e:
#     #         print(f"❌ Data Fetch Error: {e}")
#     #         return None

# # ✅ FIX: Add 'days=30' to the definition line
# # data/angel_interface.py

#     def get_candle_history(self, symbol_token, interval="ONE_DAY", days=30):
#         to_date = datetime.now()
#         from_date = to_date - timedelta(days=days)
        
#         params = {
#             "exchange": "NSE",
#             "symboltoken": symbol_token,
#             "interval": interval,
#             "fromdate": from_date.strftime("%Y-%m-%d %H:%M"),
#             "todate": to_date.strftime("%Y-%m-%d %H:%M")
#         }
        
#         # 🟢 UPGRADED RETRY LOGIC
#         max_retries = 5  # Try 5 times (instead of 3)
        
#         for attempt in range(max_retries):
#             try:
#                 response = self.api.getCandleData(params)
                
#                 # 1. SUCCESS CASE
#                 if response and response.get('status') and response.get('data'):
#                     columns = ["timestamp", "open", "high", "low", "close", "volume"]
#                     df = pd.DataFrame(response['data'], columns=columns)
#                     df['close'] = df['close'].astype(float)
#                     return df
                
#                 # 2. RATE LIMIT CASE (Server says "Wait")
#                 elif response and response.get('errorcode') == 'AB1004':
#                     print(f"   ⚠️ Rate Limit hit. Cooling down for 2s... ({attempt+1}/{max_retries})")
#                     time.sleep(2)
#                     continue

#                 # 3. OTHER API ERROR (Invalid Token, etc.)
#                 else:
#                     # If it's the last attempt, return None
#                     if attempt == max_retries - 1:
#                         return None
            
#             # 4. NETWORK CRASH CASE (Timeout / Connection Error)
#             except Exception as e:
#                 print(f"   ⚠️ Connection Timeout. Waiting 5s... ({attempt+1}/{max_retries})")
#                 # Important: Wait longer for network issues
#                 time.sleep(5) 
#                 continue
        
#         return None

import pandas as pd
from datetime import datetime, timedelta
import pyotp
import os
import time
from SmartApi import SmartConnect 

class AngelOneProvider:
    def __init__(self, api_key, client_code, password, totp_key):
        self.api = SmartConnect(api_key=api_key)
        self.client_code = client_code
        self.password = password
        self.totp_key = totp_key
        
        # Create a folder for our cache
        self.cache_dir = "data/cache"
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
            
        self.login()

    def login(self):
        try:
            totp = pyotp.TOTP(self.totp_key).now()
            data = self.api.generateSession(self.client_code, self.password, totp)
            if data['status']:
                print("✅ Login Successful")
                self.auth_token = data['data']['jwtToken']
            else:
                print(f"❌ Login Failed: {data['message']}")
        except Exception as e:
            print(f"❌ Login Error: {e}")

    def get_candle_history(self, symbol_token, interval="ONE_DAY", days=30):
        # 1. SETUP CACHE FILENAME
        # e.g. "data/cache/3045.csv"
        cache_file = os.path.join(self.cache_dir, f"{symbol_token}.csv")
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        # 2. CHECK LOCAL CACHE FIRST
        if os.path.exists(cache_file):
            # Check if file was modified TODAY
            file_time = os.path.getmtime(cache_file)
            file_date = datetime.fromtimestamp(file_time).strftime("%Y-%m-%d")
            
            if file_date == today_str:
                # print(f"   📂 Loaded {symbol_token} from Cache (Fast)")
                try:
                    df = pd.read_csv(cache_file)
                    df['timestamp'] = pd.to_datetime(df['timestamp']) # Restore date format
                    return df
                except:
                    pass # If file is corrupt, ignore and fetch new
        
        # 3. FETCH FROM API (If Cache is missing or old)
        # print(f"   ⬇️  Fetching {symbol_token} from API...")
        
        to_date = datetime.now()
        from_date = to_date - timedelta(days=days)
        
        params = {
            "exchange": "NSE",
            "symboltoken": symbol_token,
            "interval": interval,
            "fromdate": from_date.strftime("%Y-%m-%d %H:%M"),
            "todate": to_date.strftime("%Y-%m-%d %H:%M")
        }
        
        # Retry Logic for Stability
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.api.getCandleData(params)
                
                if response and response.get('status') and response.get('data'):
                    columns = ["timestamp", "open", "high", "low", "close", "volume"]
                    df = pd.DataFrame(response['data'], columns=columns)
                    df['close'] = df['close'].astype(float)
                    
                    # 4. SAVE TO CACHE
                    df.to_csv(cache_file, index=False)
                    return df
                
                elif response and response.get('errorcode') == 'AB1004':
                    print(f"   ⚠️ Rate Limit. Waiting 2s...")
                    time.sleep(2)
                    continue
                    
                else:
                    return None
                    
            except Exception as e:
                print(f"   ⚠️ Network Error. Retrying...")
                time.sleep(2)
        
        return None