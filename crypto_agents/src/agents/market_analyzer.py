# src/agents/market_analyzer.py
from langgraph.graph import Graph, END
from typing import TypedDict, Annotated, Sequence
import json
from src.utils.llm import get_llm
from src.data.crypto_data import get_crypto_price_history, calculate_metrics
from langchain_core.prompts import ChatPromptTemplate

class AgentState(TypedDict):
    messages: Sequence[str]
    current_crypto: str
    price_data: dict
    analysis: str

def create_market_analysis_chain():
    """Create the LangGraph chain for market analysis"""
    
    def analyze_market(state: AgentState) -> AgentState:
        """Node for analyzing market data"""
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
        
        # Get price data and metrics
        price_data = get_crypto_price_history(state['current_crypto'])
        metrics = calculate_metrics(price_data)
        
        if metrics is None:
            state['analysis'] = "Error: Unable to fetch or analyze cryptocurrency data."
            return state
            
        # Generate analysis
        chain = prompt | llm
        analysis = chain.invoke({
            "crypto": state['current_crypto'],
            "metrics": json.dumps(metrics, indent=2)
        })
        
        state['analysis'] = analysis
        return state

    # Create graph
    workflow = Graph()
    
    workflow.add_node("market_analysis", analyze_market)
    
    workflow.set_entry_point("market_analysis")
    workflow.add_edge('market_analysis', END)
    
    return workflow.compile()