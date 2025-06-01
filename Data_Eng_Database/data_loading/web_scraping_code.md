### Available parameters to alter

-url (str): The root URL to begin crawling from.
-max_depth (int): The maximum depth of recursive loading (default: 2).
-use_async (bool): Whether to use asynchronous loading.
-extractor (Callable): Function to extract document contents from raw HTML.
-metadata_extractor (Callable): Function to extract metadata from HTML and URL.
-exclude_dirs (Sequence[str]): List of subdirectories to exclude from crawling.
-timeout (int): Timeout for HTTP requests in seconds (default: 10).
-prevent_outside (bool): If True, prevent loading URLs outside root URL (default: True).
-link_regex (str | Pattern): Regex for extracting sub-links from HTML.
-headers (Dict): Default request headers to use for all requests.
-check_response_status (bool): If True, skip URLs with error responses (default: False).
-continue_on_failure (bool): If True, continue if a link raises an exception (default: True).
-base_url (str): Base URL to check for outside links against.
-autoset_encoding (bool): Whether to auto-set response encoding (default: True).
-encoding (str): Explicit encoding of the response if manually set.
-proxies (Dict): Dictionary mapping protocol names to proxy URLs.
-lazy (bool): If True, return an iterator instead of a list (default: False).

```python
# from prefect import task, flow
from langchain_community.document_loaders import RecursiveUrlLoader
from typing import List, Dict, Any, Optional, Callable, Pattern, Sequence, Iterator, Union, AsyncIterator
from requests import Response
from aiohttp import ClientResponse
import re
import asyncio

@task(name="load_recursive_urls")
def load_recursive_urls(
    url: str,
    max_depth: Optional[int] = 2,
    use_async: Optional[bool] = None,
    extractor: Optional[Callable[[str], str]] = None,
    metadata_extractor: Optional[Union[
        Callable[[str, str], Dict],
        Callable[[str, str, Union[Response, ClientResponse]], Dict]
    ]] = None,
    exclude_dirs: Optional[Sequence[str]] = (),
    timeout: Optional[int] = 10,
    prevent_outside: bool = True,
    link_regex: Optional[Union[str, Pattern]] = None,
    headers: Optional[Dict] = None,
    check_response_status: bool = False,
    continue_on_failure: bool = True,
    base_url: Optional[str] = None,
    autoset_encoding: bool = True,
    encoding: Optional[str] = None,
    proxies: Optional[Dict] = None
) -> List[Any]:
    """
    Load documents recursively from a root URL.
    
    Args:
        url (str): The URL to crawl
        max_depth (Optional[int]): The max depth of the recursive loading (default: 2)
        use_async (Optional[bool]): Whether to use asynchronous loading
        extractor (Optional[Callable[[str], str]]): Function to extract document contents from raw HTML
        metadata_extractor (Optional[Union[Callable...]]): Function to extract metadata from raw HTML and URL
        exclude_dirs (Optional[Sequence[str]]): A list of subdirectories to exclude (default: ())
        timeout (Optional[int]): The timeout for requests, in seconds (default: 10)
        prevent_outside (bool): If True, prevent loading from URLs which are not children of root URL (default: True)
        link_regex (Optional[Union[str, Pattern]]): Regex for extracting sub-links from raw HTML
        headers (Optional[Dict]): Default request headers to use for all requests
        check_response_status (bool): If True, check HTTP response status and skip error responses (default: False)
        continue_on_failure (bool): If True, continue if getting or parsing a link raises an exception (default: True)
        base_url (Optional[str]): The base URL to check for outside links against
        autoset_encoding (bool): Whether to automatically set the encoding of the response (default: True)
        encoding (Optional[str]): The encoding of the response if manually set
        proxies (Optional[Dict]): A dictionary mapping protocol names to proxy URLs
        
    Returns:
        List[Any]: List of Document objects from recursive URLs
    """
    # Define default values to compare against
    defaults = {
        "max_depth": 2,
        "exclude_dirs": (),
        "timeout": 10,
        "prevent_outside": True,
        "check_response_status": False,
        "continue_on_failure": True,
        "autoset_encoding": True
    }
    
    # Start with the required parameter
    params = {"url": url}
    
    # Create a dictionary of all optional parameters
    optional_params = {
        "max_depth": max_depth,
        "use_async": use_async,
        "extractor": extractor,
        "metadata_extractor": metadata_extractor,
        "exclude_dirs": exclude_dirs,
        "timeout": timeout,
        "prevent_outside": prevent_outside,
        "link_regex": link_regex,
        "headers": headers,
        "check_response_status": check_response_status,
        "continue_on_failure": continue_on_failure,
        "base_url": base_url,
        "autoset_encoding": autoset_encoding,
        "encoding": encoding,
        "proxies": proxies
    }
    
    # Add optional parameters only if they're not None and differ from defaults
    params.update({
        k: v for k, v in optional_params.items() 
        if v is not None and (k not in defaults or v != defaults.get(k))
    })
    
    # Create the loader with only the necessary parameters
    loader = RecursiveUrlLoader(**params)
    
    return loader.load()

@task(name="lazy_load_recursive_urls")
def lazy_load_recursive_urls(
    url: str,
    max_depth: Optional[int] = 2,
    use_async: Optional[bool] = None,
    extractor: Optional[Callable[[str], str]] = None,
    metadata_extractor: Optional[Union[
        Callable[[str, str], Dict],
        Callable[[str, str, Union[Response, ClientResponse]], Dict]
    ]] = None,
    exclude_dirs: Optional[Sequence[str]] = (),
    timeout: Optional[int] = 10,
    prevent_outside: bool = True,
    link_regex: Optional[Union[str, Pattern]] = None,
    headers: Optional[Dict] = None,
    check_response_status: bool = False,
    continue_on_failure: bool = True,
    base_url: Optional[str] = None,
    autoset_encoding: bool = True,
    encoding: Optional[str] = None,
    proxies: Optional[Dict] = None
) -> Iterator[Any]:
    """
    Lazy load documents recursively from a root URL.
    
    Args:
        url (str): The URL to crawl
        max_depth (Optional[int]): The max depth of the recursive loading (default: 2)
        use_async (Optional[bool]): Whether to use asynchronous loading
        extractor (Optional[Callable[[str], str]]): Function to extract document contents from raw HTML
        metadata_extractor (Optional[Union[Callable...]]): Function to extract metadata from raw HTML and URL
        exclude_dirs (Optional[Sequence[str]]): A list of subdirectories to exclude (default: ())
        timeout (Optional[int]): The timeout for requests, in seconds (default: 10)
        prevent_outside (bool): If True, prevent loading from URLs which are not children of root URL (default: True)
        link_regex (Optional[Union[str, Pattern]]): Regex for extracting sub-links from raw HTML
        headers (Optional[Dict]): Default request headers to use for all requests
        check_response_status (bool): If True, check HTTP response status and skip error responses (default: False)
        continue_on_failure (bool): If True, continue if getting or parsing a link raises an exception (default: True)
        base_url (Optional[str]): The base URL to check for outside links against
        autoset_encoding (bool): Whether to automatically set the encoding of the response (default: True)
        encoding (Optional[str]): The encoding of the response if manually set
        proxies (Optional[Dict]): A dictionary mapping protocol names to proxy URLs
        
    Returns:
        Iterator[Any]: Iterator of Document objects from recursive URLs
    """
    # Define default values to compare against
    defaults = {
        "max_depth": 2,
        "exclude_dirs": (),
        "timeout": 10,
        "prevent_outside": True,
        "check_response_status": False,
        "continue_on_failure": True,
        "autoset_encoding": True
    }
    
    # Start with the required parameter
    params = {"url": url}
    
    # Create a dictionary of all optional parameters
    optional_params = {
        "max_depth": max_depth,
        "use_async": use_async,
        "extractor": extractor,
        "metadata_extractor": metadata_extractor,
        "exclude_dirs": exclude_dirs,
        "timeout": timeout,
        "prevent_outside": prevent_outside,
        "link_regex": link_regex,
        "headers": headers,
        "check_response_status": check_response_status,
        "continue_on_failure": continue_on_failure,
        "base_url": base_url,
        "autoset_encoding": autoset_encoding,
        "encoding": encoding,
        "proxies": proxies
    }
    
    # Add optional parameters only if they're not None and differ from defaults
    params.update({
        k: v for k, v in optional_params.items() 
        if v is not None and (k not in defaults or v != defaults.get(k))
    })
    
    # Create the loader with only the necessary parameters
    loader = RecursiveUrlLoader(**params)
    
    return loader.lazy_load()

@task(name="aload_recursive_urls")
async def aload_recursive_urls(
    url: str,
    max_depth: Optional[int] = 2,
    use_async: Optional[bool] = True,
    extractor: Optional[Callable[[str], str]] = None,
    metadata_extractor: Optional[Union[
        Callable[[str, str], Dict],
        Callable[[str, str, Union[Response, ClientResponse]], Dict]
    ]] = None,
    exclude_dirs: Optional[Sequence[str]] = (),
    timeout: Optional[int] = 10,
    prevent_outside: bool = True,
    link_regex: Optional[Union[str, Pattern]] = None,
    headers: Optional[Dict] = None,
    check_response_status: bool = False,
    continue_on_failure: bool = True,
    base_url: Optional[str] = None,
    autoset_encoding: bool = True,
    encoding: Optional[str] = None,
    proxies: Optional[Dict] = None
) -> List[Any]:
    """
    Asynchronously load documents recursively from a root URL.
    
    Args:
        url (str): The URL to crawl
        max_depth (Optional[int]): The max depth of the recursive loading (default: 2)
        use_async (Optional[bool]): Whether to use asynchronous loading (default: True)
        extractor (Optional[Callable[[str], str]]): Function to extract document contents from raw HTML
        metadata_extractor (Optional[Union[Callable...]]): Function to extract metadata from raw HTML and URL
        exclude_dirs (Optional[Sequence[str]]): A list of subdirectories to exclude (default: ())
        timeout (Optional[int]): The timeout for requests, in seconds (default: 10)
        prevent_outside (bool): If True, prevent loading from URLs which are not children of root URL (default: True)
        link_regex (Optional[Union[str, Pattern]]): Regex for extracting sub-links from raw HTML
        headers (Optional[Dict]): Default request headers to use for all requests
        check_response_status (bool): If True, check HTTP response status and skip error responses (default: False)
        continue_on_failure (bool): If True, continue if getting or parsing a link raises an exception (default: True)
        base_url (Optional[str]): The base URL to check for outside links against
        autoset_encoding (bool): Whether to automatically set the encoding of the response (default: True)
        encoding (Optional[str]): The encoding of the response if manually set
        proxies (Optional[Dict]): A dictionary mapping protocol names to proxy URLs
        
    Returns:
        List[Any]: List of Document objects from recursive URLs
    """
    # Define default values to compare against
    defaults = {
        "max_depth": 2,
        "exclude_dirs": (),
        "timeout": 10,
        "prevent_outside": True,
        "check_response_status": False,
        "continue_on_failure": True,
        "autoset_encoding": True
    }
    
    # Start with the required parameter
    params = {"url": url}
    

    optional_params = {
        "max_depth": max_depth,
        "use_async": use_async,
        "extractor": extractor,
        "metadata_extractor": metadata_extractor,
        "exclude_dirs": exclude_dirs,
        "timeout": timeout,
        "prevent_outside": prevent_outside,
        "link_regex": link_regex,
        "headers": headers,
        "check_response_status": check_response_status,
        "continue_on_failure": continue_on_failure,
        "base_url": base_url,
        "autoset_encoding": autoset_encoding,
        "encoding": encoding,
        "proxies": proxies
    }
    
    # Add optional parameters only if they're not None and differ from defaults
    params.update({
        k: v for k, v in optional_params.items() 
        if v is not None and (k not in defaults or v != defaults.get(k))
    })
    
    # Create the loader with only the necessary parameters
    loader = RecursiveUrlLoader(**params)
    
    return await loader.aload()

@task(name="alazy_load_recursive_urls")
async def alazy_load_recursive_urls(
    url: str,
    max_depth: Optional[int] = 2,
    use_async: Optional[bool] = True,
    extractor: Optional[Callable[[str], str]] = None,
    metadata_extractor: Optional[Union[
        Callable[[str, str], Dict],
        Callable[[str, str, Union[Response, ClientResponse]], Dict]
    ]] = None,
    exclude_dirs: Optional[Sequence[str]] = (),
    timeout: Optional[int] = 10,
    prevent_outside: bool = True,
    link_regex: Optional[Union[str, Pattern]] = None,
    headers: Optional[Dict] = None,
    check_response_status: bool = False,
    continue_on_failure: bool = True,
    base_url: Optional[str] = None,
    autoset_encoding: bool = True,
    encoding: Optional[str] = None,
    proxies: Optional[Dict] = None
) -> AsyncIterator[Any]:
    """
    Asynchronously and lazily load documents recursively from a root URL.
    
    Args:
        url (str): The URL to crawl
        max_depth (Optional[int]): The max depth of the recursive loading (default: 2)
        use_async (Optional[bool]): Whether to use asynchronous loading (default: True)
        extractor (Optional[Callable[[str], str]]): Function to extract document contents from raw HTML
        metadata_extractor (Optional[Union[Callable...]]): Function to extract metadata from raw HTML and URL
        exclude_dirs (Optional[Sequence[str]]): A list of subdirectories to exclude (default: ())
        timeout (Optional[int]): The timeout for requests, in seconds (default: 10)
        prevent_outside (bool): If True, prevent loading from URLs which are not children of root URL (default: True)
        link_regex (Optional[Union[str, Pattern]]): Regex for extracting sub-links from raw HTML
        headers (Optional[Dict]): Default request headers to use for all requests
        check_response_status (bool): If True, check HTTP response status and skip error responses (default: False)
        continue_on_failure (bool): If True, continue if getting or parsing a link raises an exception (default: True)
        base_url (Optional[str]): The base URL to check for outside links against
        autoset_encoding (bool): Whether to automatically set the encoding of the response (default: True)
        encoding (Optional[str]): The encoding of the response if manually set
        proxies (Optional[Dict]): A dictionary mapping protocol names to proxy URLs
        
    Returns:
        AsyncIterator[Any]: Async iterator of Document objects from recursive URLs
    """
    # Define default values to compare against
    defaults = {
        "max_depth": 2,
        "exclude_dirs": (),
        "timeout": 10,
        "prevent_outside": True,
        "check_response_status": False,
        "continue_on_failure": True,
        "autoset_encoding": True
    }
    
    # Start with the required parameter
    params = {"url": url}
    
    # Create a dictionary of all optional parameters
    optional_params = {
        "max_depth": max_depth,
        "use_async": use_async,
        "extractor": extractor,
        "metadata_extractor": metadata_extractor,
        "exclude_dirs": exclude_dirs,
        "timeout": timeout,
        "prevent_outside": prevent_outside,
        "link_regex": link_regex,
        "headers": headers,
        "check_response_status": check_response_status,
        "continue_on_failure": continue_on_failure,
        "base_url": base_url,
        "autoset_encoding": autoset_encoding,
        "encoding": encoding,
        "proxies": proxies
    }

    params.update({
        k: v for k, v in optional_params.items() 
        if v is not None and (k not in defaults or v != defaults.get(k))
    })
    

    loader = RecursiveUrlLoader(**params)
    
    return loader.alazy_load()

@flow(name="recursive_url_loader_flow")
def recursive_url_loader_flow(
    url: str,
    max_depth: Optional[int] = 2,
    use_async: Optional[bool] = None,
    extractor: Optional[Callable[[str], str]] = None,
    metadata_extractor: Optional[Union[
        Callable[[str, str], Dict],
        Callable[[str, str, Union[Response, ClientResponse]], Dict]
    ]] = None,
    exclude_dirs: Optional[Sequence[str]] = (),
    timeout: Optional[int] = 10,
    prevent_outside: bool = True,
    link_regex: Optional[Union[str, Pattern]] = None,
    headers: Optional[Dict] = None,
    check_response_status: bool = False,
    continue_on_failure: bool = True,
    base_url: Optional[str] = None,
    autoset_encoding: bool = True,
    encoding: Optional[str] = None,
    proxies: Optional[Dict] = None,
    lazy: bool = False
) -> Union[List[Any], Iterator[Any]]:
    """
    Flow to load documents recursively from a URL with comprehensive options.
    
    Args:
        url (str): The URL to crawl
        max_depth (Optional[int]): The max depth of the recursive loading (default: 2)
        use_async (Optional[bool]): Whether to use asynchronous loading
        extractor (Optional[Callable[[str], str]]): Function to extract document contents from raw HTML
        metadata_extractor (Optional[Union[Callable...]]): Function to extract metadata from raw HTML and URL
        exclude_dirs (Optional[Sequence[str]]): A list of subdirectories to exclude (default: ())
        timeout (Optional[int]): The timeout for requests, in seconds (default: 10)
        prevent_outside (bool): If True, prevent loading from URLs which are not children of root URL (default: True)
        link_regex (Optional[Union[str, Pattern]]): Regex for extracting sub-links from raw HTML
        headers (Optional[Dict]): Default request headers to use for all requests
        check_response_status (bool): If True, check HTTP response status and skip error responses (default: False)
        continue_on_failure (bool): If True, continue if getting or parsing a link raises an exception (default: True)
        base_url (Optional[str]): The base URL to check for outside links against
        autoset_encoding (bool): Whether to automatically set the encoding of the response (default: True)
        encoding (Optional[str]): The encoding of the response if manually set
        proxies (Optional[Dict]): A dictionary mapping protocol names to proxy URLs
        lazy (bool): If True, return an iterator instead of a list (default: False)
        
    Returns:
        Union[List[Any], Iterator[Any]]: List or iterator of Document objects depending on lazy parameter
    """
    if lazy:
        result = lazy_load_recursive_urls(
            url=url,
            max_depth=max_depth,
            use_async=use_async,
            extractor=extractor,
            metadata_extractor=metadata_extractor,
            exclude_dirs=exclude_dirs,
            timeout=timeout,
            prevent_outside=prevent_outside,
            link_regex=link_regex,
            headers=headers,
            check_response_status=check_response_status,
            continue_on_failure=continue_on_failure,
            base_url=base_url,
            autoset_encoding=autoset_encoding,
            encoding=encoding,
            proxies=proxies
        )
    else:
        result= load_recursive_urls(
            url=url,
            max_depth=max_depth,
            use_async=use_async,
            extractor=extractor,
            metadata_extractor=metadata_extractor,
            exclude_dirs=exclude_dirs,
            timeout=timeout,
            prevent_outside=prevent_outside,
            link_regex=link_regex,
            headers=headers,
            check_response_status=check_response_status,
            continue_on_failure=continue_on_failure,
            base_url=base_url,
            autoset_encoding=autoset_encoding,
            encoding=encoding,
            proxies=proxies
        )
    return result

@flow(name="async_recursive_url_loader_flow")
async def async_recursive_url_loader_flow(
    url: str,
    max_depth: Optional[int] = 2,
    use_async: Optional[bool] = True,
    extractor: Optional[Callable[[str], str]] = None,
    metadata_extractor: Optional[Union[
        Callable[[str, str], Dict],
        Callable[[str, str, Union[Response, ClientResponse]], Dict]
    ]] = None,
    exclude_dirs: Optional[Sequence[str]] = (),
    timeout: Optional[int] = 10,
    prevent_outside: bool = True,
    link_regex: Optional[Union[str, Pattern]] = None,
    headers: Optional[Dict] = None,
    check_response_status: bool = False,
    continue_on_failure: bool = True,
    base_url: Optional[str] = None,
    autoset_encoding: bool = True,
    encoding: Optional[str] = None,
    proxies: Optional[Dict] = None,
    lazy: bool = False
) -> Union[List[Any], AsyncIterator[Any]]:
    """
    Asynchronous flow to load documents recursively from a URL with comprehensive options.
    
    Args:
        url (str): The URL to crawl
        max_depth (Optional[int]): The max depth of the recursive loading (default: 2)
        use_async (Optional[bool]): Whether to use asynchronous loading (default: True)
        extractor (Optional[Callable[[str], str]]): Function to extract document contents from raw HTML
        metadata_extractor (Optional[Union[Callable...]]): Function to extract metadata from raw HTML and URL
        exclude_dirs (Optional[Sequence[str]]): A list of subdirectories to exclude (default: ())
        timeout (Optional[int]): The timeout for requests, in seconds (default: 10)
        prevent_outside (bool): If True, prevent loading from URLs which are not children of root URL (default: True)
        link_regex (Optional[Union[str, Pattern]]): Regex for extracting sub-links from raw HTML
        headers (Optional[Dict]): Default request headers to use for all requests
        check_response_status (bool): If True, check HTTP response status and skip error responses (default: False)
        continue_on_failure (bool): If True, continue if getting or parsing a link raises an exception (default: True)
        base_url (Optional[str]): The base URL to check for outside links against
        autoset_encoding (bool): Whether to automatically set the encoding of the response (default: True)
        encoding (Optional[str]): The encoding of the response if manually set
        proxies (Optional[Dict]): A dictionary mapping protocol names to proxy URLs
        lazy (bool): If True, return an async iterator instead of a list (default: False)
        
    Returns:
        Union[List[Any], AsyncIterator[Any]]: List or async iterator of Document objects depending on lazy parameter
    """
    if lazy:
        result= await alazy_load_recursive_urls(
            url=url,
            max_depth=max_depth,
            use_async=use_async,
            extractor=extractor,
            metadata_extractor=metadata_extractor,
            exclude_dirs=exclude_dirs,
            timeout=timeout,
            prevent_outside=prevent_outside,
            link_regex=link_regex,
            headers=headers,
            check_response_status=check_response_status,
            continue_on_failure=continue_on_failure,
            base_url=base_url,
            autoset_encoding=autoset_encoding,
            encoding=encoding,
            proxies=proxies
        )
    else:
        result= await aload_recursive_urls(
            url=url,
            max_depth=max_depth,
            use_async=use_async,
            extractor=extractor,
            metadata_extractor=metadata_extractor,
            exclude_dirs=exclude_dirs,
            timeout=timeout,
            prevent_outside=prevent_outside,
            link_regex=link_regex,
            headers=headers,
            check_response_status=check_response_status,
            continue_on_failure=continue_on_failure,
            base_url=base_url,
            autoset_encoding=autoset_encoding,
            encoding=encoding,
            proxies=proxies
        )
    return result

# Example usage
if __name__ == "__main__":

    result = recursive_url_loader_flow()
    async def test_async():
        
        async_result = await async_recursive_url_loader_flow()
        
        # 3. Test async lazy loading (iterator)
        async_iter = await async_recursive_url_loader_flow()
        # async for doc in async_iter:
        #     print("ASYNC ITERATOR RESULT:",doc)
    # Run the async test function
    asyncio.run(test_async())

# Sample output format:
# The result is a list of Document objects, where each Document has:
# - metadata: A dictionary containing 'source' (URL), 'content_type', 'title', and 'language'
# - page_content: The extracted text content from the webpage
#
# Example:
# [Document(
#     metadata={
#         'source': 'https://docs.python.org/3.9/', 
#         'content_type': 'text/html', 
#         'title': '3.9.22 Documentation', 
#         'language': None
#     }, 
#     page_content='3.9.22 Documentation\n\nDownload\nDownload these documents\nDocs by version\n...'
# )]



# Sample output format for lazy loading:
# The result is an iterator that yields Document objects one at a time.
# Each Document has the same structure as in the synchronous version.
#
# Example Document from the iterator:
    # Document(
    #     page_content='The Python Language Reference — Python 3.9.22 documentation\nPrevious topic\n5. Editors and IDEs\nNext topic\n...',
    #     metadata={
    #         'source': 'https://docs.python.org/3.9/reference/', 
    #         'content_type': 'text/html', 
    #         'title': 'The Python Language Reference — Python 3.9.22 documentation', 
    #         'language': None
    #     }
    # )
```

