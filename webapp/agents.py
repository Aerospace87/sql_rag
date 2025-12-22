import os
import asyncio
from llama_index.llms.huggingface_api import HuggingFaceInferenceAPI
from tools import guest_info_tool, add_two_numbers_tools, web_search_tool
from llama_index.core.agent.workflow import AgentWorkflow, AgentStream, ToolCallResult

# get HF token
token = os.getenv('HF_TOKEN')

# Initialize the Hugging Face model
llm = HuggingFaceInferenceAPI(
    model_name="Qwen/Qwen2.5-Coder-32B-Instruct",
    token=token,
    temperature=1e-03,
    max_tokens=50,
    provider = "auto"
)

# Create Alfred, our gala agent, with the guest info tool
alfred = AgentWorkflow.from_tools_or_functions(
    [guest_info_tool, web_search_tool],
    llm=llm
)

async def debug_agent(handler):
    """Function to debug the 'reasoning' of the agent"""
    async for ev in handler.stream_events():
        if isinstance(ev, ToolCallResult):
            print("")
            print("Called tool: ", ev.tool_name, ev.tool_kwargs, "=>", ev.tool_output)
        elif isinstance(ev, AgentStream):
            print(f"{ev.delta}", end="", flush=True)