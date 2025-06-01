### Available parameters to alter

#### tavily_search
- `query`: The search query string (max 400 characters)
- `search_depth`: 'basic' or 'advanced'
- `include_domains`: List of domains to include in search results
- `exclude_domains`: List of domains to exclude from search results
- `max_results`: Maximum number of search results to return
- `chunks_per_source`: Number of content chunks to return per source (advanced search)
- `include_raw_content`: Whether to include raw content in results
- `time_range`: Time range for results (e.g., 'day', 'week', 'month')
- `topic`: Filter for specific topics (e.g., 'news')
- `days`: Number of days back for news results
- `min_score`: Minimum relevance score for filtering results

#### tavily_extract
- `urls`: List of URLs to extract content from
- `extract_depth`: 'basic' or 'advanced'

#### tavily_crawl
- `start_url`: The URL to start crawling from
- `instructions`: Optional instructions for the crawl
- `max_pages`: Maximum number of pages to crawl
- `max_depth`: Maximum depth level for crawling
- `max_breadth`: Maximum number of links to follow at each level
- `extract_depth`: 'basic' or 'advanced'
- `select_paths`: List of regex patterns for paths to include
- `exclude_paths`: List of regex patterns for paths to exclude
- `select_domains`: List of regex patterns for domains to include
- `exclude_domains`: List of regex patterns for domains to exclude
- `categories`: List of content categories to focus on
- `include_images`: Whether to include images in the extraction

#### tavily_api_examples_flow
- All parameters from `tavily_search`, `tavily_extract`, and `tavily_crawl` can be altered via the flow's arguments.
       