# FIRE CRAWL
### Available parameters to alter

#### For firecrawl_scrape_flow:
- url (str): The URL to scrape
- api_key (str): Your Firecrawl API key (can also be set via FIRECRAWL_API_KEY environment variable)
- formats (List[str]): List of output formats to return
- only_main_content (bool): Whether to extract only the main content of the page
- include_tags (List[str]): List of HTML tags to include in the extraction
- exclude_tags (List[str]): List of HTML tags to exclude from the extraction
- wait_for (int): Time to wait for dynamic content to load (in milliseconds)
- timeout (int): Maximum time to wait for the page to load (in milliseconds)
- extract_prompt (str): Custom prompt for content extraction
- extract_schema (Dict): Schema defining the structure of extracted data
- system_prompt (str): Custom system prompt for the extraction process
- actions (List[Dict]): List of custom actions to perform during scraping

#### For firecrawl_crawl_flow:
- url (str): The root URL to begin crawling from
- api_key (str): Your Firecrawl API key (can also be set via FIRECRAWL_API_KEY environment variable)
- include_paths (List[str]): List of URL patterns to include in crawling
- exclude_paths (List[str]): List of URL patterns to exclude from crawling
- max_depth (int): Maximum depth of recursive crawling
- limit (int): Maximum number of pages to crawl
- allow_backward_links (bool): Whether to allow crawling of parent/previous pages
- allow_external_links (bool): Whether to allow crawling of external domains
- delay (float): Delay between requests in seconds
- formats (List[str]): List of output formats to return
- only_main_content (bool): Whether to extract only the main content of pages
- include_tags (List[str]): List of HTML tags to include in extraction
- exclude_tags (List[str]): List of HTML tags to exclude from extraction
- wait_for (int): Time to wait for dynamic content to load (in milliseconds)
- timeout (int): Maximum time to wait for pages to load (in milliseconds)
- check_status (bool): Whether to check and return the crawl job status

