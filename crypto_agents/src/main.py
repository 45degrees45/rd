
# src/main.py
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main function to run the crypto analysis system"""
    logger.info("Starting crypto analysis system")
    
    # Initialize the analysis chain
    chain = create_market_analysis_chain()
    
    # Initial state
    initial_state = AgentState(
        messages=[],
        current_crypto="BTC-USD",
        price_data={},
        analysis=""
    )
    
    try:
        # Run analysis
        logger.info("Running market analysis")
        result = chain.invoke(initial_state)
        
        print("\nCrypto Market Analysis:")
        print("-" * 50)
        print(result['analysis'])
        logger.info("Analysis completed and results displayed")
    except Exception as e:
        logger.error(f"Error running analysis: {e}")
        print(f"Error running analysis: {e}")

if __name__ == "__main__":
    main()