```python
from prefect import task, flow
import os
import re
from typing import Dict, Any, Optional, List, Union
from tavily import TavilyClient
import asyncio

@task(name="tavily_search_task")
def tavily_search(
    query: str, 
    api_key: Optional[str] = None,
    search_depth: str = "basic",
    include_domains: Optional[List[str]] = None,
    exclude_domains: Optional[List[str]] = None,
    max_results: int = 10,
    chunks_per_source: Optional[int] = None,
    include_raw_content: bool = False,
    time_range: Optional[str] = None,
    topic: Optional[str] = None,
    days: Optional[int] = None,
    min_score: Optional[float] = None
) -> Dict[str, Any]:
    """
    Search the web using Tavily's API.
    
    Args:
        query: The search query string (max 400 characters)
        api_key: Tavily API key (defaults to TAVILY_API_KEY environment variable)
        search_depth: 'basic' or 'advanced' search depth
        include_domains: List of domains to include in search results
        exclude_domains: List of domains to exclude from search results
        max_results: Maximum number of search results to return
        chunks_per_source: Number of content chunks to return per source (used with advanced search)
        include_raw_content: Whether to include raw content in results
        time_range: Time range for results (e.g., 'day', 'week', 'month')
        topic: Filter for specific topics (e.g., 'news')
        days: Number of days back for news results
        min_score: Minimum relevance score for filtering results
        
    Returns:
        Dict containing search results
    """
    try:
        # Validate query length
        if len(query) > 400:
            raise ValueError("Query is too long. Max query length is 400 characters.")
            
        # Validate search_depth
        if search_depth not in ["basic", "advanced"]:
            raise ValueError("search_depth must be either 'basic' or 'advanced'")
        
        # Get API key from parameters or environment
        api_key = api_key or os.environ.get("TAVILY_API_KEY")
        if not api_key:
            raise ValueError("Tavily API key is required. Provide it as a parameter or set TAVILY_API_KEY environment variable.")
            
        # Initialize client
        client = TavilyClient(api_key=api_key)
        
        params = {
            "query": query,
            "search_depth": search_depth,
            "max_results": max_results
        }
        optional_params = {
            "include_domains": include_domains,
            "exclude_domains": exclude_domains,
            "include_raw_content": include_raw_content,
            "time_range": time_range,
            "topic": topic,
            "chunks_per_source": chunks_per_source if search_depth == "advanced" else None,
            "days": days if topic == "news" else None
        }
        params.update({k: v for k, v in optional_params.items() if v is not None})
        
            
        # Execute search with parameters
        response = client.search(**params)
        
        # Apply post-processing if needed
        if min_score is not None and "results" in response:
            response["results"] = [r for r in response["results"] if r.get("score", 0) >= min_score]
            
        return response
        
    except Exception as e:
        print(f"Error searching with Tavily: {str(e)}")
        raise

# Sample Output for tavily_search
# {
#   'query': 'latest advances in artificial intelligence',
#   'follow_up_questions': None,
#   'answer': None,
#   'images': [],
#   'results': [
#     {
#       'title': "Year in review: Google's biggest AI advancements of 2024",
#       'url': 'https://blog.google/technology/ai/2024-ai-extraordinary-progress-advancement/',
#       'content': '...',
#       'score': 0.71948266,
#       'raw_content': None
#     },
#     ...
#   ],
#   'response_time': 1.67
# }

@task(name="tavily_extract_task")
def tavily_extract(urls: List[str], api_key: Optional[str] = None, extract_depth: str = "advanced") -> Dict[str, Any]:
    """
    Extract content from a URL using Tavily's API.
    
    Args:
        url: The URL to extract content from
        api_key: Tavily API key (defaults to TAVILY_API_KEY environment variable)
        extract_depth: Level of extraction depth ("basic" or "advanced")
        
    Returns:
        Dict containing extracted content
    """
    try:
        # Get API key from parameters or environment
        api_key = api_key or os.environ.get("TAVILY_API_KEY")
        if not api_key:
            raise ValueError("Tavily API key is required. Provide it as a parameter or set TAVILY_API_KEY environment variable.")
            
        # Initialize client
        client = TavilyClient(api_key=api_key)
        
        # Execute extraction with advanced depth by default
        response = client.extract(urls=urls, extract_depth=extract_depth)
        
        return response
    except Exception as e:
        print(f"Error extracting content with Tavily: {str(e)}")
        raise

# Sample Output for tavily_extract
# {
#   'results': [
#     {
#       'url': 'https://www.anthropic.com/',
#       'raw_content': '...',
#       'images': []
#     }
#   ],
#   'failed_results': [],
#   'response_time': 0.01
# }

@task(name="tavily_crawl_task")
def tavily_crawl(
    start_url: str,
    api_key: Optional[str] = None,
    instructions: Optional[str] = None,
    max_pages: int = 10,
    max_depth: int = 1,
    max_breadth: Optional[int] = None,
    extract_depth: str = "basic",
    select_paths: Optional[List[str]] = None,
    exclude_paths: Optional[List[str]] = None,
    select_domains: Optional[List[str]] = None,
    exclude_domains: Optional[List[str]] = None,
    categories: Optional[List[str]] = None,
    include_images: bool = False
) -> Dict[str, Any]:
    """
    Crawl a website starting from a URL using Tavily's API.
    Note: This feature is in invite-only beta.
    
    Args:
        start_url: The URL to start crawling from
        api_key: Tavily API key (defaults to TAVILY_API_KEY environment variable)
        instructions: Optional instructions for the crawl (e.g., "Find all pages on the Python SDK")
        max_pages: Maximum number of pages to crawl (limit)
        max_depth: Maximum depth level for crawling (default: 1, increase carefully)
        max_breadth: Maximum number of links to follow at each level
        extract_depth: Level of content extraction ("basic" or "advanced")
        select_paths: List of regex patterns for paths to include
        exclude_paths: List of regex patterns for paths to exclude
        select_domains: List of regex patterns for domains to include
        exclude_domains: List of regex patterns for domains to exclude
        categories: List of content categories to focus on
        include_images: Whether to include images in the extraction
        
    Returns:
        Dict containing crawl results
    """
    try:
        # Get API key from parameters or environment
        api_key = api_key or os.environ.get("TAVILY_API_KEY")
        if not api_key:
            raise ValueError("Tavily API key is required. Provide it as a parameter or set TAVILY_API_KEY environment variable.")
            
        # Initialize client
        client = TavilyClient(api_key=api_key)
        
        # Build crawl parameters
        crawl_params = {
            "url": start_url,
            "limit": max_pages,
            "max_depth": max_depth,
            "extract_depth": extract_depth
        }
        
        # Add optional parameters if provided
        optional_params = {
            "instructions": instructions,
            "max_breadth": max_breadth,
            "select_paths": select_paths,
            "exclude_paths": exclude_paths, 
            "select_domains": select_domains,
            "exclude_domains": exclude_domains,
            "categories": categories,
            "include_images": include_images
        }

        # Filter out None values and update crawl_params
        crawl_params.update({k: v for k, v in optional_params.items() if v is not None})
        
        response = client.crawl(**crawl_params)
        return response
    except Exception as e:
        print(f"Error crawling with Tavily: {str(e)}")
        raise

# Sample Output for tavily_crawl
# {
#   'base_url': 'https://www.anthropic.com/',
#   'results': [
#     {
#       'url': 'https://www.anthropic.com/claude',
#       'raw_content': '...',
#       'images': []
#     },
#     ...
#   ],
#   'response_time': 7.1
# }

@flow(name="tavily_api_examples_flow")
def tavily_api_examples(
    api_key: str = None,
    # Search params
    search_query: str = "latest advances in artificial intelligence",
    search_depth: str = "basic",
    include_domains: Optional[List[str]] = None,
    exclude_domains: Optional[List[str]] = None,
    max_results: int = 5,
    chunks_per_source: Optional[int] = None,
    include_raw_content: bool = False,
    time_range: Optional[str] = None,
    topic: Optional[str] = None,
    days: Optional[int] = None,
    min_score: Optional[float] = None,
    # Extract params
    extract_urls: Union[str, List[str]] = "https://www.anthropic.com/",
    extract_depth: str = "basic",
    # Crawl params
    crawl_start_url: str = "https://www.anthropic.com/",
    crawl_instructions: Optional[str] = "Find information about Claude AI",
    crawl_max_pages: int = 3,
    crawl_max_depth: int = 1,
    crawl_max_breadth: Optional[int] = None,
    crawl_extract_depth: str = "basic",
    crawl_select_paths: Optional[List[str]] = None,
    crawl_exclude_paths: Optional[List[str]] = None,
    crawl_select_domains: Optional[List[str]] = None,
    crawl_exclude_domains: Optional[List[str]] = None,
    crawl_categories: Optional[List[str]] = None,
    crawl_include_images: bool = False
) -> Dict[str, Any]:
    api_key = api_key or os.environ.get("TAVILY_API_KEY")
    results = {}

    # Example 1: Basic web search

    search_results = tavily_search(
        query=search_query,
        api_key=api_key,
        search_depth=search_depth,
        include_domains=include_domains,
        exclude_domains=exclude_domains,
        max_results=max_results,
        chunks_per_source=chunks_per_source,
        include_raw_content=include_raw_content,
        time_range=time_range,
        topic=topic,
        days=days,
        min_score=min_score
    )
    results["search"] = search_results

    print("Search Results:", search_results)

    # Example 2: Extract content from a URL

    extract_results = tavily_extract(
        urls=extract_urls,
        api_key=api_key,
        extract_depth=extract_depth
    )
    results["extract"] = extract_results
  
    print(f"Extracted content from {extract_urls} : {extract_results}")

    # Example 3: Crawl a website

    crawl_results = tavily_crawl(
        start_url=crawl_start_url,
        api_key=api_key,
        instructions=crawl_instructions,
        max_pages=crawl_max_pages,
        max_depth=crawl_max_depth,
        max_breadth=crawl_max_breadth,
        extract_depth=crawl_extract_depth,
        select_paths=crawl_select_paths,
        exclude_paths=crawl_exclude_paths,
        select_domains=crawl_select_domains,
        exclude_domains=crawl_exclude_domains,
        categories=crawl_categories,
        include_images=crawl_include_images
    )
    results["crawl"] = crawl_results

    print(f"Crawled results: {crawl_results}")

    return results

if __name__ == "__main__":
    # Call the example function
    results = tavily_api_examples()
       
```

