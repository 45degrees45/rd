rom openbb import obb
import pandas as pd

def get_crypto_price_history(symbol: str):
    """Fetch cryptocurrency price history using OpenBB"""
    try:
        # Get the data and convert to DataFrame
        response = obb.crypto.price.historical(symbol=symbol)
        
        if hasattr(response, 'results'):
            # Convert list of data objects to DataFrame
            df = pd.DataFrame([
                {
                    'date': data.date,
                    'open': data.open,
                    'high': data.high,
                    'low': data.low,
                    'close': data.close,
                    'volume': data.volume
                }
                for data in response.results
            ])
            return df
            
        return None
    except Exception as e:
        print(f"Error fetching price data: {e}")
        return None

def calculate_metrics(price_data):
    """Calculate basic technical indicators"""
    if price_data is None or price_data.empty:
        return None
    
    try:
        metrics = {}
        
        # Basic price metrics
        metrics['current_price'] = float(price_data['close'].iloc[-1])
        metrics['price_change_24h'] = float(
            (price_data['close'].iloc[-1] - price_data['close'].iloc[-2])
            / price_data['close'].iloc[-2] * 100
        )
        
        # Add volume metrics
        metrics['volume_24h'] = float(price_data['volume'].iloc[-1])
        
        # Add some additional technical metrics
        metrics['7d_high'] = float(price_data['high'].tail(7).max())
        metrics['7d_low'] = float(price_data['low'].tail(7).min())
        metrics['7d_avg_volume'] = float(price_data['volume'].tail(7).mean())
        
        return metrics
    except Exception as e:
        print(f"Error calculating metrics: {e}")
        return None