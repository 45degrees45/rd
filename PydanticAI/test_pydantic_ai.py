from pydantic_ai.agent import Agent
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from typing import Dict, Any

# Load environment variables
load_dotenv()

# Ensure we have API key
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("Please set OPENAI_API_KEY in your .env file")

class WeatherResponse(BaseModel):
    temperature: float
    conditions: str
    recommendation: str

# Create the system prompt for the agent
SYSTEM_PROMPT = """You are a weather information agent. When asked about weather, provide a response
that includes temperature, current conditions, and a recommendation for activities."""

# Specify the model in the Agent constructor
agent = Agent[Dict[str, Any], WeatherResponse](
    system_prompt=SYSTEM_PROMPT,
    model="gpt-3.5-turbo"  # or "gpt-4" if you prefer
)

async def get_weather():
    response = await agent.run(
        "What's the weather like in Paris today? Give me a fake response for testing."
    )
    return response

if __name__ == "__main__":
    import asyncio
    weather = asyncio.run(get_weather())
    print(weather)