# src/data/crypto_data.py
import logging
from openbb import obb
import pandas as pd

# Configure logging
logger = logging.getLogger(__name__)

def get_crypto_price_history(symbol: str):
    """Fetch cryptocurrency price history using OpenBB"""
    logger.info(f"Fetching price history for {symbol}")
    try:
        # Get the data and convert to DataFrame
        response = obb.crypto.price.historical(symbol=symbol)
        logger.debug(f"OpenBB Response type: {type(response)}")
        
        if hasattr(response, 'results'):
            logger.debug("Processing OpenBB results")
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
            logger.info(f"Successfully created DataFrame with {len(df)} rows")
            return df
            
        logger.error("Response does not contain expected results attribute")
        return None
    except Exception as e:
        logger.error(f"Error fetching price data: {e}")
        return None

def calculate_metrics(price_data):
    """Calculate basic technical indicators"""
    logger.info("Calculating market metrics")
    
    if price_data is None or price_data.empty:
        logger.error("No price data available for metric calculation")
        return None
    
    try:
        metrics = {}
        
        # Basic price metrics
        metrics['current_price'] = float(price_data['close'].iloc[-1])
        metrics['price_change_24h'] = float(
            (price_data['close'].iloc[-1] - price_data['close'].iloc[-2])
            / price_data['close'].iloc[-2] * 100
        )
        
        # Volume metrics
        metrics['volume_24h'] = float(price_data['volume'].iloc[-1])
        
        # Technical metrics
        metrics['7d_high'] = float(price_data['high'].tail(7).max())
        metrics['7d_low'] = float(price_data['low'].tail(7).min())
        metrics['7d_avg_volume'] = float(price_data['volume'].tail(7).mean())
        
        logger.info("Successfully calculated all metrics")
        return metrics
    except Exception as e:
        logger.error(f"Error calculating metrics: {e}")
        return None