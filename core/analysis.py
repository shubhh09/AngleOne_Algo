import numpy as np
import pandas as pd
from scipy.signal import find_peaks
from scipy.stats import gaussian_kde

# FIND SUPPORT AND RESISTANCE
class ImpactZoneAnalyzer:
    
    @staticmethod
    def get_smart_price(cluster_points, role):
        vals = sorted([x[0] for x in cluster_points])
        if len(vals) < 2: return vals[0]
        
        # Priority Logic: Floor vs Ceiling
        if len(vals) >= 3:
            if role == "Support":
                return np.mean(vals[:int(len(vals)*0.4)+1]) # Floor: Bottom 40%
            elif role == "Resistance":
                return np.mean(vals[int(len(vals)*0.6):])   # Ceiling: Top 40%
                
        # Default: Density Peak
        try:
            kde = gaussian_kde(vals, bw_method=0.3)
            x_grid = np.linspace(min(vals), max(vals), 100)
            return x_grid[np.argmax(kde(x_grid))]
        except:
            return np.mean(vals)

    @staticmethod
    def pick_winner(zone, current_price):
        zone.sort(key=lambda x: x['strength'], reverse=True)
        candidates = [z for z in zone if z['strength'] >= zone[0]['strength']*0.8]
        avg = np.mean([z['price'] for z in candidates])
        
        if avg > current_price: candidates.sort(key=lambda x: x['price'], reverse=True)
        else: candidates.sort(key=lambda x: x['price'])
        return candidates[0]

    @staticmethod
    def process_cluster(cluster, current_price):
        if len(cluster) < 2: return []
        vals = [x[0] for x in cluster]
        avg = np.mean(vals)
        has_high = 'High' in [x[1] for x in cluster]
        has_low = 'Low' in [x[1] for x in cluster]
        
        if has_high and has_low: role = "Polarity"
        elif current_price > avg: role = "Support"
        else: role = "Resistance"
        
        price = ImpactZoneAnalyzer.get_smart_price(cluster, role)
        return [{'price': price, 'type': role, 'strength': len(cluster)}]

    @staticmethod
    def consolidate_zones(levels, current_price):
        if not levels: return []
        levels.sort(key=lambda x: x['price'])
        merged = []
        current_zone = [levels[0]]
        
        for i in range(1, len(levels)):
            if levels[i]['price'] < current_zone[-1]['price'] * 1.015: # 1.5% merge threshold
                current_zone.append(levels[i])
            else:
                merged.append(ImpactZoneAnalyzer.pick_winner(current_zone, current_price))
                current_zone = [levels[i]]
        merged.append(ImpactZoneAnalyzer.pick_winner(current_zone, current_price))
        return merged

    @staticmethod
    def find_focused_levels(df, interval_type="daily"):
        # 1. Normalize Columns (Angel One is lowercase, Logic needs Title Case)
        df = df.copy()
        df.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close'}, inplace=True)
        
        highs = df['High'].values
        lows = df['Low'].values
        closes = df['Close'].values
        current_price = df['Close'].iloc[-1]
        
        found_levels = []
        
        # 2. ADAPTIVE SCAN
        # Detect if intraday (5m) or swing (Daily/Weekly)
        if "5m" in interval_type or "minute" in interval_type.lower(): 
            steps = [2.0, 1.5, 1.0, 0.5, 0.2]
            dist = 5
        else: 
            steps = [3.0, 2.0, 1.5, 1.0]
            dist = max(3, len(df)//20)
        
        for prom_mult in steps:
            avg_candle = np.mean(highs - lows)
            prominence = avg_candle * prom_mult
            
            h_idx, _ = find_peaks(highs, distance=dist, prominence=prominence)
            l_idx, _ = find_peaks(-lows, distance=dist, prominence=prominence)
            
            points = []
            for i in h_idx: points.append((highs[i], 'High')); points.append((closes[i], 'Body'))
            for i in l_idx: points.append((lows[i], 'Low')); points.append((closes[i], 'Body'))
            points.sort(key=lambda x: x[0])
            
            # Clustering Logic
            levels = []
            tolerance = df['Close'].mean() * 0.003
            current_cluster = []
            
            for p in points:
                if not current_cluster:
                    current_cluster.append(p)
                    continue
                if abs(p[0] - np.mean([x[0] for x in current_cluster])) < tolerance:
                    current_cluster.append(p)
                else:
                    levels.extend(ImpactZoneAnalyzer.process_cluster(current_cluster, current_price))
                    current_cluster = [p]
            levels.extend(ImpactZoneAnalyzer.process_cluster(current_cluster, current_price))
            
            clean_levels = ImpactZoneAnalyzer.consolidate_zones(levels, current_price)
            if len(clean_levels) >= 2:
                found_levels = clean_levels
                break
                
        # Fallback
        if not found_levels:
            found_levels.append({'price': np.max(highs), 'type': 'Resistance', 'strength': 10})
            found_levels.append({'price': np.min(lows), 'type': 'Support', 'strength': 10})

        # 3. IMPACT ZONE FILTER (+/- 20% by default)
        zone_levels = []
        limit = 0.20 
        upper = current_price * (1 + limit)
        lower = current_price * (1 - limit)
        
        for lvl in found_levels:
            if lower <= lvl['price'] <= upper:
                zone_levels.append(lvl)
                
        return zone_levels

# ================================================= FOR FINDING RSI STOCK (GFS & ADVANCE GFS)
class TechnicalAnalysis:
    
    @staticmethod
    def calculate_rsi(series, period=14):
        """Calculates RSI manually using Pandas"""
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).fillna(0)
        loss = (-delta.where(delta < 0, 0)).fillna(0)

        avg_gain = gain.ewm(com=period-1, min_periods=period).mean()
        avg_loss = loss.ewm(com=period-1, min_periods=period).mean()

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    @staticmethod
    def resample_data(df, timeframe='W'):
        """
        Converts Daily Data -> Weekly ('W') or Monthly ('ME')
        """
        # Ensure timestamp is the index
        df = df.copy()
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        
        # Resample logic (OHLCV)
        agg_dict = {
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }
        
        resampled_df = df.resample(timeframe).agg(agg_dict)
        # Drop incomplete candles (optional)
        return resampled_df.dropna()
    
    @staticmethod
    def calculate_sma(series, window=20):
        """Calculates Simple Moving Average"""
        return series.rolling(window=window).mean()

    @staticmethod
    def calculate_gap_percent(current_price, sma_value): #FOR FINDING SMA PEREENT GAP WITH CURRENT PRICE 
        """
        Calculates how far the price is from the SMA in %.
        Positive = Price is ABOVE SMA
        Negative = Price is BELOW SMA
        """
        if sma_value == 0 or pd.isna(sma_value): return 0.0
        gap = ((current_price - sma_value) / sma_value) * 100
        return round(gap, 2)