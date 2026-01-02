from utils.token_manager import TokenManager

print("🔍 STARTING DIAGNOSTIC TEST...")

# 1. Test Angel One Master List
print("\n[1] Checking Angel One Master List...")
try:
    angel_data = TokenManager.get_angel_master_data()
    print(f"   ✅ Angel One Data Loaded: {len(angel_data)} items found.")
except Exception as e:
    print(f"   ❌ FAILED to load Angel One Data: {e}")

# 2. Test Nifty Download
print("\n[2] Testing Nifty 50 CSV Download...")
try:
    # Run the function that's failing silently
    stock_map, cat_map = TokenManager.get_market_categories()
    
    print(f"\n[3] RESULT:")
    print(f"   ✅ Total Stocks Mapped: {len(stock_map)}")
    
    if len(stock_map) == 0:
        print("   ❌ ERROR: Result is empty! The CSV download likely failed or was blocked.")
    else:
        first_stock = list(stock_map.values())[0]
        print(f"   ✅ Success! First stock found: {first_stock}")

except Exception as e:
    print(f"   ❌ CRASHED: {e}")

print("\n🔍 END OF TEST.")