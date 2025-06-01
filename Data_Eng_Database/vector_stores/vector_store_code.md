```python
import time
from typing import Any, Dict, List, Optional
from uuid import UUID
import os
from openai import AsyncAzureOpenAI
import weaviate
# from fastapi import HTTPException, status
from weaviate.classes.config import Configure
from weaviate.classes.init import Auth
from dotenv import load_dotenv
load_dotenv()

# Global variables to store clients
weaviate_client = None
embeddings_client = None

async def initialize_weaviate():
    """
    Initialize the Weaviate and embeddings clients.
    
    Returns:
        tuple: (weaviate_client, embeddings_client)
    """
    global weaviate_client, embeddings_client
    
    weaviate_api_key = os.getenv("WEAVIATE_API_KEY")
    weaviate_url = os.getenv("WEAVIATE_URL") or "y7wcfexstxwetjucs7gk5q.c0.asia-southeast1.gcp.weaviate.cloud"
    
    # Use WeaviateClient for v4 API
    weaviate_client = weaviate.connect_to_weaviate_cloud(
        cluster_url=weaviate_url,
        auth_credentials=Auth.api_key(weaviate_api_key),
        headers={
            "X-Azure-Api-Key": os.getenv("AZURE_API_KEY"),
            "X-Azure-Deployment-Id": os.getenv("AZURE_DEPLOYMENT"),
            "X-Azure-Resource-Name": os.getenv("AZURE_MODEL"),
        },
    )
    
    if not weaviate_client.is_ready():
        raise Exception("Weaviate client connection failed")

    embeddings_client = AsyncAzureOpenAI(
        azure_deployment=os.getenv("AZURE_EMBEDDING_DEPLOYMENT"),
        azure_endpoint=os.getenv("AZURE_EMBEDDING_ENDPOINT"),
        api_key=os.getenv("AZURE_EMBEDDING_API_KEY"),
        api_version=os.getenv("AZURE_EMBEDDING_API_VERSION"),
    )
    
    return weaviate_client, embeddings_client

async def close_connections():
    """
    Close the Weaviate and embeddings client connections.
    """
    global weaviate_client, embeddings_client
    
    if weaviate_client:
        weaviate_client.close()
    
    if embeddings_client:
        await embeddings_client.close()

def get_collection(collection_name: str):
    """
    Get a collection from Weaviate.
    If the collection does not exist, it will be created.
    """
    global weaviate_client
    
    if weaviate_client.collections.exists(collection_name):
        collection = weaviate_client.collections.get(collection_name)
    else:
        collection = weaviate_client.collections.create(
            collection_name,
            generative_config=Configure.Generative.azure_openai(
                resource_name=os.getenv("AZURE_MODEL"),
                deployment_id=os.getenv("AZURE_DEPLOYMENT"),
                base_url=os.getenv("AZURE_ENDPOINT"),
            ),
        )

    return collection

async def generate_embedding(text):
    """
    Generate an embedding for the given text.
    """
    global embeddings_client
    
    start_time = time.time()
    embedding = await embeddings_client.embeddings.create(
        model="text-embedding-3-small", input=[text]
    )
    end_time = time.time()
    print(f"Embedding Generation Time: {end_time - start_time:.2f} seconds")

    return embedding.data[0].embedding

def add(
    collection_name: str,
    properties: dict[str, Any],
    references: Optional[dict[str, Any]] = None,
):
    """
    Add properties to a collection.
    """
    collection = get_collection(collection_name)
    collection.data.insert(properties, references)

async def query_weaviate(query: str, collection_name: str):
    """
    Query Weaviate for a specific collection.
    """
    try:
        query_embedding = await generate_embedding(query)
        collection = get_collection(collection_name)
        response = collection.query.hybrid(
            query=query, alpha=0.5, vector=query_embedding
        )

        result = [o.properties.get("content") for o in response.objects]
        return result
    except weaviate.exceptions.UnexpectedStatusCodeException as e:
        raise Exception(f"Error querying Weaviate: {e}")

async def add_documents_workflow(collection_name: str, documents: List[Dict[str, Any]]):
    """
    Complete workflow for adding documents to Weaviate.
    
    This function demonstrates the entire process of:
    1. Initializing Weaviate connections
    2. Adding documents to a collection
    3. Closing connections
    
    Args:
        collection_name: The name of the collection to add documents to
        documents: List of dictionaries containing document data
    """
    try:
        print(f"Starting document addition workflow for collection '{collection_name}'...")
        
        # Step 1: Initialize Weaviate and embeddings clients
        await initialize_weaviate()
        print("Successfully connected to Weaviate and embedding services")
        
        # Step 2: Add each document to the collection
        for i, doc in enumerate(documents):
            add(collection_name, doc)
            print(f"Added document {i+1}/{len(documents)}")
            
        print(f"Successfully added {len(documents)} documents to collection '{collection_name}'")
            
    except Exception as e:
        print(f"Error in document addition workflow: {str(e)}")
        raise
    
    finally:
        # Step 3: Always close connections
        await close_connections()
        print("Connections closed")

async def search_documents_workflow(collection_name: str, query: str):
    """
    Complete workflow for searching documents in Weaviate.
    
    This function demonstrates the entire process of:
    1. Initializing Weaviate connections
    2. Generating an embedding for the query
    3. Performing a hybrid search
    4. Processing and returning results
    5. Closing connections
    
    Args:
        collection_name: The name of the collection to search
        query: The search query text
        
    Returns:
        List of search results
    """
    results = None
    
    try:

        
        # Step 1: Initialize Weaviate and embeddings clients
        await initialize_weaviate()
        print("Successfully connected to Weaviate and embedding services")
        
        # Step 2: Generate embedding and perform hybrid search
        print(f"Executing query: '{query}'")
        results = await query_weaviate(query, collection_name)
        print(f"Search returned {len(results)} results")
            
        return results
            
    except Exception as e:
        print(f"Error in search workflow: {str(e)}")
        raise
    
    finally:
        # Step 3: Always close connections
        await close_connections()
        print("Connections closed")

# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def main():
        # Sample documents
        documents = [
            {"content": "The quick brown fox jumps over the lazy dog"},
            {"content": "Machine learning models can help analyze text data"},
            {"content": "Vector databases are optimized for similarity search"}
        ]
        
        # Execute the complete document addition workflow
        await add_documents_workflow(
            collection_name="Documents",
            documents=documents
        )
        
        # Execute the complete search workflow
        results = await search_documents_workflow(
            collection_name="Documents",
            query="machine learning"
        )
        
        # Print results
        if results:
            print("\nSearch Results:")
            for i, content in enumerate(results, 1):
                print(f"{i}. {content}")
    
    # Run the async example
    asyncio.run(main())

```
# PINECONE