#Serper (Google Search API)

### Available parameters to alter
#### serper_google_search

- `serper_api_key`: API key for the Serper Google Search API (optional if set as environment variable)
- `aiosession`: Optional aiohttp ClientSession for async requests
- `gl`: Country code for the search (e.g., 'us' for United States)
- `hl`: Language code for the search (e.g., 'en' for English)
- `k`: Number of search results to return
- `result_key_for_type`: Mapping of search type to result key
- `serper_api_url`: Custom API URL for Serper requests

``` python 


from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_groq import ChatGroq
from langchain.agents import initialize_agent, Tool
from langchain.agents import AgentType
import os
from typing import Optional, Dict, Any
from aiohttp import ClientSession
import asyncio

def initialize_serper_tool(
    serper_api_key: Optional[str] = None,
    aiosession: Optional[ClientSession] = None,
    gl: Optional[str] = None,
    hl: Optional[str] = None,
    k: Optional[int] = None,
    result_key_for_type: Optional[Dict[str, str]] = None,
    serper_api_url: Optional[str] = None
) -> Tool:
    """
    Initialize the Google Serper search tool with parameters from the documentation.
    
    Args:
        serper_api_key: API key for the Serper Google Search API (optional if set as env var)
        aiosession: Optional aiohttp ClientSession
        gl: Optional country code for the search
        hl: Optional language code for the search
        k: Optional number of search results to return
        result_key_for_type: Optional mapping of search type to result key
        serper_api_url: Optional custom API URL
    
    Returns:
        Tool object configured for Google Serper search
    """
    # Set the API key in the environment if provided
    if serper_api_key:
        os.environ["SERPER_API_KEY"] = serper_api_key
    
    # Prepare kwargs with only non-None values
    kwargs = {k: v for k, v in {'serper_api_key': serper_api_key, 'aiosession': aiosession, 'gl': gl, 'hl': hl, 'k': k, 'result_key_for_type': result_key_for_type, 'serper_api_url': serper_api_url}.items() if v is not None}
    
    # Initialize the Google Serper wrapper with only provided parameters
    search = GoogleSerperAPIWrapper(**kwargs)
    
    # Create a tool from the wrapper
    serper_tool = Tool(
        name="Search",
        func=search.run,
        description="Useful for when you need to search for information on the web. Input should be a search query."
    )
    
    print("Google Serper Search tool initialized successfully.")
    
    return serper_tool

def demonstrate_serper_capabilities(
    user_question: str,
    llm_api_key: str,
    serper_api_key: Optional[str] = None,
    llm_model_name: str = "llama-3.3-70b-versatile",
    verbose: bool = True,
    gl: Optional[str] = None,
    hl: Optional[str] = None,
    k: Optional[int] = None,
    result_key_for_type: Optional[Dict[str, str]] = None,
    serper_api_url: Optional[str] = None
) -> str:
    """
    Demonstrates the capabilities of the Google Serper API integration with LangChain.
    
    Args:
        user_question: The question to ask that requires web search
        llm_api_key: API key for Groq
        serper_api_key: API key for the Serper Google Search API (optional if set as env var)
        llm_model_name: Model name for Groq (default: "llama-3.3-70b-versatile")
        verbose: Whether to print detailed agent reasoning
        gl: Optional country code for the search
        hl: Optional language code for the search
        k: Optional number of search results to return
        result_key_for_type: Optional mapping of search type to result key
        serper_api_url: Optional custom API URL
    
    Returns:
        The final answer from the agent
    """
    
    # Initialize the serper tool with documented parameters
    serper_tool = initialize_serper_tool(
        serper_api_key=serper_api_key,
        gl=gl,
        hl=hl,
        k=k,
        result_key_for_type=result_key_for_type,
        serper_api_url=serper_api_url
    )
    
    # Initialize the language model
    llm = ChatGroq(temperature=0, 
                   groq_api_key=llm_api_key, 
                   model_name=llm_model_name)
    
    # Create an agent with the tool - using ZERO_SHOT_REACT_DESCRIPTION
    agent = initialize_agent(
        [serper_tool], 
        llm, 
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=verbose,
        handle_parsing_errors=True
    )
    
    # Run the agent with the user's question
    try:
        result = agent.run(user_question)
        print(f"Final answer: {result}")
        return result
    except Exception as e:
        print(f"An error occurred: {e}")
        return str(e)

# Asynchronous version

async def initialize_serper_tool_async(
    serper_api_key: Optional[str] = None,
    aiosession: Optional[ClientSession] = None,
    gl: Optional[str] = None,
    hl: Optional[str] = None,
    k: Optional[int] = None,
    result_key_for_type: Optional[Dict[str, str]] = None,
    serper_api_url: Optional[str] = None
) -> Tool:
    """
    Initialize the Google Serper search tool asynchronously with documented parameters.
    
    Args:
        serper_api_key: API key for the Serper Google Search API (optional if set as env var)
        aiosession: Optional aiohttp ClientSession
        gl: Optional country code for the search
        hl: Optional language code for the search
        k: Optional number of search results to return
        result_key_for_type: Optional mapping of search type to result key
        serper_api_url: Optional custom API URL
    
    Returns:
        Tool object configured for Google Serper search
    """
    # Set the API key in the environment if provided
    if serper_api_key:
        os.environ["SERPER_API_KEY"] = serper_api_key
    
    kwargs = {k: v for k, v in {'serper_api_key': serper_api_key, 'aiosession': aiosession, 'gl': gl, 'hl': hl, 'k': k, 'result_key_for_type': result_key_for_type, 'serper_api_url': serper_api_url}.items() if v is not None}
    
    # Initialize the Google Serper wrapper with only provided parameters
    search = GoogleSerperAPIWrapper(**kwargs)
    
    # Create a tool from the wrapper using the async version
    serper_tool = Tool(
        name="Search",
        func=search.arun,  # Use the async run method
        description="Useful for when you need to search for information on the web. Input should be a search query.",
        coroutine=search.arun  # Specify the coroutine
    )
    
    print("Google Serper Search tool initialized successfully (async).")
    
    return serper_tool

async def demonstrate_serper_capabilities_async(
    user_question: str,
    llm_api_key: str,
    serper_api_key: Optional[str] = None,
    llm_model_name: str = "llama-3.3-70b-versatile",
    verbose: bool = True,
    gl: Optional[str] = None,
    hl: Optional[str] = None,
    k: Optional[int] = None,
    result_key_for_type: Optional[Dict[str, str]] = None,
    serper_api_url: Optional[str] = None
) -> str:
    """
    Demonstrates the capabilities of the Google Serper API integration with LangChain asynchronously.
    
    Args:
        user_question: The question to ask that requires web search
        llm_api_key: API key for Groq
        serper_api_key: API key for the Serper Google Search API (optional if set as env var)
        llm_model_name: Model name for Groq (default: "llama-3.3-70b-versatile")
        verbose: Whether to print detailed agent reasoning
        gl: Optional country code for the search
        hl: Optional language code for the search
        k: Optional number of search results to return
        result_key_for_type: Optional mapping of search type to result key
        serper_api_url: Optional custom API URL
    
    Returns:
        The final answer from the agent
    """
    # Create an aiohttp session for reuse
    async with ClientSession() as session:
        # Initialize the serper tool with documented parameters
        serper_tool = await initialize_serper_tool_async(
            serper_api_key=serper_api_key,
            aiosession=session,
            gl=gl,
            hl=hl,
            k=k,
            result_key_for_type=result_key_for_type,
            serper_api_url=serper_api_url
        )
        
        # Initialize the language model
        llm = ChatGroq(temperature=0, 
                      groq_api_key=llm_api_key, 
                      model_name=llm_model_name)
        
        # Create an agent with the tool
        agent = initialize_agent(
            [serper_tool], 
            llm, 
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=verbose,
            handle_parsing_errors=True
        )
        
        # Run the agent with the user's question
        try:
            # Use agent.arun for async execution
            result = await agent.arun(user_question)
            print(f"Final answer: {result}")
            return result
        except Exception as e:
            print(f"An error occurred: {e}")
            return str(e)

# Example usage
async def main():
    serper_api_key = "3b9bd5471301b85b5f42ac7c3a7b8e49e62a36b4"
    llm_api_key = "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"
    user_question = "Who is the current president of the United States?"
    
    # Run the async version
    result = await demonstrate_serper_capabilities_async(
        user_question=user_question,
        llm_api_key=llm_api_key,
        serper_api_key=serper_api_key
    )
    print(result)

# Run the async main function
if __name__ == "__main__":
    # For synchronous usage
    # result = demonstrate_serper_capabilities(
    #     user_question="What is the capital of France?",
    #     llm_api_key="YOUR_GROQ_API_KEY",
    #     serper_api_key="YOUR_SERPER_API_KEY"
    # )
    # print(result)
    
    # For asynchronous usage
    asyncio.run(main())

```

