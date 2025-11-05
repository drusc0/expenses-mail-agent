from smolagents import (
    ToolCallingAgent,
    ToolCollection,
    LiteLLMModel,
)
from mcp import StdioServerParameters


model = LiteLLMModel(
    model_id="ollama/llama2",
    num_ctx=8192,
)
server_parameters = StdioServerParameters(
    command="uv",
    args=["run", "main.py"],
    env=None,
)

with ToolCollection.from_mcp(server_parameters=server_parameters, trust_remote_code=True) as tool_collection:
    agent = ToolCallingAgent(tools=[*tool_collection.tools], model=model)
    agent.run("What is the stock price of WDAY?", verbose=True, iterations=1)
