# Sentence Transformers
```python
from prefect import task, flow
from sentence_transformers import SentenceTransformer
import numpy as np

@task(name="calculate_sentence_embeddings")
def calculate_embeddings(sentences, model_name):
    """
    Calculate embeddings for a list of sentences using a SentenceTransformer model.
    
    Args:
        sentences (list): List of strings to encode
        model_name (str): Name of the SentenceTransformer model to use
        
    Returns:
        tuple: (embeddings, similarities) - The embeddings array and similarity matrix
    """
    # 1. Load the pretrained Sentence Transformer model
    model = SentenceTransformer(model_name)
    
    # 2. Calculate embeddings
    embeddings = model.encode(sentences)
    print(f"Embeddings shape: {embeddings.shape}")
    
    # 3. Calculate the embedding similarities
    similarities = model.similarity(embeddings, embeddings)
    print("Similarities matrix:")
    print(similarities)
    
    return embeddings, similarities

@flow(name="sentence_embedding_flow")
def sentence_embedding_flow():
    # Example sentences
    sentences = [
        "The weather is lovely today.",
        "It's so sunny outside!",
        "He drove to the stadium.",
    ]
    
    # Replace with your desired model name
    model_name = "nvidia/NV-Embed-v2"  # This parameter is allowed to be altered from the options mentioned
    
    # Run the task
    embeddings, similarities = calculate_embeddings(sentences, model_name)
    
    return embeddings, similarities

# Run the flow if executed directly
if __name__ == "__main__":
    sentence_embedding_flow()
```
### Available parameters to alter
model_name:
- "intfloat/multilingual-e5-large-instruct"
- "nvidia/NV-Embed-v2"
- "Alibaba-NLP/gte-Qwen2-7B-instruct"
- "Alibaba-NLP/gte-Qwen2-1.5B-instruct"

# Cohere API
## embed-v4.0
- Embed Text
```python
from prefect import task, flow
import cohere

@task(name="calculate_cohere_embeddings")
def calculate_cohere_embeddings(texts, model_name, input_type, api_key=None):
    """
    Calculate embeddings for a list of texts using Cohere's API.
    
    Args:
        texts (list): List of strings to encode
        model_name (str): Name of the Cohere embedding model to use
        input_type (str): Type of input (e.g., "search_document", "search_query", etc.)
        api_key (str, optional): Cohere API key. If None, will use environment variable.
        
    Returns:
        dict: The complete response from Cohere's API
    """
    # Initialize the Cohere client
    co = cohere.ClientV2(api_key)
    
    # Request embeddings from Cohere
    response = co.embed(
        texts=texts,
        model=model_name,
        input_type=input_type,
        embedding_types=["float"],
    )
    
    # Print the response for debugging
    print(f"Response ID: {response.id}")
    print(f"Embedding dimensions: {len(response.embeddings['float'][0])}")
    print(f"Number of embeddings: {len(response.embeddings['float'])}")
    
    return response

@flow(name="cohere_embedding_flow")
def cohere_embedding_flow(api_key=None):
    # Example texts
    texts = ["hello", "goodbye"]
    
    # Model parameters
    model_name = "embed-v4.0" # STAYS FIXED
    input_type = "search_document"  # This parameter is allowed to be altered from the options mentioned
    
    # Run the task
    response = calculate_cohere_embeddings(
        texts=texts,
        model_name=model_name,
        input_type=input_type,
        api_key=api_key
    )
    
    # You can process the response further here if needed
    return response

# Run the flow if executed directly
if __name__ == "__main__":
    cohere_embedding_flow()
    
# Example Response    
# {
#     "id" : "...",
#     "embeddings":{
#         "float":[[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
#         },
#     "texts":["hello", "goodbye"],
#     "meta": {
#       "api_version": {
#           "version": "2",
#           "is_experimental": true
#       },
#       "billed_units": {
#           "input_tokens": 2
#       },
#       "warnings": [
#           "You are using an experimental version, for more information please refer to https://docs.cohere.com/versioning-reference"
#       ]
#     }  
# }
```
### Available parameters to alter
input_type:
- "search_document": Used for embeddings stored in a vector database for search use-cases.
- "search_query": Used for embeddings of search queries run against a vector DB to find relevant documents.
- "classification": Used for embeddings passed through a text classifier.
- "clustering": Used for the embeddings run through a clustering algorithm.
- "image": Used for embeddings with image input.