``` python
from typing import List, Dict, Any, Optional
from firecrawl import FirecrawlApp, ScrapeOptions
import os

def _filter_none(params: Dict[str, Any]) -> Dict[str, Any]:
    """Return a copy of params with all None values removed."""
    return {k: v for k, v in params.items() if v is not None}


def scrape_firecrawl(
    url: str,
    api_key: str,
    **kwargs
) -> Dict[str, Any]:
    app = FirecrawlApp(api_key=api_key)
    return app.scrape_url(url, **kwargs)


def crawl_firecrawl(
    url: str,
    api_key: str,
    formats: Optional[List[str]] = None,
    only_main_content: Optional[bool] = None,
    include_tags: Optional[List[str]] = None,
    exclude_tags: Optional[List[str]] = None,
    wait_for: Optional[int] = None,
    timeout: Optional[int] = None,
    **kwargs
) -> Dict[str, Any]:
    app = FirecrawlApp(api_key=api_key)

    # collect only the non-None arguments
    opts = _filter_none({
        "formats": formats,
        "only_main_content": only_main_content,
        "include_tags": include_tags,
        "exclude_tags": exclude_tags,
        "wait_for": wait_for,
        "timeout": timeout,
    })

    if opts:
        kwargs["scrape_options"] = ScrapeOptions(**opts)

    return app.crawl_url(url, **kwargs)


def firecrawl_scrape_flow(
    url: str,
    api_key: Optional[str] = None,
    formats: Optional[List[str]] = None,
    only_main_content: Optional[bool] = None,
    include_tags: Optional[List[str]] = None,
    exclude_tags: Optional[List[str]] = None,
    wait_for: Optional[int] = None,
    timeout: Optional[int] = None,
    extract_prompt: Optional[str] = None,
    extract_schema: Optional[Dict] = None,
    system_prompt: Optional[str] = None,
    actions: Optional[List[Dict]] = None,
) -> Dict[str, Any]:
    api_key = api_key or os.getenv("FIRECRAWL_API_KEY", "")
    params = _filter_none({
        "formats": formats,
        "only_main_content": only_main_content,
        "include_tags": include_tags,
        "exclude_tags": exclude_tags,
        "wait_for": wait_for,
        "timeout": timeout,
        "extract_prompt": extract_prompt,
        "extract_schema": extract_schema,
        "system_prompt": system_prompt,
        "actions": actions,
    })
    return scrape_firecrawl(url=url, api_key=api_key, **params)


def firecrawl_crawl_flow(
    url: str,
    api_key: Optional[str] = None,
    include_paths: Optional[List[str]] = None,
    exclude_paths: Optional[List[str]] = None,
    max_depth: Optional[int] = None,
    limit: Optional[int] = None,
    allow_backward_links: Optional[bool] = None,
    allow_external_links: Optional[bool] = None,
    delay: Optional[float] = None,
    formats: Optional[List[str]] = None,
    only_main_content: Optional[bool] = None,
    include_tags: Optional[List[str]] = None,
    exclude_tags: Optional[List[str]] = None,
    wait_for: Optional[int] = None,
    timeout: Optional[int] = None,
    check_status: bool = False,
) -> Dict[str, Any]:
    api_key = api_key or os.getenv("FIRECRAWL_API_KEY", "YOUR_API_KEY")

    # top-level crawl params
    crawl_params = _filter_none({
        "include_paths": include_paths,
        "exclude_paths": exclude_paths,
        "max_depth": max_depth,
        "limit": limit,
        "allow_backward_links": allow_backward_links,
        "allow_external_links": allow_external_links,
        "delay": delay,
        # pass through the same page-level options
        "formats": formats,
        "only_main_content": only_main_content,
        "include_tags": include_tags,
        "exclude_tags": exclude_tags,
        "wait_for": wait_for,
        "timeout": timeout,
    })

    response = crawl_firecrawl(url=url, api_key=api_key, **crawl_params)

    if check_status and "id" in response:
        return check_crawl_job_firecrawl(job_id=response["id"], api_key=api_key)

    return response

```
<!-- 
EXPECTED OUTPUT FORMAT:
{
    "url": "string",           // The URL that was scraped
    "markdown": "string",      // The scraped content in markdown format
    "html": "string",          // The raw HTML content (if requested)
    "rawHtml": "string",       // The unprocessed HTML content
    "links": ["string"],       // List of links found on the page
    "extract": "string",       // Extracted structured data (if extraction was requested)
    "json": object,            // JSON representation of the extracted data
    "screenshot": "string",    // Base64 encoded screenshot (if requested)
    "metadata": {              // Page metadata
        "title": "string",
        "description": "string",
        "language": "string",
        // ... other metadata fields
    },
    "actions": ["string"],     // List of actions performed
    "title": "string",         // Page title
    "description": "string",   // Page description
    "changeTracking": object,  // Change tracking information
    "success": boolean,        // Whether the scrape was successful
    "warning": "string",       // Warning message if any
    "error": "string"          // Error message if any
}
```

#### For Crawl Response:
```json
{
    "success": boolean,        // Whether the crawl job was successfully created
    "status": "string",        // Status of the crawl job (e.g., "completed", "in_progress")
    "completed": integer,      // Number of pages completed
    "total": integer,          // Total number of pages to crawl
    "creditsUsed": integer,    // Number of credits used
    "expiresAt": "string",     // ISO timestamp when the crawl results expire
    "results": [{              // Array of crawled page results
        "url": "string",
        "markdown": "string",
        "html": "string",
        "metadata": object,
        // ... other page-specific fields
    }]
} -->


