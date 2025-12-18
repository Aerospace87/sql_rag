from llama_index.core.workflow import Context
from agents import alfred, ToolCallResult, AgentStream, asyncio, debug_agent
from retriever import get_sql_data
import sys

debug = True
context = True

async def main():

    # Creation of the SQL-RAG prompt
    query = "Identify the most expensive article"
    prompt = get_sql_data(query, top_n=2)

    if context:
        # Creation of the context necessary to give "memory" to the agent
        ctx = Context(alfred)

        # Handler to await later
        handler = alfred.run(prompt, ctx = ctx)
    else:
        # Handler to await later
        handler = alfred.run(prompt)

    if debug:
        await debug_agent(handler)
    else:
        try:
            response = await handler

            print("🎩 Alfred's Response:")
            print(response)

        except Exception as e:
            sys.exit(f"The following exception occurred:\n{str(e)}")


if __name__ == "__main__":
    asyncio.run(main())