- Embed Images
```python
from prefect import task, flow
import cohere
import requests
import base64

@task(name="fetch_image_as_base64")
def fetch_image_as_base64(image_url):
    """
    Fetch an image from a URL and convert it to base64 format.
    
    Args:
        image_url (str): URL of the image to fetch
        
    Returns:
        str: Base64-encoded image with content type prefix
    """
    # Fetch the image
    response = requests.get(image_url)
    
    # Check if the request was successful
    response.raise_for_status()
    
    # Get content type and encode image content as base64
    content_type = response.headers["Content-Type"]
    stringified_buffer = base64.b64encode(response.content).decode("utf-8")
    
    # Format as data URL
    image_base64 = f"data:{content_type};base64,{stringified_buffer}"
    
    return image_base64

@task(name="calculate_image_embeddings")
def calculate_image_embeddings(images, model_name, api_key=None):
    """
    Calculate embeddings for a list of base64-encoded images using Cohere's API.
    
    Args:
        images (list): List of base64-encoded images
        model_name (str): Name of the Cohere embedding model to use
        api_key (str, optional): Cohere API key. If None, will use environment variable.
        
    Returns:
        dict: The complete response from Cohere's API
    """
    # Initialize the Cohere client
    co = cohere.ClientV2(api_key)
    
    # Request embeddings from Cohere
    response = co.embed(
        model=model_name,
        input_type="image",
        embedding_types=["float"],
        images=images,
    )
    
    # Print the response for debugging
    print(f"Response ID: {response.id}")
    print(f"Embedding dimensions: {len(response.embeddings['float'][0])}")
    print(f"Number of embeddings: {len(response.embeddings['float'])}")
    
    # Print image metadata
    for i, img_metadata in enumerate(response.images):
        print(f"Image {i+1} metadata: {img_metadata}")
    
    return response

@flow(name="cohere_image_embedding_flow")
def cohere_image_embedding_flow(image_urls=None, api_key=None):
    """
    Flow to fetch images and generate embeddings using Cohere's API.
    
    Args:
        image_urls (list, optional): List of image URLs to process. 
                                    Defaults to Cohere favicon.
        api_key (str, optional): Cohere API key. If None, will use environment variable.
        
    Returns:
        dict: The complete response from Cohere's API
    """
    # Default to Cohere favicon if no URLs provided
    if image_urls is None:
        image_urls = ["https://cohere.com/favicon-32x32.png"]
    
    # Fetch and encode each image
    images_base64 = []
    for url in image_urls:
        image_base64 = fetch_image_as_base64(url)
        images_base64.append(image_base64)
    
    # Model parameters
    model_name = "embed-v4.0" # STAYS FIXED
    
    # Run the embeddings task
    response = calculate_image_embeddings(
        images=images_base64,
        model_name=model_name,
        api_key=api_key
    )
    
    return response

# Run the flow if executed directly
if __name__ == "__main__":
    cohere_image_embedding_flow()
    
# Example Response
# {
#     "id" : "...",
#     "embeddings":{
#         "float":[[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
#         },
#     "texts":[],
#     "images": [
#         {
#         "width": 400,
#         "height": 400,
#         "format": "jpeg",
#         "bit_depth": 24
#         }
#       ],  
#     "meta": {
#       "api_version": {
#           "version": "2",
#           "is_experimental": true
#       },
#       "billed_units": {
#           "images": 1
#       },
#       "warnings": [
#           "You are using an experimental version, for more information please refer to https://docs.cohere.com/versioning-reference"
#       ]
#     }  
# }
```

