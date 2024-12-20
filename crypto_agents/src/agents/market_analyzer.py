# src/agents/market_analyzer.py
# Version: 2.0
# Date: 2024-12-17
# Description: Market analysis implementation with enhanced error handling and logging

import logging
from langgraph.graph import Graph, END
from typing import TypedDict, Annotated, Sequence
import json
from src.utils.llm import get_llm
from src.data.crypto_data import get_crypto_price_history, calculate_metrics
from langchain_core.prompts import ChatPromptTemplate

# Configure logging
logger = logging.getLogger(__name__)

class AgentState(TypedDict):
    """Type definition for the agent's state"""
    messages: Sequence[str]
    current_crypto: str
    price_data: dict
    analysis: str

def analyze_market(state: AgentState) -> AgentState:
    """Node for analyzing market data with improved error handling"""
    logger.info("Starting market analysis")
    llm = get_llm()
    
    template = """Analyze the following cryptocurrency data and provide insights:
    Cryptocurrency: {crypto}
    Price Metrics: {metrics}
    
    Provide a brief market analysis focusing on:
    1. Current market conditions
    2. Notable price movements
    3. Volume analysis (if available)
    4. Key recommendations
    
    Keep the analysis concise and data-driven."""
    
    prompt = ChatPromptTemplate.from_template(template)
    
    try:
        # Get price data and metrics
        price_data = get_crypto_price_history(state['current_crypto'])
        if price_data is None:
            logger.error("Failed to fetch cryptocurrency data")
            return {**state, 'analysis': "Error: Unable to fetch cryptocurrency data."}
            
        metrics = calculate_metrics(price_data)
        if metrics is None:
            logger.error("Failed to calculate market metrics")
            return {**state, 'analysis': "Error: Unable to calculate market metrics."}
            
        # Generate analysis
        logger.info("Generating market analysis")
        chain = prompt | llm
        analysis = chain.invoke({
            "crypto": state['current_crypto'],
            "metrics": json.dumps(metrics, indent=2)
        })
        
        logger.info("Analysis completed successfully")
        return {**state, 'analysis': analysis}
    except Exception as e:
        logger.error(f"Error in market analysis: {e}", exc_info=True)
        return {**state, 'analysis': f"Error analyzing market data: {str(e)}"}

def create_market_analysis_chain():
    """Create the LangGraph chain for market analysis"""
    logger.info("Creating market analysis chain")
    
    # Create graph
    workflow = Graph()
    
    workflow.add_node("market_analysis", analyze_market)
    
    workflow.set_entry_point("market_analysis")
    workflow.add_edge('market_analysis', END)
    
    logger.info("Market analysis chain created successfully")
    return workflow.compile()

# Ensure these are available for import
__all__ = ['AgentState', 'create_market_analysis_chain']