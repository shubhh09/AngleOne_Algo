import matplotlib.pyplot as plt
import pandas as pd

class ChartPlotter:
    # ... keep your existing mplfinance code here if you want ...

    @staticmethod
    def plot_impact_zones(df, levels, symbol_name="Stock"):
        # Prepare Data
        df = df.copy().reset_index()
        # Ensure columns are Title Case for this specific script
        df.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'timestamp': 'Date'}, inplace=True)
        df['ID'] = df.index
        
        # Setup Plot
        fig, ax = plt.subplots(figsize=(16, 9))
        ax.set_facecolor('white')
        
        # Draw Custom Candles (Green/Red bars)
        up = df[df.Close >= df.Open]
        down = df[df.Close < df.Open]
        
        ax.bar(up.ID, up.Close-up.Open, 0.6, bottom=up.Open, color="#b1ccb2") #candle color 
        ax.bar(up.ID, up.High-up.Close, 0.05, bottom=up.Close, color='#b1ccb2') #candle color 
        ax.bar(up.ID, up.Low-up.Open, 0.05, bottom=up.Open, color='#b1ccb2') #candle color 
        
        ax.bar(down.ID, down.Open-down.Close, 0.6, bottom=down.Close, color="#C2C3C7") #candle color 
        ax.bar(down.ID, down.High-down.Open, 0.05, bottom=down.Open, color='#C2C3C7') #candle color 
        ax.bar(down.ID, down.Low-down.Close, 0.05, bottom=down.Close, color='#C2C3C7') #candle color 

        # Draw Levels
        current_price = df['Close'].iloc[-1]
        levels.sort(key=lambda x: x['price'])
        
        print("\n--- DETECTED ZONES ---")
        for lvl in levels:
            price = lvl['price']
            role = lvl['type']
            
            if role == "Polarity": color = 'black'; lw = 2; label = "★ FLIP"
            elif current_price > price: color = '#006400'; lw = 1.5; label = "Support"
            else: color = '#8b0000'; lw = 1.5; label = "Resistance"
                
            print(f"{label}: ₹{price:.2f}")
            ax.axhline(price, color=color, linestyle='--', linewidth=lw)
            ax.text(df.ID.iloc[-1]+1, price, f" {label}\n ₹{price:.0f}", color=color, fontweight='bold', va='center')

        ax.set_title(f"{symbol_name} - Smart Money Zones", fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.show()