## rerank-v3.5
```python
from prefect import task, flow
import cohere
from typing import List, Dict, Any, Optional

@task(name="rerank_documents")
def rerank_documents(
    query: str,
    documents: List[str],
    model_name: str = "rerank-v3.5",
    top_n: int = 3,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Rerank a list of documents based on their relevance to a query using Cohere's API.
    
    Args:
        query (str): The search query
        documents (List[str]): List of documents to rerank
        model_name (str): Name of the Cohere reranking model to use
        top_n (int): Number of top results to return
        api_key (str, optional): Cohere API key. If None, will use environment variable.
        
    Returns:
        Dict[str, Any]: The complete response from Cohere's API
    """
    # Initialize the Cohere client
    co = cohere.ClientV2(api_key)
    
    # Request reranking from Cohere
    response = co.rerank(
        model=model_name,
        query=query,
        documents=documents,
        top_n=top_n,
    )
    
    # Print the response for debugging
    print(f"Response ID: {response.id}")
    print(f"Top {len(response.results)} results:")
    
    # Print each result with its document text
    for rank, result in enumerate(response.results, 1):
        doc_index = result.index
        relevance_score = result.relevance_score
        doc_text = documents[doc_index]
        
        print(f"Rank {rank}: Document {doc_index} (Score: {relevance_score:.4f})")
        print(f"  Text: {doc_text[:100]}..." if len(doc_text) > 100 else f"  Text: {doc_text}")
    
    return response

@flow(name="document_reranking_flow")
def document_reranking_flow(
    query: Optional[str] = None,
    documents: Optional[List[str]] = None,
    model_name: str = "rerank-v3.5",         # STAYS FIXED
    top_n: int = 3,                          # This parameter is allowed to be altered from the options mentioned
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Flow to rerank documents based on relevance to a query using Cohere's API.
    
    Args:
        query (str, optional): The search query. Defaults to a sample query.
        documents (List[str], optional): List of documents to rerank. Defaults to sample docs.
        model_name (str): Name of the Cohere reranking model to use
        top_n (int): Number of top results to return
        api_key (str, optional): Cohere API key. If None, will use environment variable.
        
    Returns:
        Dict[str, Any]: The complete response from Cohere's API
    """
    # Default sample query if none provided
    if query is None:
        query = "What is the capital of the United States?"
    
    # Default sample documents if none provided
    if documents is None:
        documents = [
            "Carson City is the capital city of the American state of Nevada.",
            "The Commonwealth of the Northern Mariana Islands is a group of islands in the Pacific Ocean. Its capital is Saipan.",
            "Capitalization or capitalisation in English grammar is the use of a capital letter at the start of a word. English usage varies from capitalization in other languages.",
            "Washington, D.C. (also known as simply Washington or D.C., and officially as the District of Columbia) is the capital of the United States. It is a federal district.",
            "Capital punishment has existed in the United States since before the United States was a country. As of 2017, capital punishment is legal in 30 of the 50 states.",
        ]
    
    # Run the reranking task
    response = rerank_documents(
        query=query,
        documents=documents,
        model_name=model_name,
        top_n=top_n,
        api_key=api_key
    )
    
    return response

# Run the flow if executed directly
if __name__ == "__main__":
    result = document_reranking_flow()
    
# Example Response    
# {
#   "results": [
#     {
#       "index": 3,
#       "relevance_score": 0.999071
#     },
#     {
#       "index": 4,
#       "relevance_score": 0.7867867
#     },
#     {
#       "index": 0,
#       "relevance_score": 0.32713068
#     }
#   ],
#   "id": "07734bd2-2473-4f07-94e1-0d9f0e6843cf",
#   "meta": {
#     "api_version": {
#       "version": "2",
#       "is_experimental": false
#     },
#     "billed_units": {
#       "search_units": 1
#     }
#   }
# }
```
### Available parameters to alter
top_n:
- Choose any integer as per the requirements (3 or 5 are most commonly used) 

