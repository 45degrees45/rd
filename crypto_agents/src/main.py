# src/main.py
# Version: 2.0
# Date: 2024-12-17
# Description: Main entry point for crypto analysis system with enhanced logging

import logging
from src.agents.market_analyzer import create_market_analysis_chain, AgentState

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main function to run the crypto analysis system"""
    logger.info("Starting crypto analysis system")
    
    try:
        # Initialize the analysis chain
        logger.debug("Creating market analysis chain")
        chain = create_market_analysis_chain()
        
        # Initial state
        logger.debug("Setting up initial state")
        initial_state = AgentState(
            messages=[],
            current_crypto="BTC-USD",
            price_data={},
            analysis=""
        )
        
        # Run analysis
        logger.info("Running market analysis")
        result = chain.invoke(initial_state)
        
        print("\nCrypto Market Analysis:")
        print("-" * 50)
        print(result['analysis'])
        logger.info("Analysis completed and results displayed")
        
    except Exception as e:
        logger.error(f"Error running analysis: {str(e)}", exc_info=True)
        print(f"Error running analysis: {str(e)}")

if __name__ == "__main__":
    main()