```python

from prefect import flow, task
from pinecone import Pinecone
import os
import time

@task(name="initialize_pinecone")
def initialize_pinecone(api_key: str) -> Pinecone:
    """
    Initialize a Pinecone client with the provided API key.
    """
    pc = Pinecone(api_key=api_key)
    return pc

@task(name="create_index")
def create_index(
    pc: Pinecone,
    index_name: str,
    cloud: str = "aws",
    region: str = "us-east-1",
    model: str = "llama-text-embed-v2",
    field_map: dict = {"text": "chunk_text"}
) -> Pinecone.Index:
    """
    Create a dense index with integrated embedding model.
    """
    if not pc.has_index(index_name):
        pc.create_index_for_model(
            name=index_name,
            cloud=cloud,
            region=region,
            embed={"model": model, "field_map": field_map}
        )
        print(f"Index '{index_name}' created successfully")
    else:
        print(f"Index '{index_name}' already exists")
    return pc.Index(index_name)

@task(name="upsert_data")
def upsert_data(
    index: Pinecone.Index,
    namespace: str,
    records: list,
    wait_time: int = 10
) -> dict:
    """
    Upsert data records into the specified namespace.
    """
    index.upsert_records(namespace, records)
    print(f"Upserted {len(records)} records to namespace '{namespace}'")
    print(f"Waiting {wait_time} seconds for indexing to complete...")
    time.sleep(wait_time)
    stats = index.describe_index_stats()
    print("Index stats:")
    print(f"- Total vector count: {stats['total_vector_count']}")
    print(f"- Namespace '{namespace}' vector count: {stats['namespaces'].get(namespace, {{}}).get('vector_count', 0)}")
    return stats

@task(name="semantic_search")
def semantic_search(
    index: Pinecone.Index,
    namespace: str,
    query_text: str,
    top_k: int = 10,
    print_results: bool = True
) -> dict:
    """
    Perform semantic search on the index.
    """
    results = index.search(
        namespace=namespace,
        query={"top_k": top_k, "inputs": {'text': query_text}}
    )
    if print_results:
        print(f"\nSearch results for: '{query_text}'")
        for hit in results['result']['hits']:
            print(
                f"id: {hit['_id']:<5} | score: {round(hit['_score'], 2):<5} | "
                f"category: {hit['fields']['category']:<10} | "
                f"text: {hit['fields']['chunk_text']:<50}"
            )
    return results

@task(name="rerank_results")
def rerank_results(
    index: Pinecone.Index,
    namespace: str,
    query_text: str,
    top_k: int = 10,
    rerank_model: str = "bge-reranker-v2-m3",
    top_n: int = 10,
    rank_fields: list = ["chunk_text"],
    print_results: bool = True
) -> dict:
    """
    Perform semantic search with reranking on the index.
    """
    reranked = index.search(
        namespace=namespace,
        query={"top_k": top_k, "inputs": {'text': query_text}},
        rerank={"model": rerank_model, "top_n": top_n, "rank_fields": rank_fields}
    )
    if print_results:
        print(f"\nReranked results for: '{query_text}'")
        for hit in reranked['result']['hits']:
            print(
                f"id: {hit['_id']:<5} | score: {round(hit['_score'], 2):<5} | "
                f"category: {hit['fields']['category']:<10} | "
                f"text: {hit['fields']['chunk_text']:<50}"
            )
    return reranked

@task(name="delete_index")
def delete_index(pc: Pinecone, index_name: str) -> None:
    """
    Delete an index.
    """
    pc.delete_index(index_name)
    print(f"Index '{index_name}' deleted successfully")

@flow(name="add_documents_flow")
def add_documents_flow(
    api_key: str,
    index_name: str,
    namespace: str,
    documents: list,
    cloud: str = "aws",
    region: str = "us-east-1",
    model: str = "llama-text-embed-v2",
    field_map: dict = {"text": "chunk_text"},
    wait_time: int = 10
) -> dict:
    """
    Complete flow for adding documents to Pinecone.
    """
    pc = initialize_pinecone(api_key)
    index = create_index(pc, index_name, cloud, region, model, field_map)
    stats = upsert_data(index, namespace, documents, wait_time)
    return {"pc": pc, "index": index, "stats": stats}

@flow(name="search_documents_flow")
def search_documents_flow(
    api_key: str,
    index_name: str,
    namespace: str,
    query_text: str,
    top_k: int = 10,
    use_reranking: bool = False,
    rerank_model: str = "bge-reranker-v2-m3",
    top_n: int = 10,
    rank_fields: list = ["chunk_text"]
) -> dict:
    """
    Complete flow for searching documents in Pinecone.
    """
    pc = initialize_pinecone(api_key)
    index = pc.Index(index_name)
    if use_reranking:
        results = rerank_results(index, namespace, query_text, top_k, rerank_model, top_n, rank_fields)
    else:
        results = semantic_search(index, namespace, query_text, top_k)
    return {"pc": pc, "index": index, "results": results}

if __name__ == "__main__":
    # Replace with your actual API key
    API_KEY = "you-api-key" 
    
    # Define index and namespace names
    INDEX_NAME = "quickstart-demo"
    NAMESPACE = "example-namespace"
    
    # Example documents - in a real application, these would come from your data source
    sample_documents = [
        { "_id": "rec1", "chunk_text": "The Eiffel Tower was completed in 1889 and stands in Paris, France.", "category": "history" },
        { "_id": "rec2", "chunk_text": "Photosynthesis allows plants to convert sunlight into energy.", "category": "science" },
        { "_id": "rec3", "chunk_text": "Albert Einstein developed the theory of relativity.", "category": "science" },
        { "_id": "rec4", "chunk_text": "The mitochondrion is often called the powerhouse of the cell.", "category": "biology" },
        { "_id": "rec5", "chunk_text": "Shakespeare wrote many famous plays, including Hamlet and Macbeth.", "category": "literature" },
        { "_id": "rec6", "chunk_text": "Water boils at 100°C under standard atmospheric pressure.", "category": "physics" },
        { "_id": "rec7", "chunk_text": "The Great Wall of China was built to protect against invasions.", "category": "history" },
        { "_id": "rec8", "chunk_text": "Honey never spoils due to its low moisture content and acidity.", "category": "food science" },
        { "_id": "rec9", "chunk_text": "The speed of light in a vacuum is approximately 299,792 km/s.", "category": "physics" },
        { "_id": "rec10", "chunk_text": "Newton's laws describe the motion of objects.", "category": "physics" },
    ]
    
    # Option 1: Add documents to Pinecone
    add_result = add_documents_flow(
        api_key=API_KEY,
        index_name=INDEX_NAME,
        namespace=NAMESPACE,
        documents=sample_documents,
        wait_time=5  # Reduced wait time for testing
    )
    
    # Option 2: Search documents in Pinecone
    print("\nRunning search_documents_flow...")

    search_result = search_documents_flow(
        api_key=API_KEY,
        index_name=INDEX_NAME,
        namespace=NAMESPACE,
        query_text="Famous historical structures and monuments",
        top_k=5
    )
    
    # Option 3: Search with reranking
    print("\nRunning search_documents_flow with reranking...")
    reranked_search_result = search_documents_flow(
        api_key=API_KEY,
        index_name=INDEX_NAME,
        namespace=NAMESPACE,
        query_text="Famous historical structures and monuments",
        top_k=10,
        use_reranking=True,
        top_n=5
    )
    

```

