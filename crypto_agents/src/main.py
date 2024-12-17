# src/main.py
from src.agents.market_analyzer import create_market_analysis_chain, AgentState

def main():
    """Main function to run the crypto analysis system"""
    print("Starting crypto analysis...")
    
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
        result = chain.invoke(initial_state)
        
        print("\nCrypto Market Analysis:")
        print("-" * 50)
        print(result['analysis'])
    except Exception as e:
        print(f"Error running analysis: {e}")

if __name__ == "__main__":
    main()