# Brave Search API

### Available parameters to alter

- `q`: The user's search query (max 400 chars, 50 words)
- `country`: 2-letter country code (default 'US')
- `search_lang`: Language for results (default 'en')
- `ui_lang`: UI language (e.g., 'en-US')
- `count`: # of results to return (max 20)
- `offset`: Page offset (zero-based)
- `safesearch`: 'off'|'moderate'|'strict'
- `freshness`: 'pd'|'pw'|'pm'|'py' or 'YYYY-MM-DDtoYYYY-MM-DD'
- `text_decorations`: Highlight markup in snippets
- `spellcheck`: Auto-spellcheck query
- `result_filter`: CSV of result types (e.g., 'news,videos')
- `goggles_id`: Deprecated single-ID goggles 
- `goggles`: List of goggles (URLs or definitions)
- `units`: 'metric' or 'imperial'
- `extra_snippets`: Return up to 5 extra excerpts
- `summary`: Enable summary key generation
- `api_key`: Brave API key (or set BRAVE_API_KEY env var)


``` python 
import os
import asyncio
from typing import Any, Dict, List, Optional
from brave import Brave, AsyncBrave
from prefect import task, flow


@task(name="Brave Search Sync Task")
def brave_search(
    q: str,
    *,
    country: str = "US",
    search_lang: str = "en",
    ui_lang: str = "en-US",
    count: int = 20,
    offset: int = 0,
    safesearch: str = "moderate",
    freshness: Optional[str] = None,
    text_decorations: bool = True,
    spellcheck: bool = True,
    result_filter: Optional[str] = None,
    goggles_id: Optional[str] = None,
    goggles: Optional[List[str]] = None,
    units: Optional[str] = None,
    extra_snippets: bool = False,
    summary: bool = False,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    if not q or len(q) > 400:
        raise ValueError("Query must be non-empty and at most 400 characters.")
    if len(q.split()) > 50:
        raise ValueError("Query must be at most 50 words.")

    api_key = api_key or os.environ.get("BRAVE_API_KEY")
    if not api_key:
        raise ValueError("Brave API key is required. Provide it or set BRAVE_API_KEY.")

    client = Brave(api_key=api_key)

    params: Dict[str, Any] = {
        "q": q,
        "country": country,
        "search_lang": search_lang,
        "ui_lang": ui_lang,
        "count": count,
        "offset": offset,
        "safesearch": safesearch,
        "freshness": freshness,
        "text_decorations": int(text_decorations),
        "spellcheck": int(spellcheck),
        "result_filter": result_filter,
        "goggles_id": goggles_id,
        "goggles": goggles,
        "units": units,
        "extra_snippets": int(extra_snippets),
        "summary": int(summary),
    }
    params = {k: v for k, v in params.items() if v is not None}

    return client.search(**params)


@task(name="Brave Search Async Task")
def brave_search_async(
    q: str,
    *,
    country: str = "US",
    search_lang: str = "en",
    ui_lang: str = "en-US",
    count: int = 20,
    offset: int = 0,
    safesearch: str = "moderate",
    freshness: Optional[str] = None,
    text_decorations: bool = True,
    spellcheck: bool = True,
    result_filter: Optional[str] = None,
    goggles_id: Optional[str] = None,
    goggles: Optional[List[str]] = None,
    units: Optional[str] = None,
    extra_snippets: bool = False,
    summary: bool = False,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    if not q or len(q) > 400:
        raise ValueError("Query must be non-empty and at most 400 characters.")
    if len(q.split()) > 50:
        raise ValueError("Query must be at most 50 words.")

    api_key = api_key or os.environ.get("BRAVE_API_KEY")
    if not api_key:
        raise ValueError("Brave API key is required. Provide it or set BRAVE_API_KEY.")

    client = AsyncBrave(api_key=api_key)

    params: Dict[str, Any] = {
        "q": q,
        "country": country,
        "search_lang": search_lang,
        "ui_lang": ui_lang,
        "count": count,
        "offset": offset,
        "safesearch": safesearch,
        "freshness": freshness,
        "text_decorations": int(text_decorations),
        "spellcheck": int(spellcheck),
        "result_filter": result_filter,
        "goggles_id": goggles_id,
        "goggles": goggles,
        "units": units,
        "extra_snippets": int(extra_snippets),
        "summary": int(summary),
    }
    params = {k: v for k, v in params.items() if v is not None}

    async def _run():
        return await client.search(**params)

    return asyncio.get_event_loop().run_until_complete(_run())


@flow(name="Brave Search Flow")
def brave_search_example():
    res = brave_search.submit(
        "openai",
        country="CA",
        count=10,
        safesearch="strict",
        extra_snippets=True
    )
    return res.result()


if __name__ == "__main__":
    brave_search_example()


```

