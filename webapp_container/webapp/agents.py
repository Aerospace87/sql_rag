import asyncio
from tools import add_two_numbers_tools
from llama_index.core.agent.workflow import AgentWorkflow, AgentStream, ToolCallResult
from models import chat_llm

# Create Alfred, our gala agent, with the guest info tool
alfred = AgentWorkflow.from_tools_or_functions(
    [add_two_numbers_tools],
    llm=chat_llm
)

async def debug_agent(handler):
    """Function to debug the 'reasoning' of the agent"""
    async for ev in handler.stream_events():
        if isinstance(ev, ToolCallResult):
            print("")
            print("Called tool: ", ev.tool_name, ev.tool_kwargs, "=>", ev.tool_output)
        elif isinstance(ev, AgentStream):
            print(f"{ev.delta}", end="", flush=True)

if __name__ == "__main__":
    llm.complete("Hello how are you?")