# OpenAI Embedding
```python
from prefect import task, flow
import os
import openai
import dotenv
from typing import Union, List, Optional, Dict, Any

@task(name="initialize_azure_openai_client")
def initialize_azure_openai_client(
    azure_endpoint: Optional[str] = None,
    api_key: Optional[str] = None,
    api_version: Optional[str] = None,
    load_env: bool = True
) -> openai.AzureOpenAI:
    """
    Initialize the Azure OpenAI client.
    
    Args:
        azure_endpoint (str, optional): Azure OpenAI endpoint.
        api_key (str, optional): Azure OpenAI API key.
        api_version (str, optional): OpenAI API version.
        load_env (bool): Whether to load environment variables from .env file.
        
    Returns:
        openai.AzureOpenAI: Initialized Azure OpenAI client
    """
    # Load environment variables if requested
    if load_env:
        dotenv.load_dotenv()
    
    # Use provided values or get from environment
    azure_endpoint = azure_endpoint or os.environ.get("AZURE_OPENAI_ENDPOINT")
    api_key = api_key or os.environ.get("AZURE_OPENAI_API_KEY")
    api_version = api_version or os.environ.get("OPENAI_API_VERSION")
    
    # Validate required parameters
    if not all([azure_endpoint, api_key, api_version]):
        missing = []
        if not azure_endpoint: missing.append("AZURE_OPENAI_ENDPOINT")
        if not api_key: missing.append("AZURE_OPENAI_API_KEY")
        if not api_version: missing.append("OPENAI_API_VERSION")
        
        raise ValueError(f"Missing required parameters: {', '.join(missing)}")
    
    # Initialize the client
    client = openai.AzureOpenAI(
        azure_endpoint=azure_endpoint,
        api_key=api_key,
        api_version=api_version
    )
    
    return client

@task(name="generate_azure_openai_embeddings")
def generate_azure_openai_embeddings(
    input_text: Union[str, List[str]],
    model_deployment: str,
    client: Optional[openai.AzureOpenAI] = None,
    azure_endpoint: Optional[str] = None,
    api_key: Optional[str] = None,
    api_version: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate embeddings using Azure OpenAI API.
    
    Args:
        input_text (Union[str, List[str]]): Text to generate embeddings for.
        model_deployment (str): Name of the model deployment.
        client (openai.AzureOpenAI, optional): Pre-initialized Azure OpenAI client.
        azure_endpoint (str, optional): Azure OpenAI endpoint.
        api_key (str, optional): Azure OpenAI API key.
        api_version (str, optional): OpenAI API version.
        
    Returns:
        Dict[str, Any]: Response containing the embeddings
    """
    # If no client is provided, initialize one
    if client is None:
        client = initialize_azure_openai_client(
            azure_endpoint=azure_endpoint,
            api_key=api_key,
            api_version=api_version
        )
    
    # Generate embeddings
    response = client.embeddings.create(
        model=model_deployment,
        input=input_text
    )
    
    # Extract and log information about the response
    if hasattr(response, 'data') and len(response.data) > 0:
        first_embedding = response.data[0].embedding
        embedding_dimensions = len(first_embedding)
        print(f"Generated embeddings with {embedding_dimensions} dimensions")
        
        if isinstance(input_text, list):
            print(f"Created embeddings for {len(input_text)} text inputs")
        else:
            # Display part of the input text
            display_text = input_text[:50] + "..." if len(input_text) > 50 else input_text
            print(f"Created embedding for text: '{display_text}'")
    
    return response

@flow(name="azure_openai_embeddings_flow")
def azure_openai_embeddings_flow(
    input_text: Optional[Union[str, List[str]]] = None,
    model_deployment: Optional[str] = None,
    azure_endpoint: Optional[str] = None,
    api_key: Optional[str] = None,
    api_version: Optional[str] = None
) -> Dict[str, Any]:
    """
    Flow to generate embeddings using Azure OpenAI.
    
    Args:
        input_text (Union[str, List[str]], optional): Text to generate embeddings for.
                                                    Defaults to a sample text.
        model_deployment (str, optional): Name of the model deployment. If None,
                                        will use AZURE_OPENAI_DEPLOYMENT from env.
        azure_endpoint (str, optional): Azure OpenAI endpoint.
        api_key (str, optional): Azure OpenAI API key.
        api_version (str, optional): OpenAI API version.
        
    Returns:
        Dict[str, Any]: Response containing the embeddings
    """
    # Load environment variables
    dotenv.load_dotenv()
    
    # Use default sample text if none provided
    if input_text is None:
        input_text = "The food was delicious and the waiter..."
    
    # Get model deployment from environment if not provided
    if model_deployment is None:
        model_deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT")    # This parameter is allowed to be altered from the options mentioned
        if not model_deployment:
            raise ValueError("Model deployment not provided and AZURE_OPENAI_DEPLOYMENT not found in environment")
    
    # Initialize the client
    client = initialize_azure_openai_client(
        azure_endpoint=azure_endpoint,
        api_key=api_key,
        api_version=api_version
    )
    
    # Generate embeddings
    response = generate_azure_openai_embeddings(
        input_text=input_text,
        model_deployment=model_deployment,
        client=client
    )
    
    # Process results to return a clean dictionary
    result = {
        "model": model_deployment,
        "input_text": input_text,
        "embedding_data": response.model_dump()
    }
    
    return result

# Run the flow if executed directly
if __name__ == "__main__":
    result = azure_openai_embeddings_flow()

```
### Available parameters to alter
model_deployment:
- "text-embedding-3-small"
- "text-embedding-3-large"

