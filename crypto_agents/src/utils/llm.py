# src/utils/llm.py
#from langchain_ollama import Ollama
from langchain_community.llms import Ollama

def get_llm():
    """Initialize Ollama LLM with tinyllama model"""
    return Ollama(model="tinyllama", temperature=0.1)