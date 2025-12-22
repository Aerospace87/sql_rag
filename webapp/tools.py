from llama_index.core.tools import FunctionTool
from llama_index.retrievers.bm25 import BM25Retriever
from retriever import load_guest_dataset
from ddgs import DDGS

# Loading the dataset
docs = load_guest_dataset()

def get_guest_info_retriever(query: str) -> str:
    """Retrieves detailed information about gala guests based on their name or relation."""

    bm25_retriever = BM25Retriever.from_defaults(nodes=docs)
    results = bm25_retriever.retrieve(query)

    if results:
        return "\n\n".join([doc.text for doc in results[:3]])
    else:
        return "No matching guest information found."

# Initialize the tool
guest_info_tool = FunctionTool.from_defaults(
    get_guest_info_retriever,
    name = "guest_info_tool",
    description = "Retrieves detailed information about gala guests based on their name or relation."
)


def add_two_numbers(x: int, y: int) -> int :
    """Function that returns the sum of two numbers x and y"""
    return x + y

add_two_numbers_tools = FunctionTool.from_defaults(
    add_two_numbers
)


# This because the DuckDuckGoSearchToolSpec of Lllamaindex gives an error
# of max number of requests even if only one request is send
web_search_tool = FunctionTool.from_defaults(
    DDGS().text,
    name = "web_search_tool",
    description="Function that search information in the web"
)

if __name__ == '__main__':
    print('Unit Test of guest_info_tool')
    print(guest_info_tool.call("Lady Ada Lovelace"))

    print('Unit test of web_search_tool')
    print(web_search_tool.call("Who is the current president of USA?"))