# Jina AI
## jina-embeddings-v3
```python
from prefect import task, flow
import requests
import json
from typing import List, Dict, Any, Optional

@task(name="generate_jina_embeddings")
def generate_jina_embeddings(
    texts: List[str],
    model: str,
    task_type: str,
    api_key: str
) -> Dict[str, Any]:
    """
    Generate embeddings using Jina AI API.
    
    Args:
        texts (List[str]): List of texts to embed
        model (str): Model name to use for embeddings
        task_type (str): Type of task for embeddings
        api_key (str): Jina AI API key
        
    Returns:
        Dict[str, Any]: Response from Jina AI API
    """
    url = "https://api.jina.ai/v1/embeddings"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "model": model,
        "task": task_type,
        "input": texts
    }
    
    response = requests.post(url, headers=headers, json=data)
    return response.json()

@flow(name="jina_embeddings_flow")
def jina_embeddings_flow(
    texts: Optional[List[str]] = None,
    model: str = "jina-embeddings-v3",      # STAYS FIXED
    task_type: str = None,                  # This parameter is allowed to be altered from the options mentioned
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Flow to generate embeddings using Jina AI.
    
    Args:
        texts (List[str], optional): List of texts to embed
        model (str): Model name to use for embeddings
        task_type (str): Type of task for embeddings
        api_key (str, optional): Jina AI API key
        
    Returns:
        Dict[str, Any]: Response from Jina AI API
    """
    if texts is None:
        texts = [
            "Organic skincare for sensitive skin with aloe vera and chamomile: Imagine the soothing embrace of nature with our organic skincare range, crafted specifically for sensitive skin. Infused with the calming properties of aloe vera and chamomile, each product provides gentle nourishment and protection. Say goodbye to irritation and hello to a glowing, healthy complexion.",
            "Bio-Hautpflege für empfindliche Haut mit Aloe Vera und Kamille: Erleben Sie die wohltuende Wirkung unserer Bio-Hautpflege, speziell für empfindliche Haut entwickelt. Mit den beruhigenden Eigenschaften von Aloe Vera und Kamille pflegen und schützen unsere Produkte Ihre Haut auf natürliche Weise. Verabschieden Sie sich von Hautirritationen und genießen Sie einen strahlenden Teint."
        ]
    
    if api_key is None:
        api_key = "jina_defcddccea21418c9647f248b64a9833utpe1vwRVuqWuZDrTLSd7X2uH3-6"
    
    response = generate_jina_embeddings(
        texts=texts,
        model=model,
        task_type=task_type,
        api_key=api_key
    )
    
    return response

# Run the flow if executed directly
if __name__ == "__main__":
    result = jina_embeddings_flow()

# Response Format
# {
#   "model": "string",                 // The name of the embedding model used (e.g., "jina-embeddings-v3")
#   "object": "string",                // Describes the type of root object (e.g., "list")
#   "usage": {
#     "total_tokens": integer,        // Total number of tokens processed
#     "prompt_tokens": integer        // Tokens that were part of the prompt
#   },
#   "data": [
#     {
#       "object": "string",           // Type of individual data object (e.g., "embedding")
#       "index": integer,             // The index position of this embedding
#       "embedding": [
#         number,                     // Array of floats representing the embedding vector
#         ...
#       ]
#     },
#     ...
#   ]
# }

```
### Available parameters to alter
task_type:
- "retrieval.passage"
- "retrieval.query"
- "text-matching"