# Perplexity API 
### Available parameters to alter
- `messages`: List of messages (required)
- `model`: Model to use (default 'sonar')
- `max_tokens`: Maximum number of tokens to generate
- `temperature`: Controls randomness (0-2)
- `top_p`: Controls diversity via nucleus sampling (0-1)
- `search_domain_filter`: List of domains to include in search
- `return_images`: Whether to return images
- `return_related_questions`: Whether to return related questions
- `search_recency_filter`: Time range for search results
- `top_k`: Number of results to return
- `stream`: Whether to stream responses
- `presence_penalty`: Penalty for new tokens based on presence in text (0-2)
- `frequency_penalty`: Penalty for new tokens based on frequency in text (0-2)
- `response_format`: Response format options
- `web_search_options`: Options for web search

```python
import os
import requests
import httpx
from typing import Any, Dict, List, Optional
from prefect import flow, task

# Default endpoints and credentials from environment
PERPLEXITY_API_URL = os.getenv(
    "PERPLEXITY_API_URL", "https://api.perplexity.ai/chat/completions"
)
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")


@task(name="perplexity_chat")
def perplexity_chat(
    messages: List[Dict[str, str]],
    model: str = "sonar",
    max_tokens: Optional[int] = None,
    temperature: float = 0.2,
    top_p: float = 0.9,
    search_domain_filter: Optional[List[str]] = None,
    return_images: bool = False,
    return_related_questions: bool = False,
    search_recency_filter: Optional[str] = None,
    top_k: int = 0,
    stream: bool = False,
    presence_penalty: float = 0.0,
    frequency_penalty: float = 1.0,
    response_format: Optional[Dict[str, Any]] = None,
    web_search_options: Optional[Dict[str, Any]] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Send a chat-completion request to the Perplexity API (synchronous).
    """
    if not PERPLEXITY_API_KEY:
        raise ValueError("PERPLEXITY_API_KEY environment variable not set.")

    payload: Dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "top_p": top_p,
        "return_images": return_images,
        "return_related_questions": return_related_questions,
        "top_k": top_k,
        "stream": stream,
        "presence_penalty": presence_penalty,
        "frequency_penalty": frequency_penalty,
    }
    if max_tokens is not None:
        payload["max_tokens"] = max_tokens
    if search_domain_filter:
        payload["search_domain_filter"] = search_domain_filter
    if search_recency_filter:
        payload["search_recency_filter"] = search_recency_filter
    if response_format:
        payload["response_format"] = response_format
    if web_search_options:
        payload["web_search_options"] = web_search_options
    payload.update(kwargs)

    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json",
    }

    resp = requests.post(PERPLEXITY_API_URL, json=payload, headers=headers)
    resp.raise_for_status()
    return resp.json()


@task(name="perplexity_chat_async")
async def perplexity_chat_async(
    messages: List[Dict[str, str]],
    model: str = "sonar",
    max_tokens: Optional[int] = None,
    temperature: float = 0.2,
    top_p: float = 0.9,
    search_domain_filter: Optional[List[str]] = None,
    return_images: bool = False,
    return_related_questions: bool = False,
    search_recency_filter: Optional[str] = None,
    top_k: int = 0,
    stream: bool = False,
    presence_penalty: float = 0.0,
    frequency_penalty: float = 1.0,
    response_format: Optional[Dict[str, Any]] = None,
    web_search_options: Optional[Dict[str, Any]] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Send a chat-completion request to the Perplexity API (asynchronous).
    """
    if not PERPLEXITY_API_KEY:
        raise ValueError("PERPLEXITY_API_KEY environment variable not set.")

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "top_p": top_p,
        "return_images": return_images,
        "return_related_questions": return_related_questions,
        "top_k": top_k,
        "stream": stream,
        "presence_penalty": presence_penalty,
        "frequency_penalty": frequency_penalty,
    }
    if max_tokens is not None:
        payload["max_tokens"] = max_tokens
    if search_domain_filter:
        payload["search_domain_filter"] = search_domain_filter
    if search_recency_filter:
        payload["search_recency_filter"] = search_recency_filter
    if response_format:
        payload["response_format"] = response_format
    if web_search_options:
        payload["web_search_options"] = web_search_options
    payload.update(kwargs)

    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(PERPLEXITY_API_URL, json=payload, headers=headers)
        resp.raise_for_status()
        return resp.json()


@flow(name="run_perplexity_flow")
def run_perplexity_flow():
    """
    Flow to run the synchronous Perplexity chat task.
    """
    messages = [
        {"role": "system", "content": "Be precise and concise."},
        {"role": "user", "content": "How many stars are there in our galaxy?"}
    ]
    try:
        result = perplexity_chat.submit(messages=messages, model="sonar", max_tokens=100).result()
        print("Response:", result)
    except Exception as e:
        print("Error during Perplexity API call:", e)


@flow(name="run_perplexity_flow_async")
def run_perplexity_flow_async():
    """
    Flow to run the asynchronous Perplexity chat task.
    """
    messages = [
        {"role": "system", "content": "Be precise and concise."},
        {"role": "user", "content": "How many stars are there in our galaxy?"}
    ]
    try:
        result = perplexity_chat_async.submit(messages=messages, model="sonar", max_tokens=100).result()
        print("Async Response:", result)
    except Exception as e:
        print("Async error during Perplexity API call:", e)


if __name__ == "__main__":
    run_perplexity_flow()
    # Uncomment to run async flow:
    # run_perplexity_flow_async()

```
