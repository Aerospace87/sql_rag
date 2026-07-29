from llama_index.core.tools import FunctionTool
from llama_index.retrievers.bm25 import BM25Retriever
from ddgs import DDGS

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