## jina-clip-v2
- Embedding as Document
```python
from prefect import task, flow
import requests
from typing import List, Dict, Any, Optional, Union

@task(name="generate_jina_multimodal_embeddings")
def generate_jina_multimodal_embeddings(
    inputs: List[Dict[str, str]],
    model: str,
    api_key: str
) -> Dict[str, Any]:
    """
    Generate multimodal embeddings using Jina AI API.
    
    Args:
        inputs (List[Dict[str, str]]): List of text or image inputs
        model (str): Model name to use for embeddings
        api_key (str): Jina AI API key
        
    Returns:
        Dict[str, Any]: Response from Jina AI API
    """
    url = 'https://api.jina.ai/v1/embeddings'
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    
    data = {
        "model": model,
        "input": inputs
    }
    
    response = requests.post(url, headers=headers, json=data)
    return response.json()

@flow(name="jina_multimodal_embeddings_flow")
def jina_multimodal_embeddings_flow(
    inputs: Optional[List[Dict[str, str]]] = None,
    model: str = "jina-clip-v2",                       # STAYS FIXED
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Flow to generate multimodal embeddings using Jina AI.
    
    Args:
        inputs (List[Dict[str, str]], optional): List of text or image inputs
        model (str): Model name to use for embeddings
        api_key (str, optional): Jina AI API key
        
    Returns:
        Dict[str, Any]: Response from Jina AI API
    """
    if inputs is None:
        inputs = [
            {"text": "A beautiful sunset over the beach"},
            {"text": "浜辺に沈む美しい夕日"},
            {"image": "https://i.ibb.co/nQNGqL0/beach1.jpg"},
            {"image": "https://i.ibb.co/r5w8hG8/beach2.jpg"},
        ]
    
    if api_key is None:
        api_key = "jina_defcddccea21418c9647f248b64a9833utpe1vwRVuqWuZDrTLSd7X2uH3-6"
    
    response = generate_jina_multimodal_embeddings(
        inputs=inputs,
        model=model,
        api_key=api_key
    )
    
    return response

# Run the flow if executed directly
if __name__ == "__main__":
    result = jina_multimodal_embeddings_flow()
    
# Response format
# {
#   "model": "string",                 // Name of the model used (e.g., jina-clip-v2)
#   "object": "string",                // Type of the object (e.g., "list")
#   "usage": {
#     "total_tokens": integer,        // Total number of tokens used
#     "prompt_tokens": integer        // Tokens used for the prompt
#   },
#   "data": [
#     {
#       "object": "string",           // Type of the embedded object (e.g., "embedding")
#       "index": integer,             // Index of the embedding in the batch
#       "embedding": [
#         number,                     // List of float values representing the embedding
#         ...
#       ]
#     },
#     ...
#   ]
# }

```
-  Embedding as Query
```python
from prefect import task, flow
import requests
from typing import List, Dict, Any, Optional

@task(name="generate_jina_retrieval_embeddings")
def generate_jina_retrieval_embeddings(
    inputs: List[Dict[str, str]],
    model: str,
    task_type: str,
    api_key: str
) -> Dict[str, Any]:
    """
    Generate retrieval embeddings using Jina AI API.
    
    Args:
        inputs (List[Dict[str, str]]): List of text or image inputs
        model (str): Model name to use for embeddings
        task_type (str): Type of task for embeddings
        api_key (str): Jina AI API key
        
    Returns:
        Dict[str, Any]: Response from Jina AI API
    """
    url = 'https://api.jina.ai/v1/embeddings'
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "model": model,
        "task": task_type,
        "input": inputs
    }
    
    response = requests.post(url, headers=headers, json=data)
    return response.json()

@flow(name="jina_retrieval_embeddings_flow")
def jina_retrieval_embeddings_flow(
    inputs: Optional[List[Dict[str, str]]] = None,
    model: str = "jina-clip-v2",                            # STAYS FIXED
    task_type: str = "retrieval.query",                     # STAYS FIXED
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Flow to generate retrieval embeddings using Jina AI.
    
    Args:
        inputs (List[Dict[str, str]], optional): List of text or image inputs
        model (str): Model name to use for embeddings
        task_type (str): Type of task for embeddings
        api_key (str, optional): Jina AI API key
        
    Returns:
        Dict[str, Any]: Response from Jina AI API
    """
    if inputs is None:
        inputs = [
            {"text": "A beautiful sunset over the beach"},
            {"text": "浜辺に沈む美しい夕日"},
            {"image": "https://i.ibb.co/nQNGqL0/beach1.jpg"},
            {"image": "https://i.ibb.co/r5w8hG8/beach2.jpg"},
        ]
    
    if api_key is None:
        api_key = "jina_defcddccea21418c9647f248b64a9833utpe1vwRVuqWuZDrTLSd7X2uH3-6"
    
    response = generate_jina_retrieval_embeddings(
        inputs=inputs,
        model=model,
        task_type=task_type,
        api_key=api_key
    )
    
    return response

# Run the flow if executed directly
if __name__ == "__main__":
    result = jina_retrieval_embeddings_flow()
    
# Response format
# {
#   "model": "string",                 // Name of the model used (e.g., jina-clip-v2)
#   "object": "string",                // Type of the object (e.g., "list")
#   "usage": {
#     "total_tokens": integer,        // Total number of tokens used
#     "prompt_tokens": integer        // Tokens used for the prompt
#   },
#   "data": [
#     {
#       "object": "string",           // Type of the embedded object (e.g., "embedding")
#       "index": integer,             // Index of the embedding in the batch
#       "embedding": [
#         number,                     // List of float values representing the embedding
#         ...
#       ]
#     },
#     ...
#   ]
# }
```