# AGENTQL

### Available parameters to alter 
- url (str): The URL to scrape
- wait_for_network_idle (bool): Whether to wait for network to be idle before scraping (default: True)
- stealth_config (Dict[str, str]): Configuration for stealth mode (default: None)

#### Search
- search_prompt (str): Prompt to locate search input field (default: "Search input field")
- search_text (str): Text to search for (default: "")
- prompt_timeout (int): Timeout for prompt queries in seconds (default: 10)
- prompt_wait_for_network_idle (bool): Whether to wait for network idle after prompt queries (default: True)
- prompt_include_hidden (bool): Whether to include hidden elements in prompt queries (default: False)
- prompt_mode (str): Mode for prompt queries (default: "fast")
- prompt_experimental (bool): Whether to use experimental features for prompt queries (default: False)

#### Elements and Data Extraction
- elements_query (str): Query to extract page elements (default: "")
- elements_timeout (int): Timeout for elements queries in seconds (default: 20)
- elements_wait_for_network_idle (bool): Whether to wait for network idle after elements queries (default: True)
- elements_include_hidden (bool): Whether to include hidden elements in elements queries (default: False)
- elements_mode (str): Mode for elements queries (default: "standard")
- elements_experimental (bool): Whether to use experimental features for elements queries (default: False)
- data_query (str): Query to extract structured data (default: "")
- data_timeout (int): Timeout for data queries in seconds (default: 20)
- data_wait_for_network_idle (bool): Whether to wait for network idle after data queries (default: True)
- data_include_hidden (bool): Whether to include hidden elements in data queries (default: True)
- data_mode (str): Mode for data queries (default: "fast")