# QDRANT 

```python 

import numpy as np
import uuid
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.models import Distance, VectorParams, PointStruct
from prefect import task, flow

# Optional imports for different embedding methods
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

@task(name="initialize_qdrant")
def initialize_qdrant(url=None, api_key=None, local=False):
    """
    Initialize a Qdrant client with various connection options.
    
    Args:
        url (str, optional): URL to Qdrant server or cloud
        api_key (str, optional): API key for Qdrant cloud
        local (bool): Whether to use local mode
        
    Returns:
        QdrantClient: The initialized Qdrant client
    """
    if local:
        return QdrantClient(path=":memory:")
    else:
        return QdrantClient(url=url, api_key=api_key)

@task(name="create_collection")
def create_collection(client, collection_name, vector_size=1536, distance="cosine"):
    """
    Create a new vector collection in Qdrant.
    
    Args:
        client (QdrantClient): The Qdrant client
        collection_name (str): Name for the new collection
        vector_size (int): Dimensionality of vectors
        distance (str): Distance metric ("cosine", "euclid", or "dot")
        
    Returns:
        bool: True if collection was created
    """
    
    # Check if collection already exists
    collections = client.get_collections().collections
    collection_names = [collection.name for collection in collections]
    
    if collection_name in collection_names:
        print(f"Collection '{collection_name}' already exists")
        return False
    
    # Create collection    
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=vector_size, 
            distance=Distance.COSINE
        )
    )
    
    print(f"Collection '{collection_name}' created successfully")
    return True

@task(name="get_embeddings")
def get_embeddings(text, embedding_type="openai", model=None):
    """
    Get embeddings using various embedding models.
    
    Args:
        text (str or list): Text to embed (string or list of strings)
        embedding_type (str): Type of embedding to use
                             "openai" - OpenAI API (requires API key)
                             "sentence_transformers" - HuggingFace models
                             "fastembed" - Use Qdrant's FastEmbed (handled separately)
        model (str): Model name to use (depends on embedding_type)
                    For openai: "text-embedding-ada-002" etc.
                    For sentence_transformers: "all-MiniLM-L6-v2", "all-mpnet-base-v2", etc.
        
    Returns:
        list or ndarray: Embedding vector
    """
    if isinstance(text, list) and embedding_type != "fastembed":
        return [get_embeddings(t, embedding_type, model) for t in text]
    
    if embedding_type == "openai":
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI package not installed. Install with 'pip install openai'")
        
        model = model or "text-embedding-ada-002"
        response = openai.Embedding.create(
            input=text,
            model=model
        )
        return response['data'][0]['embedding']
    
    elif embedding_type == "sentence_transformers":
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError("Sentence Transformers not installed. Install with 'pip install sentence-transformers'")
        
        model_name = model or "all-MiniLM-L6-v2"  # Default to a good general purpose model
        model = SentenceTransformer(model_name)
        
        # Get embeddings
        embedding = model.encode(text)
        return embedding.tolist() if isinstance(embedding, np.ndarray) else embedding
    
    else:
        raise ValueError(f"Unsupported embedding type: {embedding_type}")

@task(name="setup_fastembed")
def setup_fastembed(client, model_name="BAAI/bge-base-en", gpu=False):
    """
    Set up FastEmbed for the client. This is Qdrant's built-in embedding feature.
    
    Args:
        client (QdrantClient): The Qdrant client
        model_name (str): Name of the embedding model to use
        gpu (bool): Whether to use GPU for embeddings
        
    Returns:
        QdrantClient: The client with FastEmbed configured
    """
    if gpu:
        client.set_model(
            model_name,
            providers=["CUDAExecutionProvider", "CPUExecutionProvider"]
        )
    else:
        client.set_model(model_name)
    
    print(f"FastEmbed initialized with model: {model_name}")
    return client

@task(name="upsert_chunks")
def upsert_chunks(client, collection_name, chunks, embedding_type="openai", embedding_model=None):
    """
    Embed chunks and upsert into Qdrant collection.
    
    Args:
        client (QdrantClient): The Qdrant client
        collection_name (str): Name of the collection
        chunks (list): List of text chunks to embed and store
        embedding_type (str): Type of embedding to use ("openai", "sentence_transformers", or "fastembed")
        embedding_model (str): Model name to use
        
    Returns:
        dict: Operation result
    """
    points = []
    
    if embedding_type == "fastembed":
        # For FastEmbed, we'll let Qdrant handle the embedding
        # First, ensure FastEmbed is set up
        setup_fastembed(client, model_name=embedding_model or "BAAI/bge-base-en")
        
        # For FastEmbed, we'll use the client.add method
        result = client.add(
            collection_name=collection_name,
            documents=chunks,
            metadata=[{"index": i} for i in range(len(chunks))],
            ids=[str(uuid.uuid4()) for _ in range(len(chunks))]
        )
        
        print(f"Added {len(chunks)} chunks to the collection using FastEmbed")
        return result
    
    else:
        # For other embedding types, we'll handle the embedding ourselves
        for chunk in chunks:
            # Generate embedding
            embedding = get_embeddings(chunk, embedding_type=embedding_type, model=embedding_model)
            
            # Create a unique ID
            point_id = str(uuid.uuid4())
            
            # Create point
            points.append(
                PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload={"text": chunk}
                )
            )
        
        # Upsert points
        result = client.upsert(
            collection_name=collection_name,
            points=points,
            wait=True
        )
        
        print(f"Added {len(chunks)} chunks to the collection using {embedding_type}")
        return result

@task(name="semantic_search")
def semantic_search(client, collection_name, query, embedding_type="openai", embedding_model=None, limit=3):
    """
    Perform semantic search on the collection.
    
    Args:
        client (QdrantClient): The Qdrant client
        collection_name (str): Name of the collection
        query (str): Search query
        embedding_type (str): Type of embedding to use ("openai", "sentence_transformers", or "fastembed")
        embedding_model (str): Model name to use
        limit (int): Number of results to return
        
    Returns:
        list: Search results
    """
    if embedding_type == "fastembed":
        # For FastEmbed, we use the client.query method
        search_results = client.search(
            collection_name=collection_name,
            query_text=query,
            limit=limit
        )
    else:
        # Get query embedding
        query_embedding = get_embeddings(query, embedding_type=embedding_type, model=embedding_model)
        
        # Search the collection
        search_results = client.search(
            collection_name=collection_name,
            query_vector=query_embedding,
            limit=limit
        )
    
    return search_results

@flow(name="main")
def main():
    # Cloud Qdrant configuration
    QDRANT_URL = "https://aa97a128-a25f-4bf2-ac0a-e9863ebe178b.us-west-2-0.aws.cloud.qdrant.io:6333"  # Replace with your Qdrant cloud URL
    QDRANT_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.IAgacZmccrWyeZOdeUVI_JGkZ-5IVi8DE6H3PKDvNd0"  # Replace with your Qdrant API key
    
    # Choose your embedding method
    EMBEDDING_TYPE = "sentence_transformers"  # Options: "openai", "sentence_transformers", "fastembed"
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"      # Model name depends on the embedding type
    
    # if EMBEDDING_TYPE == "sentence_transformers":
    #     EMBEDDING_MODEL = "BAAI/bge-base-en"  # Sentence Transformers model

    # OpenAI-specific configuration (only needed if using OpenAI embeddings)
    if EMBEDDING_TYPE == "openai":
        openai.api_key = "your-openai-api-key"  # Replace with your actual API key
        EMBEDDING_MODEL = "text-embedding-ada-002"  # OpenAI model
    
    if EMBEDDING_TYPE == "fastembed":
        EMBEDDING_MODEL = "thenlper/gte-large"  # FastEmbed model

    # Initialize Qdrant client (cloud mode)
    client = initialize_qdrant(url=QDRANT_URL, api_key=QDRANT_API_KEY, local=False)
    print(f"Initialized Qdrant client connected to: {QDRANT_URL}")
    
    # Collection name
    collection_name = "sample-collection8"
    
    # Vector size depends on the embedding model
    vector_size_map = {
        "openai": {
            "text-embedding-ada-002": 1536
        },
        "sentence_transformers": {
            "all-MiniLM-L6-v2": 384,
            "all-mpnet-base-v2": 768,
            "all-distilroberta-v1": 768,
            "paraphrase-multilingual-MiniLM-L12-v2": 768
        },
        "fastembed": {
            "BAAI/bge-base-en": 768,
            "BAAI/bge-small-en": 768,
            "thenlper/gte-large": 768,
        }
    }
    
    vector_size = vector_size_map[EMBEDDING_TYPE].get(EMBEDDING_MODEL, 768)
    
    create_collection(
        client,
        collection_name,
        vector_size=vector_size,
    )
    
    # Sample chunks - replace with your own sample text
    sample_chunks = [
        "The Eiffel Tower was completed in 1889 and stands in Paris, France.",
        "Photosynthesis allows plants to convert sunlight into energy.",
        "Albert Einstein developed the theory of relativity.",
        "The mitochondrion is often called the powerhouse of the cell.",
        "Shakespeare wrote many famous plays, including Hamlet and Macbeth.",
        "Water boils at 100°C under standard atmospheric pressure.",
        "The Great Wall of China was built to protect against invasions.",
        "Honey never spoils due to its low moisture content and acidity.",
        "The speed of light in a vacuum is approximately 299,792 km/s.",
        "Newton's laws describe the motion of objects."
    ]
    
    # Upload chunks to Qdrant
    upsert_chunks(
        client, 
        collection_name, 
        sample_chunks,
        embedding_type=EMBEDDING_TYPE,
        embedding_model=EMBEDDING_MODEL
    )
    
    # Example search query
    query = "Famous historical structures and monuments"
    print(f"\nSearching for: '{query}'")
    
    # Perform search
    results = semantic_search(
        client, 
        collection_name, 
        query,
        embedding_type=EMBEDDING_TYPE,
        embedding_model=EMBEDDING_MODEL
    )
    
    # Display results
    print("\nSearch results:")
    for i, result in enumerate(results):
        print(f"{i+1}. Score: {result.score:.4f}")
        print(f"   Text: {result.payload['text']}")
        print()

if __name__ == "__main__":
    main()

```