## jina-reranker-m0
```python
from prefect import task, flow
import requests
from typing import List, Dict, Any, Optional, Union

@task(name="jina_rerank")
def jina_rerank(
    query: str,
    documents: List[Dict[str, str]],
    model: str,
    top_n: Union[int, str],
    return_documents: bool,
    api_key: str
) -> Dict[str, Any]:
    """
    Rerank documents using Jina AI API.
    
    Args:
        query (str): The query to match against documents
        documents (List[Dict[str, str]]): List of documents to rerank
        model (str): Model name to use for reranking
        top_n (Union[int, str]): Number of top results to return
        return_documents (bool): Whether to include documents in results
        api_key (str): Jina AI API key
        
    Returns:
        Dict[str, Any]: Response from Jina AI API
    """
    url = 'https://api.jina.ai/v1/rerank'
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    
    payload = {
        "model": model,
        "query": query,
        "top_n": top_n,
        "documents": documents,
        "return_documents": return_documents
    }
    
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

@flow(name="jina_rerank_flow")
def jina_rerank_flow(
    query: Optional[str] = None,
    documents: Optional[List[Dict[str, str]]] = None,
    model: str = "jina-reranker-m0",                        # STAYS FIXED
    top_n: Union[int, str] = "3",                           # This parameter is allowed to be altered from the options mentioned 
    return_documents: bool = True,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Flow to rerank documents using Jina AI.
    
    Args:
        query (str, optional): The query to match against documents
        documents (List[Dict[str, str]], optional): List of documents to rerank
        model (str): Model name to use for reranking
        top_n (Union[int, str]): Number of top results to return
        return_documents (bool): Whether to include documents in results
        api_key (str, optional): Jina AI API key
        
    Returns:
        Dict[str, Any]: Response from Jina AI API
    """
    if query is None:
        query = "small language model data extraction"
    
    if documents is None:
        documents = [
            {
                "image": "https://raw.githubusercontent.com/jina-ai/multimodal-reranker-test/main/handelsblatt-preview.png"
            },
            {
                "image": "https://raw.githubusercontent.com/jina-ai/multimodal-reranker-test/main/paper-11.png"
            },
            {
                "text": "We present ReaderLM-v2, a compact 1.5 billion parameter language model designed for efficient web content extraction. Our model processes documents up to 512K tokens, transforming messy HTML into clean Markdown or JSON formats with high accuracy -- making it an ideal tool for grounding large language models. The models effectiveness results from two key innovations: (1) a three-stage data synthesis pipeline that generates high quality, diverse training data by iteratively drafting, refining, and critiquing web content extraction; and (2) a unified training framework combining continuous pre-training with multi-objective optimization. Intensive evaluation demonstrates that ReaderLM-v2 outperforms GPT-4o-2024-08-06 and other larger models by 15-20% on carefully curated benchmarks, particularly excelling at documents exceeding 100K tokens, while maintaining significantly lower computational requirements."
            },
            {
                "text": "数据提取么？为什么不用正则啊，你用正则不就全解决了么？"
            },
        ]
    
    if api_key is None:
        api_key = "jina_defcddccea21418c9647f248b64a9833utpe1vwRVuqWuZDrTLSd7X2uH3-6"
    
    response = jina_rerank(
        query=query,
        documents=documents,
        model=model,
        top_n=top_n,
        return_documents=return_documents,
        api_key=api_key
    )
    
    return response

# Run the flow if executed directly
if __name__ == "__main__":
    result = jina_rerank_flow()

# Example Reponse    
# {
#   "model": "jina-reranker-m0",
#   "usage": {
#     "total_tokens": 2894
#   },
#   "results": [
#     {
#       "index": 1,
#       "document": {
#         "url": "https://raw.githubusercontent.com/jina-ai/multimodal-reranker-test/main/paper-11.png"
#       },
#       "relevance_score": 0.8814517277012487
#     },
#     {
#       "index": 3,
#       "document": {
#         "text": "We present ReaderLM-v2, a compact 1.5 billion parameter language model designed for efficient web content extraction. Our model processes documents up to 512K tokens, transforming messy HTML into clean Markdown or JSON formats with high accuracy -- making it an ideal tool for grounding large language models. The models effectiveness results from two key innovations: (1) a three-stage data synthesis pipeline that generates high quality, diverse training data by iteratively drafting, refining, and critiquing web content extraction; and (2) a unified training framework combining continuous pre-training with multi-objective optimization. Intensive evaluation demonstrates that ReaderLM-v2 outperforms GPT-4o-2024-08-06 and other larger models by 15-20% on carefully curated benchmarks, particularly excelling at documents exceeding 100K tokens, while maintaining significantly lower computational requirements."
#       },
#       "relevance_score": 0.7756727858283531
#     },
#     {
#       "index": 4,
#       "document": {
#         "text": "数据提取么？为什么不用正则啊，你用正则不就全解决了么？"
#       },
#       "relevance_score": 0.6128658982982312
#     }
#   ]
# }

```
### Available parameters to alter
top_n:
- Choose any integer as per the requirements (3 or 5 are most commonly used) 