#### Pagination
- paginate_query (str): Query to locate pagination controls (default: "")
- paginate_pages (int): Number of pages to paginate (default: 3)
- paginate_timeout (int): Timeout for pagination queries in seconds (default: 15)
- paginate_wait_for_network_idle (bool): Whether to wait for network idle after pagination (default: True)
- paginate_include_hidden (bool): Whether to include hidden elements in pagination (default: False)
- paginate_mode (str): Mode for pagination (default: "fast")
- paginate_force_click (bool): Whether to force click on pagination links (default: False)


```python
from typing import Optional, Dict, Any, Tuple
from prefect import task, flow
from playwright.sync_api import sync_playwright, Page as PWPage
import agentql
from agentql.tools.sync_api import paginate

# --- Tasks ---
@task(name="Create Browser Page")
def create_page(
    url: str,
    wait_for_network_idle: bool = True
) -> PWPage:
    """
    Launch browser, wrap Playwright page with AgentQL, navigate to URL.
    """
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=False)
    raw_page = browser.new_page()
    page = agentql.wrap(raw_page)
    page.goto(url)
    page.wait_for_page_ready_state(wait_for_network_idle=wait_for_network_idle)
    return page

@task(name="Apply Stealth Mode")
def apply_stealth(
    page: PWPage,
    stealth_config: Optional[Dict[str, str]] = None
) -> PWPage:
    """
    Enable stealth mode if configuration provided.
    """
    if stealth_config:
        page.enable_stealth_mode(
            webgl_vendor=stealth_config.get("webgl_vendor"),
            webgl_renderer=stealth_config.get("webgl_renderer"),
            nav_user_agent=stealth_config.get("nav_user_agent"),
        )
    return page

@task(name="Search With Prompt")
def prompt_search(
    page: PWPage,
    search_prompt: str,
    search_text: str,
    timeout: int,
    wait_for_network_idle: bool,
    include_hidden: bool,
    mode: str,
    experimental: bool
) -> PWPage:
    """
    Locate input by prompt, type text, click button.
    """
    input_el = page.get_by_prompt(
        prompt=search_prompt,
        timeout=timeout,
        wait_for_network_idle=wait_for_network_idle,
        include_hidden=include_hidden,
        mode=mode
    )
    input_el.type(search_text)
    button = page.get_by_prompt(
        prompt="Search button",
        timeout=timeout,
        wait_for_network_idle=wait_for_network_idle,
        include_hidden=include_hidden,
        mode=mode,
        experimental_query_elements_enabled=experimental
    )
    button.click()
    page.wait_for_page_ready_state(wait_for_network_idle=wait_for_network_idle)
    return page

@task(name="Extract Page Elements")
def extract_elements(
    page: PWPage,
    elements_query: str,
    timeout: int,
    wait_for_network_idle: bool,
    include_hidden: bool,
    mode: str,
    experimental: bool
) -> Any:
    """
    Query multiple elements and return structured data.
    """
    resp = page.query_elements(
        query=elements_query,
        timeout=timeout,
        wait_for_network_idle=wait_for_network_idle,
        include_hidden=include_hidden,
        mode=mode,
        experimental_query_elements_enabled=experimental
    )
    return resp.to_data()

@task(name="Extract Structured Data")
def extract_data(
    page: PWPage,
    data_query: str,
    timeout: int,
    wait_for_network_idle: bool,
    include_hidden: bool,
    mode: str
) -> Any:
    """
    Query structured data blocks.
    """
    return page.query_data(
        query=data_query,
        timeout=timeout,
        wait_for_network_idle=wait_for_network_idle,
        include_hidden=include_hidden,
        mode=mode
    )

@task(name="Auto Paginate Results")
def auto_paginate(
    page: PWPage,
    paginate_query: str,
    pages: int,
    timeout: int,
    wait_for_network_idle: bool,
    include_hidden: bool,
    mode: str,
    force_click: bool
) -> Any:
    """
    Collect data across multiple pages.
    """
    return paginate(
        page=page,
        query=paginate_query,
        number_of_pages=pages,
        timeout=timeout,
        wait_for_network_idle=wait_for_network_idle,
        include_hidden=include_hidden,
        mode=mode,
        force_click=force_click
    )

@task(name="Manual Page Navigation")
def manual_pagination(
    page: PWPage,
    timeout: int,
    wait_for_network_idle: bool,
    include_hidden: bool,
    mode: str
) -> bool:
    """
    Navigate to next page if available.
    """
    info = page.get_pagination_info(
        timeout=timeout,
        wait_for_network_idle=wait_for_network_idle,
        include_hidden=include_hidden,
        mode=mode
    )
    if info.has_next_page:
        info.navigate_to_next_page()
        return True
    return False

@task(name="Introspect Page State")
def introspect(
    page: PWPage
) -> Dict[str, Any]:
    """
    Retrieve last query, response, and accessibility tree.
    """
    return {
        "last_query": page.get_last_query(),
        "last_response": page.get_last_response(),
        "accessibility_tree": page.get_last_accessibility_tree()
    }

# --- Flow ---
@flow
def agentql_sync_flow(
    url: str,
    wait_for_network_idle: bool = True,
    stealth_config: Optional[Dict[str, str]] = None,
    search_prompt: str = "Search input field",
    search_text: str = "",
    prompt_timeout: int = 10,
    prompt_wait_for_network_idle: bool = True,
    prompt_include_hidden: bool = False,
    prompt_mode: str = "fast",
    prompt_experimental: bool = False,
    elements_query: str = "",
    elements_timeout: int = 20,
    elements_wait_for_network_idle: bool = True,
    elements_include_hidden: bool = False,
    elements_mode: str = "standard",
    elements_experimental: bool = False,
    data_query: str = "",
    data_timeout: int = 20,
    data_wait_for_network_idle: bool = True,
    data_include_hidden: bool = True,
    data_mode: str = "fast",
    paginate_query: str = "",
    paginate_pages: int = 3,
    paginate_timeout: int = 15,
    paginate_wait_for_network_idle: bool = True,
    paginate_include_hidden: bool = False,
    paginate_mode: str = "fast",
    paginate_force_click: bool = False
) -> Tuple[Any, Any, Any, bool, Dict[str, Any]]:
    """
    Sync flow orchestrating individual tasks for AgentQL interactions.
    """
    # 1. Create and wrap page
    page = create_page(url, wait_for_network_idle)
    # 2. Stealth
    page = apply_stealth(page, stealth_config)
    # 3. Prompt search
    if search_text:
        page = prompt_search(
            page, search_prompt, search_text,
            prompt_timeout, prompt_wait_for_network_idle,
            prompt_include_hidden, prompt_mode,
            prompt_experimental
        )
    # 4. Elements extraction
    elements = None
    if elements_query:
        elements = extract_elements(
            page, elements_query,
            elements_timeout, elements_wait_for_network_idle,
            elements_include_hidden, elements_mode,
            elements_experimental
        )
    # 5. Data extraction
    data_blocks = None
    if data_query:
        data_blocks = extract_data(
            page, data_query,
            data_timeout, data_wait_for_network_idle,
            data_include_hidden, data_mode
        )
    # 6. Auto pagination
    paginated = None
    if paginate_query:
        paginated = auto_paginate(
            page, paginate_query,
            paginate_pages, paginate_timeout,
            paginate_wait_for_network_idle,
            paginate_include_hidden, paginate_mode,
            paginate_force_click
        )
    # 7. Manual pagination
    manual_nav = manual_pagination(
        page, paginate_timeout,
        paginate_wait_for_network_idle,
        paginate_include_hidden, paginate_mode
    )
    # 8. Introspection
    logs = introspect(page)


    print("Results -> Elements:", elements)
    print("Data Blocks:", data_blocks)
    print("Paginated:", paginated)
    print("Manual Nav:", manual_nav)
    print("Logs:", logs)

    return elements, data_blocks, paginated, manual_nav, logs

# Example invocation:
if __name__ == "__main__":
    agentql_sync_flow()

```