# Gemini
## gemini-embedding-exp-03-07
```python
from prefect import task, flow
from google import genai
from google.genai import types
from typing import List, Dict, Any, Optional

@task(name="generate_gemini_embeddings")
def generate_gemini_embeddings(
    content: str,
    model: str,
    task_type: str,
    api_key: str
) -> List[float]:
    """
    Generate embeddings using Google Gemini API.
    
    Args:
        content (str): Text content to embed
        model (str): Model name to use for embeddings
        task_type (str): Type of task for embeddings
        api_key (str): Google Gemini API key
        
    Returns:
        List[float]: Generated embeddings
    """
    client = genai.Client(api_key=api_key)
    
    result = client.models.embed_content(
        model=model,
        contents=content,
        config=types.EmbedContentConfig(task_type=task_type)
    )
    
    return result.embeddings

@flow(name="gemini_embeddings_flow")
def gemini_embeddings_flow(
    content: Optional[str] = None,
    model: str = "gemini-embedding-exp-03-07",        # STAYS FIXED
    task_type: str = "SEMANTIC_SIMILARITY",           # This parameter is allowed to be altered from the options mentioned 
    api_key: Optional[str] = None
) -> List[float]:
    """
    Flow to generate embeddings using Google Gemini.
    
    Args:
        content (str, optional): Text content to embed
        model (str): Model name to use for embeddings
        task_type (str): Type of task for embeddings
        api_key (str, optional): Google Gemini API key
        
    Returns:
        List[float]: Generated embeddings
    """
    if content is None:
        content = "What is the meaning of life?"
    
    if api_key is None:
        api_key = "GEMINI_API_KEY"
    
    embeddings = generate_gemini_embeddings(
        content=content,
        model=model,
        task_type=task_type,
        api_key=api_key
    )
    
    return embeddings

# Run the flow if executed directly
if __name__ == "__main__":
    result = gemini_embeddings_flow()
    print(result)
```
### Available parameters to alter
task_type:
- "SEMANTIC_SIMILARITY": Used to generate embeddings that are optimized to assess text similarity.
- "CLASSIFICATION": Used to generate embeddings that are optimized to classify texts according to preset labels.
- "CLUSTERING": Used to generate embeddings that are optimized to cluster texts based on their similarities.
- "RETRIEVAL_DOCUMENT": Used to generate embeddings that are optimized for document search or information retrieval.
- "RETRIEVAL_QUERY": Used to generate embeddings that are optimized for document search or information retrieval.
- "QUESTION_ANSWERING": Used to generate embeddings that are optimized for document search or information retrieval.
- "FACT_VERIFICATION": Used to generate embeddings that are optimized for document search or information retrieval.
- "CODE_RETRIEVAL_QUERY": Used to retrieve a code block based on a natural language query, such as sort an array or reverse a linked list. Embeddings of the code blocks are computed using RETRIEVAL_DOCUMENT.