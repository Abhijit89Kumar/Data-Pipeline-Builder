# Chunking Strategies Code Implementations

This document contains code implementations for the chunking strategies described in `chunking_strategies.md`. All implementations use the Prefect library for workflow management.

## Table of Contents

1. [Fixed-Size Chunking (with Overlap)](#fixed-size-chunking-with-overlap)
2. [Recursive Chunking (with Overlap and Specialized Splitters)](#recursive-chunking-with-overlap-and-specialized-splitters)
3. [Semantic Chunking](#semantic-chunking)
4. [Smart/Adaptive Chunking](#smartadaptive-chunking)
5. [Sliding-Window Chunking](#sliding-window-chunking)

## Fixed-Size Chunking (with Overlap)

```python
from prefect import task, flow
from typing import List, Dict, Any, Optional
import tiktoken
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@task
def load_document(file_path: str) -> str:
    """Load document content from a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        logger.info(f"Successfully loaded document from {file_path}")
        return content
    except Exception as e:
        logger.error(f"Error loading document: {e}")
        raise

@task
def count_tokens(text: str, encoding_name: str = "cl100k_base") -> int:
    """Count the number of tokens in the text using tiktoken."""
    try:
        encoding = tiktoken.get_encoding(encoding_name)
        tokens = encoding.encode(text)
        return len(tokens)
    except Exception as e:
        logger.error(f"Error counting tokens: {e}")
        # Fallback to approximate counting if tiktoken fails
        return len(text.split()) * 1.3  # Rough approximation

@task
def fixed_size_chunking(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    by_tokens: bool = True,
    encoding_name: str = "cl100k_base"
) -> List[Dict[str, Any]]:
    """Split text into fixed-size chunks with optional overlap.

    Args:
        text: The text to split into chunks
        chunk_size: The size of each chunk (in tokens or characters)
        chunk_overlap: The number of tokens/characters to overlap between chunks
        by_tokens: If True, chunk by tokens; if False, chunk by characters
        encoding_name: The name of the tiktoken encoding to use

    Returns:
        A list of dictionaries, each containing a chunk of text and metadata
    """
    chunks = []

    if by_tokens:
        try:
            encoding = tiktoken.get_encoding(encoding_name)
            tokens = encoding.encode(text)

            # Process by tokens
            i = 0
            while i < len(tokens):
                # Get chunk tokens
                chunk_end = min(i + chunk_size, len(tokens))
                chunk_tokens = tokens[i:chunk_end]

                # Decode back to text
                chunk_text = encoding.decode(chunk_tokens)

                # Create chunk with metadata
                chunk = {
                    "text": chunk_text,
                    "metadata": {
                        "start_idx": i,
                        "end_idx": chunk_end,
                        "token_count": len(chunk_tokens),
                        "chunk_type": "fixed_size_token"
                    }
                }
                chunks.append(chunk)

                # Move to next chunk position, accounting for overlap
                i += max(1, chunk_size - chunk_overlap)

        except Exception as e:
            logger.error(f"Error in token-based chunking: {e}")
            logger.info("Falling back to character-based chunking")
            by_tokens = False

    if not by_tokens:
        # Process by characters
        i = 0
        while i < len(text):
            # Get chunk text
            chunk_end = min(i + chunk_size, len(text))
            chunk_text = text[i:chunk_end]

            # Create chunk with metadata
            chunk = {
                "text": chunk_text,
                "metadata": {
                    "start_idx": i,
                    "end_idx": chunk_end,
                    "char_count": len(chunk_text),
                    "chunk_type": "fixed_size_char"
                }
            }
            chunks.append(chunk)

            # Move to next chunk position, accounting for overlap
            i += max(1, chunk_size - chunk_overlap)

    logger.info(f"Created {len(chunks)} fixed-size chunks")
    return chunks

@flow(name="Fixed-Size Chunking Flow")
def fixed_size_chunking_flow(
    file_path: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    by_tokens: bool = True
) -> List[Dict[str, Any]]:
    """Prefect flow for fixed-size chunking of a document."""
    # Load the document
    document = load_document(file_path)

    # Perform fixed-size chunking
    chunks = fixed_size_chunking(
        text=document,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        by_tokens=by_tokens
    )

    return chunks

# Example usage
if __name__ == "__main__":
    # Example document path
    document_path = "path/to/your/document.txt"

    # Run the flow
    chunks = fixed_size_chunking_flow(
        file_path=document_path,
        chunk_size=1000,  # 1000 tokens per chunk
        chunk_overlap=200,  # 200 tokens overlap
        by_tokens=True  # Chunk by tokens
    )

    # Print the first chunk as an example
    if chunks:
        print(f"First chunk: {chunks[0]['text'][:100]}...")
        print(f"Metadata: {chunks[0]['metadata']}")
        print(f"Total chunks created: {len(chunks)}")
```

This implementation provides a flexible fixed-size chunking strategy with the following features:

- Supports chunking by tokens or characters
- Configurable chunk size and overlap
- Includes metadata with each chunk for tracking
- Uses tiktoken for accurate token counting (with fallback)
- Wrapped in a Prefect flow for easy integration into data pipelines

## Recursive Chunking (with Overlap and Specialized Splitters)

```python
from prefect import task, flow
from typing import List, Dict, Any, Optional, Callable, Tuple
import re
import tiktoken
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@task
def load_document(file_path: str) -> str:
    """Load document content from a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        logger.info(f"Successfully loaded document from {file_path}")
        return content
    except Exception as e:
        logger.error(f"Error loading document: {e}")
        raise

@task
def count_tokens(text: str, encoding_name: str = "cl100k_base") -> int:
    """Count the number of tokens in the text using tiktoken."""
    try:
        encoding = tiktoken.get_encoding(encoding_name)
        tokens = encoding.encode(text)
        return len(tokens)
    except Exception as e:
        logger.error(f"Error counting tokens: {e}")
        # Fallback to approximate counting if tiktoken fails
        return len(text.split()) * 1.3  # Rough approximation

# Define splitter functions for different levels
def split_by_paragraphs(text: str) -> List[str]:
    """Split text by paragraphs (double newlines)."""
    paragraphs = re.split(r'\n\s*\n', text)
    return [p.strip() for p in paragraphs if p.strip()]

def split_by_sentences(text: str) -> List[str]:
    """Split text by sentences."""
    # Simple sentence splitter - can be improved with NLP libraries
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]

def split_by_python_code_blocks(text: str) -> List[str]:
    """Split Python code by logical blocks (functions, classes, etc.)."""
    # This is a simplified version - a real implementation would be more robust
    # Split by function or class definitions
    blocks = re.split(r'(\n\s*def\s+|\n\s*class\s+)', text)

    # Recombine the split markers with the content
    result = []
    i = 0
    while i < len(blocks):
        if i + 1 < len(blocks) and (blocks[i].strip().startswith('def') or blocks[i].strip().startswith('class')):
            result.append(blocks[i] + blocks[i+1])
            i += 2
        else:
            if blocks[i].strip():
                result.append(blocks[i])
            i += 1

    return result

@task
def recursive_chunking(
    text: str,
    max_chunk_size: int = 1000,
    min_chunk_size: int = 100,
    chunk_overlap: int = 200,
    splitter_functions: List[Callable[[str], List[str]]] = None,
    encoding_name: str = "cl100k_base"
) -> List[Dict[str, Any]]:
    """Recursively split text into chunks using a hierarchy of splitters.

    Args:
        text: The text to split into chunks
        max_chunk_size: Maximum size of a chunk (in tokens)
        min_chunk_size: Minimum size of a chunk (in tokens)
        chunk_overlap: The number of tokens to overlap between chunks
        splitter_functions: List of functions to split text at different levels
        encoding_name: The name of the tiktoken encoding to use

    Returns:
        A list of dictionaries, each containing a chunk of text and metadata
    """
    # Default splitter hierarchy if none provided
    if splitter_functions is None:
        splitter_functions = [
            split_by_paragraphs,
            split_by_sentences
        ]

    # Initialize token encoder
    try:
        encoding = tiktoken.get_encoding(encoding_name)
    except Exception as e:
        logger.error(f"Error initializing tokenizer: {e}")
        # Fallback to simple word count approximation
        def count_tokens_fallback(s):
            return len(s.split()) * 1.3  # Rough approximation
        token_counter = count_tokens_fallback
    else:
        def count_tokens_tiktoken(s):
            return len(encoding.encode(s))
        token_counter = count_tokens_tiktoken

    # Recursive function to split text
    def split_recursive(text: str, level: int = 0) -> List[Dict[str, Any]]:
        # Check if we've reached the end of our splitter hierarchy
        if level >= len(splitter_functions) or not text.strip():
            # Base case: create a chunk with the current text
            token_count = token_counter(text)
            return [{
                "text": text,
                "metadata": {
                    "token_count": token_count,
                    "chunk_type": "recursive_base",
                    "splitter_level": level
                }
            }]

        # Split the text using the current level's splitter
        segments = splitter_functions[level](text)

        # If splitting produced only one segment or empty, move to next level
        if len(segments) <= 1:
            return split_recursive(text, level + 1)

        chunks = []
        current_chunk = ""
        current_chunk_tokens = 0

        for segment in segments:
            segment_tokens = token_counter(segment)

            # If a single segment is already too large, recursively split it
            if segment_tokens > max_chunk_size:
                sub_chunks = split_recursive(segment, level + 1)
                chunks.extend(sub_chunks)
                continue

            # If adding this segment would exceed max size, finalize current chunk
            if current_chunk and current_chunk_tokens + segment_tokens > max_chunk_size:
                # Only add the chunk if it meets minimum size
                if current_chunk_tokens >= min_chunk_size:
                    chunks.append({
                        "text": current_chunk,
                        "metadata": {
                            "token_count": current_chunk_tokens,
                            "chunk_type": "recursive_combined",
                            "splitter_level": level
                        }
                    })

                # Start a new chunk, potentially with overlap from previous chunk
                if chunk_overlap > 0 and current_chunk:
                    # Create overlap by taking the end of the previous chunk
                    overlap_text = create_overlap(current_chunk, chunk_overlap, token_counter)
                    current_chunk = overlap_text + segment
                    current_chunk_tokens = token_counter(current_chunk)
                else:
                    current_chunk = segment
                    current_chunk_tokens = segment_tokens
            else:
                # Add a space between segments if needed
                if current_chunk:
                    current_chunk += "\n\n" + segment
                else:
                    current_chunk = segment
                current_chunk_tokens = token_counter(current_chunk)

        # Add the last chunk if it's not empty and meets minimum size
        if current_chunk and current_chunk_tokens >= min_chunk_size:
            chunks.append({
                "text": current_chunk,
                "metadata": {
                    "token_count": current_chunk_tokens,
                    "chunk_type": "recursive_combined",
                    "splitter_level": level
                }
            })
        elif current_chunk:  # If it's too small, try to split at a lower level
            sub_chunks = split_recursive(current_chunk, level + 1)
            chunks.extend(sub_chunks)

        return chunks

    # Helper function to create overlap from the end of a chunk
    def create_overlap(text: str, overlap_tokens: int, token_counter: Callable[[str], int]) -> str:
        # For simplicity, we'll use a rough approximation for overlap
        # A more accurate implementation would use the actual tokenizer
        words = text.split()
        total_tokens = token_counter(text)

        if total_tokens <= overlap_tokens:
            return text

        # Estimate how many words to include for overlap
        approx_words_per_token = len(words) / total_tokens
        overlap_words = int(overlap_tokens * approx_words_per_token)

        # Take the last N words for overlap
        overlap_text = " ".join(words[-overlap_words:])
        return overlap_text

    # Start the recursive chunking process
    chunks = split_recursive(text)
    logger.info(f"Created {len(chunks)} recursive chunks")

    # Add index information to chunks
    for i, chunk in enumerate(chunks):
        chunk["metadata"]["chunk_index"] = i
        chunk["metadata"]["total_chunks"] = len(chunks)

    return chunks

@flow(name="Recursive Chunking Flow")
def recursive_chunking_flow(
    file_path: str,
    max_chunk_size: int = 1000,
    min_chunk_size: int = 100,
    chunk_overlap: int = 200,
    content_type: str = "text"
) -> List[Dict[str, Any]]:
    """Prefect flow for recursive chunking of a document.

    Args:
        file_path: Path to the document file
        max_chunk_size: Maximum size of a chunk (in tokens)
        min_chunk_size: Minimum size of a chunk (in tokens)
        chunk_overlap: The number of tokens to overlap between chunks
        content_type: Type of content ('text', 'python', etc.) to determine splitters
    """
    # Load the document
    document = load_document(file_path)

    # Select appropriate splitters based on content type
    if content_type.lower() == "python":
        splitters = [
            split_by_paragraphs,
            split_by_python_code_blocks,
            split_by_sentences
        ]
    else:  # Default text splitters
        splitters = [
            split_by_paragraphs,
            split_by_sentences
        ]

    # Perform recursive chunking
    chunks = recursive_chunking(
        text=document,
        max_chunk_size=max_chunk_size,
        min_chunk_size=min_chunk_size,
        chunk_overlap=chunk_overlap,
        splitter_functions=splitters
    )

    return chunks

# Example usage
if __name__ == "__main__":
    # Example document path
    document_path = "path/to/your/document.txt"

    # Run the flow for a Python file
    chunks = recursive_chunking_flow(
        file_path=document_path,
        max_chunk_size=1000,
        min_chunk_size=100,
        chunk_overlap=200,
        content_type="python"  # Specify content type for specialized splitters
    )

    # Print the first chunk as an example
    if chunks:
        print(f"First chunk: {chunks[0]['text'][:100]}...")
        print(f"Metadata: {chunks[0]['metadata']}")
        print(f"Total chunks created: {len(chunks)}")
```

This implementation provides a recursive chunking strategy with the following features:

- Hierarchical splitting using different levels of text segmentation
- Specialized splitters for different content types (e.g., Python code)
- Configurable maximum and minimum chunk sizes
- Overlap between chunks to maintain context
- Metadata tracking for each chunk
- Wrapped in a Prefect flow for easy integration into data pipelines

## Semantic Chunking

```python
from prefect import task, flow
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import tiktoken
import logging

# For semantic chunking, we'll need a way to compute embeddings
# This is a dummy implementation - in a real scenario, you would use a proper embedding model
# like OpenAI's text-embedding-ada-002, HuggingFace models, or other embedding services

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@task
def load_document(file_path: str) -> str:
    """Load document content from a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        logger.info(f"Successfully loaded document from {file_path}")
        return content
    except Exception as e:
        logger.error(f"Error loading document: {e}")
        raise

@task
def count_tokens(text: str, encoding_name: str = "cl100k_base") -> int:
    """Count the number of tokens in the text using tiktoken."""
    try:
        encoding = tiktoken.get_encoding(encoding_name)
        tokens = encoding.encode(text)
        return len(tokens)
    except Exception as e:
        logger.error(f"Error counting tokens: {e}")
        # Fallback to approximate counting if tiktoken fails
        return len(text.split()) * 1.3  # Rough approximation

@task
def get_embeddings(texts: List[str], model: str = "dummy-embedding-model") -> List[np.ndarray]:
    """Get embeddings for a list of texts.

    This is a dummy implementation that returns random embeddings.
    In a real scenario, you would use a proper embedding model or API.

    Args:
        texts: List of text strings to embed
        model: Name of the embedding model to use

    Returns:
        List of embedding vectors
    """
    logger.info(f"Getting embeddings for {len(texts)} texts using {model}")

    # In a real implementation, you would call an embedding API or model here
    # For example, with OpenAI:
    # response = openai.Embedding.create(input=texts, model=model)
    # embeddings = [np.array(item["embedding"]) for item in response["data"]]

    # Dummy implementation - returns random embeddings of dimension 384
    embedding_dim = 384
    embeddings = []

    for text in texts:
        # Create a deterministic but random-looking embedding based on the text content
        # This is just for demonstration - not for actual use
        seed = sum(ord(c) for c in text[:100])  # Simple hash of the text
        np.random.seed(seed)
        embedding = np.random.randn(embedding_dim)
        # Normalize the embedding to unit length
        embedding = embedding / np.linalg.norm(embedding)
        embeddings.append(embedding)

    return embeddings

@task
def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """Compute cosine similarity between two vectors."""
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

@task
def split_text_into_sentences(text: str) -> List[str]:
    """Split text into sentences using simple rules.

    In a real implementation, you might use a more sophisticated NLP library.
    """
    import re
    # Simple sentence splitting - can be improved with NLP libraries
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]

@task
def semantic_chunking(
    text: str,
    max_chunk_size: int = 1000,
    min_chunk_size: int = 50,
    similarity_threshold: float = 0.7,
    encoding_name: str = "cl100k_base"
) -> List[Dict[str, Any]]:
    """Split text into chunks based on semantic similarity.

    Args:
        text: The text to split into chunks
        max_chunk_size: Maximum size of a chunk (in tokens)
        min_chunk_size: Minimum size of a chunk (in tokens)
        similarity_threshold: Threshold for determining semantic similarity
        encoding_name: The name of the tiktoken encoding to use

    Returns:
        A list of dictionaries, each containing a chunk of text and metadata
    """
    # Initialize token counter
    try:
        encoding = tiktoken.get_encoding(encoding_name)
        def token_counter(s):
            return len(encoding.encode(s))
    except Exception as e:
        logger.error(f"Error initializing tokenizer: {e}")
        # Fallback to simple word count approximation
        def token_counter(s):
            return len(s.split()) * 1.3  # Rough approximation

    # Split text into sentences
    sentences = split_text_into_sentences(text)
    logger.info(f"Split text into {len(sentences)} sentences")

    if not sentences:
        return []

    # Get embeddings for all sentences
    sentence_embeddings = get_embeddings(sentences)

    # Initialize chunks
    chunks = []
    current_chunk_sentences = [sentences[0]]
    current_chunk_embedding = sentence_embeddings[0].copy()
    current_chunk_tokens = token_counter(sentences[0])

    # Process sentences to form semantically coherent chunks
    for i in range(1, len(sentences)):
        sentence = sentences[i]
        sentence_embedding = sentence_embeddings[i]
        sentence_tokens = token_counter(sentence)

        # Check if adding this sentence would exceed max token limit
        if current_chunk_tokens + sentence_tokens > max_chunk_size:
            # Finalize current chunk
            chunk_text = " ".join(current_chunk_sentences)
            chunks.append({
                "text": chunk_text,
                "metadata": {
                    "token_count": current_chunk_tokens,
                    "sentence_count": len(current_chunk_sentences),
                    "chunk_type": "semantic"
                }
            })

            # Start a new chunk with this sentence
            current_chunk_sentences = [sentence]
            current_chunk_embedding = sentence_embedding.copy()
            current_chunk_tokens = sentence_tokens
            continue

        # Compute similarity between current sentence and current chunk
        # For the chunk embedding, we use a simple average of sentence embeddings
        # In a real implementation, you might use a more sophisticated approach
        avg_chunk_embedding = current_chunk_embedding / len(current_chunk_sentences)
        similarity = cosine_similarity(avg_chunk_embedding, sentence_embedding)

        # If similarity is above threshold, add to current chunk
        if similarity >= similarity_threshold:
            current_chunk_sentences.append(sentence)
            current_chunk_embedding += sentence_embedding
            current_chunk_tokens += sentence_tokens
        else:
            # If current chunk is too small, add this sentence anyway
            if current_chunk_tokens < min_chunk_size:
                current_chunk_sentences.append(sentence)
                current_chunk_embedding += sentence_embedding
                current_chunk_tokens += sentence_tokens
            else:
                # Finalize current chunk and start a new one
                chunk_text = " ".join(current_chunk_sentences)
                chunks.append({
                    "text": chunk_text,
                    "metadata": {
                        "token_count": current_chunk_tokens,
                        "sentence_count": len(current_chunk_sentences),
                        "chunk_type": "semantic"
                    }
                })

                # Start a new chunk with this sentence
                current_chunk_sentences = [sentence]
                current_chunk_embedding = sentence_embedding.copy()
                current_chunk_tokens = sentence_tokens

    # Add the last chunk if it's not empty
    if current_chunk_sentences:
        chunk_text = " ".join(current_chunk_sentences)
        chunks.append({
            "text": chunk_text,
            "metadata": {
                "token_count": current_chunk_tokens,
                "sentence_count": len(current_chunk_sentences),
                "chunk_type": "semantic"
            }
        })

    # Add index information to chunks
    for i, chunk in enumerate(chunks):
        chunk["metadata"]["chunk_index"] = i
        chunk["metadata"]["total_chunks"] = len(chunks)

    logger.info(f"Created {len(chunks)} semantic chunks")
    return chunks

@flow(name="Semantic Chunking Flow")
def semantic_chunking_flow(
    file_path: str,
    max_chunk_size: int = 1000,
    min_chunk_size: int = 50,
    similarity_threshold: float = 0.7
) -> List[Dict[str, Any]]:
    """Prefect flow for semantic chunking of a document.

    Args:
        file_path: Path to the document file
        max_chunk_size: Maximum size of a chunk (in tokens)
        min_chunk_size: Minimum size of a chunk (in tokens)
        similarity_threshold: Threshold for determining semantic similarity
    """
    # Load the document
    document = load_document(file_path)

    # Perform semantic chunking
    chunks = semantic_chunking(
        text=document,
        max_chunk_size=max_chunk_size,
        min_chunk_size=min_chunk_size,
        similarity_threshold=similarity_threshold
    )

    return chunks

# Example usage
if __name__ == "__main__":
    # Example document path
    document_path = "path/to/your/document.txt"

    # Run the flow
    chunks = semantic_chunking_flow(
        file_path=document_path,
        max_chunk_size=1000,
        min_chunk_size=50,
        similarity_threshold=0.7
    )

    # Print the first chunk as an example
    if chunks:
        print(f"First chunk: {chunks[0]['text'][:100]}...")
        print(f"Metadata: {chunks[0]['metadata']}")
        print(f"Total chunks created: {len(chunks)}")
```

This implementation provides a semantic chunking strategy with the following features:

- Uses embeddings to detect semantic similarity between sentences
- Groups semantically related sentences into coherent chunks
- Respects maximum and minimum chunk size constraints
- Includes a configurable similarity threshold
- Provides detailed metadata for each chunk
- Uses a dummy embedding model (replace with a real one in production)
- Wrapped in a Prefect flow for easy integration into data pipelines

## Smart/Adaptive Chunking

```python
from prefect import task, flow
from typing import List, Dict, Any, Optional, Tuple, Callable
import re
import tiktoken
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@task
def load_document(file_path: str) -> str:
    """Load document content from a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        logger.info(f"Successfully loaded document from {file_path}")
        return content
    except Exception as e:
        logger.error(f"Error loading document: {e}")
        raise

@task
def count_tokens(text: str, encoding_name: str = "cl100k_base") -> int:
    """Count the number of tokens in the text using tiktoken."""
    try:
        encoding = tiktoken.get_encoding(encoding_name)
        tokens = encoding.encode(text)
        return len(tokens)
    except Exception as e:
        logger.error(f"Error counting tokens: {e}")
        # Fallback to approximate counting if tiktoken fails
        return len(text.split()) * 1.3  # Rough approximation

# Helper functions for different types of splitting
def split_by_headings(text: str, heading_pattern: str = r'^#{1,6}\s+.+$', min_heading_length: int = 3) -> List[Dict[str, Any]]:
    """Split text by Markdown headings.

    Args:
        text: The text to split
        heading_pattern: Regex pattern to identify headings
        min_heading_length: Minimum length of heading text to be considered valid

    Returns:
        List of dictionaries with heading and content
    """
    # Find all headings and their positions
    heading_matches = list(re.finditer(heading_pattern, text, re.MULTILINE))

    if not heading_matches:
        return [{
            "heading": "",
            "content": text,
            "level": 0
        }]

    sections = []

    # Process each heading and its content
    for i, match in enumerate(heading_matches):
        heading = match.group(0).strip()
        heading_level = len(re.match(r'^(#+)', heading).group(1))  # Count # symbols for level
        heading_text = re.sub(r'^#+\s+', '', heading)  # Remove # symbols from heading text

        # Skip headings that are too short (likely false positives)
        if len(heading_text) < min_heading_length:
            continue

        # Get the content for this section (until the next heading or end of text)
        start_pos = match.end()
        end_pos = heading_matches[i+1].start() if i < len(heading_matches) - 1 else len(text)
        content = text[start_pos:end_pos].strip()

        sections.append({
            "heading": heading_text,
            "content": content,
            "level": heading_level
        })

    # If there's content before the first heading, add it as an intro section
    if heading_matches[0].start() > 0:
        intro_content = text[:heading_matches[0].start()].strip()
        if intro_content:
            sections.insert(0, {
                "heading": "Introduction",
                "content": intro_content,
                "level": 0
            })

    return sections

def split_by_structure(text: str, structure_type: str = "markdown") -> List[Dict[str, Any]]:
    """Split text based on document structure.

    Args:
        text: The text to split
        structure_type: Type of document structure (markdown, html, etc.)

    Returns:
        List of sections with metadata
    """
    if structure_type.lower() == "markdown":
        return split_by_headings(text)
    else:
        # Default to simple paragraph splitting if structure type is not recognized
        paragraphs = re.split(r'\n\s*\n', text)
        return [{
            "heading": "",
            "content": p.strip(),
            "level": 0
        } for p in paragraphs if p.strip()]

def estimate_complexity(text: str) -> float:
    """Estimate the complexity of text based on simple heuristics.

    Higher values indicate more complex text that might need smaller chunks.

    Args:
        text: The text to analyze

    Returns:
        A complexity score between 0 and 1
    """
    # This is a simplified complexity estimation
    # In a real implementation, you might use more sophisticated metrics

    # Count sentences, words, and average word length
    sentences = re.split(r'[.!?]\s+', text)
    words = text.split()

    if not words:
        return 0.0

    avg_word_length = sum(len(word) for word in words) / len(words)
    avg_sentence_length = len(words) / max(1, len(sentences))

    # Normalize metrics to 0-1 range (these thresholds are arbitrary)
    normalized_word_length = min(1.0, avg_word_length / 10.0)  # Assume max avg word length is 10
    normalized_sentence_length = min(1.0, avg_sentence_length / 30.0)  # Assume max avg sentence length is 30

    # Calculate complexity score (equal weighting)
    complexity = (normalized_word_length + normalized_sentence_length) / 2.0

    return complexity

@task
def smart_adaptive_chunking(
    text: str,
    base_chunk_size: int = 1000,
    min_chunk_size: int = 100,
    max_chunk_size: int = 2000,
    chunk_overlap: int = 200,
    structure_type: str = "markdown",
    encoding_name: str = "cl100k_base"
) -> List[Dict[str, Any]]:
    """Adaptively split text into chunks based on structure and content complexity.

    Args:
        text: The text to split into chunks
        base_chunk_size: Base size of a chunk (in tokens)
        min_chunk_size: Minimum size of a chunk (in tokens)
        max_chunk_size: Maximum size of a chunk (in tokens)
        chunk_overlap: The number of tokens to overlap between chunks
        structure_type: Type of document structure (markdown, html, etc.)
        encoding_name: The name of the tiktoken encoding to use

    Returns:
        A list of dictionaries, each containing a chunk of text and metadata
    """
    # Initialize token counter
    try:
        encoding = tiktoken.get_encoding(encoding_name)
        def token_counter(s):
            return len(encoding.encode(s))
    except Exception as e:
        logger.error(f"Error initializing tokenizer: {e}")
        # Fallback to simple word count approximation
        def token_counter(s):
            return len(s.split()) * 1.3  # Rough approximation

    # Split text based on document structure
    sections = split_by_structure(text, structure_type)
    logger.info(f"Split document into {len(sections)} structural sections")

    chunks = []
    current_chunk_text = ""
    current_chunk_tokens = 0
    current_chunk_sections = []

    for section in sections:
        section_text = section["content"]
        section_heading = section["heading"]
        section_level = section["level"]

        # Skip empty sections
        if not section_text.strip():
            continue

        # Estimate section complexity to adjust chunk size
        complexity = estimate_complexity(section_text)

        # Adjust target chunk size based on complexity
        # More complex content gets smaller chunks
        adjusted_chunk_size = int(base_chunk_size * (1.0 - 0.5 * complexity))
        adjusted_chunk_size = max(min_chunk_size, min(max_chunk_size, adjusted_chunk_size))

        section_tokens = token_counter(section_text)

        # If section is too large, split it further
        if section_tokens > adjusted_chunk_size:
            # Finalize current chunk if not empty
            if current_chunk_text:
                chunks.append({
                    "text": current_chunk_text,
                    "metadata": {
                        "token_count": current_chunk_tokens,
                        "sections": current_chunk_sections,
                        "chunk_type": "adaptive"
                    }
                })
                current_chunk_text = ""
                current_chunk_tokens = 0
                current_chunk_sections = []

            # Split large section into paragraphs
            paragraphs = re.split(r'\n\s*\n', section_text)

            # Process each paragraph
            para_chunk_text = ""
            para_chunk_tokens = 0
            para_chunk_sections = []

            for para in paragraphs:
                para_tokens = token_counter(para)

                # If adding this paragraph would exceed the adjusted chunk size
                if para_chunk_tokens + para_tokens > adjusted_chunk_size and para_chunk_text:
                    # Add section heading to the chunk if it's the first paragraph
                    full_chunk_text = para_chunk_text
                    if section_heading and para_chunk_sections == []:
                        full_chunk_text = f"# {section_heading}\n\n{full_chunk_text}"

                    chunks.append({
                        "text": full_chunk_text,
                        "metadata": {
                            "token_count": para_chunk_tokens,
                            "sections": para_chunk_sections + [section_heading],
                            "chunk_type": "adaptive_paragraph"
                        }
                    })

                    # Start a new paragraph chunk
                    para_chunk_text = para
                    para_chunk_tokens = para_tokens
                    para_chunk_sections = []
                else:
                    # Add paragraph to current chunk
                    if para_chunk_text:
                        para_chunk_text += "\n\n" + para
                    else:
                        para_chunk_text = para
                    para_chunk_tokens += para_tokens

            # Add the last paragraph chunk if not empty
            if para_chunk_text:
                # Add section heading to the chunk if it's the first paragraph
                full_chunk_text = para_chunk_text
                if section_heading and para_chunk_sections == []:
                    full_chunk_text = f"# {section_heading}\n\n{full_chunk_text}"

                chunks.append({
                    "text": full_chunk_text,
                    "metadata": {
                        "token_count": para_chunk_tokens,
                        "sections": para_chunk_sections + [section_heading],
                        "chunk_type": "adaptive_paragraph"
                    }
                })
        else:
            # If adding this section would exceed the max chunk size
            if current_chunk_tokens + section_tokens > max_chunk_size and current_chunk_text:
                # Finalize current chunk
                chunks.append({
                    "text": current_chunk_text,
                    "metadata": {
                        "token_count": current_chunk_tokens,
                        "sections": current_chunk_sections,
                        "chunk_type": "adaptive"
                    }
                })

                # Start a new chunk with this section
                current_chunk_text = f"# {section_heading}\n\n{section_text}" if section_heading else section_text
                current_chunk_tokens = section_tokens
                current_chunk_sections = [section_heading] if section_heading else []
            else:
                # Add section to current chunk
                if current_chunk_text:
                    section_with_heading = f"# {section_heading}\n\n{section_text}" if section_heading else section_text
                    current_chunk_text += "\n\n" + section_with_heading
                else:
                    current_chunk_text = f"# {section_heading}\n\n{section_text}" if section_heading else section_text

                current_chunk_tokens += section_tokens
                if section_heading:
                    current_chunk_sections.append(section_heading)

    # Add the last chunk if not empty
    if current_chunk_text:
        chunks.append({
            "text": current_chunk_text,
            "metadata": {
                "token_count": current_chunk_tokens,
                "sections": current_chunk_sections,
                "chunk_type": "adaptive"
            }
        })

    # Add overlap between chunks if specified
    if chunk_overlap > 0 and len(chunks) > 1:
        chunks_with_overlap = [chunks[0]]

        for i in range(1, len(chunks)):
            prev_chunk = chunks[i-1]["text"]
            current_chunk = chunks[i]["text"]

            # Create overlap by taking the end of the previous chunk
            overlap_text = create_overlap(prev_chunk, chunk_overlap, token_counter)

            # Add overlap to the beginning of the current chunk
            if overlap_text:
                new_text = overlap_text + "\n\n" + current_chunk
                new_tokens = token_counter(new_text)

                chunks[i]["text"] = new_text
                chunks[i]["metadata"]["token_count"] = new_tokens
                chunks[i]["metadata"]["has_overlap"] = True
                chunks[i]["metadata"]["overlap_tokens"] = token_counter(overlap_text)

            chunks_with_overlap.append(chunks[i])

        chunks = chunks_with_overlap

    # Add index information to chunks
    for i, chunk in enumerate(chunks):
        chunk["metadata"]["chunk_index"] = i
        chunk["metadata"]["total_chunks"] = len(chunks)

    logger.info(f"Created {len(chunks)} adaptive chunks")
    return chunks

# Helper function to create overlap from the end of a chunk
def create_overlap(text: str, overlap_tokens: int, token_counter: Callable[[str], int]) -> str:
    """Create an overlap text from the end of a chunk."""
    # For simplicity, we'll use a rough approximation for overlap
    # A more accurate implementation would use the actual tokenizer
    words = text.split()
    total_tokens = token_counter(text)

    if total_tokens <= overlap_tokens:
        return text

    # Estimate how many words to include for overlap
    approx_words_per_token = len(words) / total_tokens
    overlap_words = int(overlap_tokens * approx_words_per_token)

    # Take the last N words for overlap
    overlap_text = " ".join(words[-overlap_words:])
    return overlap_text

@flow(name="Smart Adaptive Chunking Flow")
def smart_adaptive_chunking_flow(
    file_path: str,
    base_chunk_size: int = 1000,
    min_chunk_size: int = 100,
    max_chunk_size: int = 2000,
    chunk_overlap: int = 200,
    structure_type: str = "markdown"
) -> List[Dict[str, Any]]:
    """Prefect flow for smart adaptive chunking of a document.

    Args:
        file_path: Path to the document file
        base_chunk_size: Base size of a chunk (in tokens)
        min_chunk_size: Minimum size of a chunk (in tokens)
        max_chunk_size: Maximum size of a chunk (in tokens)
        chunk_overlap: The number of tokens to overlap between chunks
        structure_type: Type of document structure (markdown, html, etc.)
    """
    # Load the document
    document = load_document(file_path)

    # Perform smart adaptive chunking
    chunks = smart_adaptive_chunking(
        text=document,
        base_chunk_size=base_chunk_size,
        min_chunk_size=min_chunk_size,
        max_chunk_size=max_chunk_size,
        chunk_overlap=chunk_overlap,
        structure_type=structure_type
    )

    return chunks

# Example usage
if __name__ == "__main__":
    # Example document path
    document_path = "path/to/your/document.md"

    # Run the flow
    chunks = smart_adaptive_chunking_flow(
        file_path=document_path,
        base_chunk_size=1000,
        min_chunk_size=100,
        max_chunk_size=2000,
        chunk_overlap=200,
        structure_type="markdown"  # Specify document structure type
    )

    # Print the first chunk as an example
    if chunks:
        print(f"First chunk: {chunks[0]['text'][:100]}...")
        print(f"Metadata: {chunks[0]['metadata']}")
        print(f"Total chunks created: {len(chunks)}")
```

This implementation provides a smart/adaptive chunking strategy with the following features:

- Adapts chunk boundaries based on document structure (headings, sections)
- Adjusts chunk size based on content complexity
- Respects minimum and maximum chunk size constraints
- Preserves document structure in the chunks
- Provides overlap between chunks for context continuity
- Includes detailed metadata about sections in each chunk
- Wrapped in a Prefect flow for easy integration into data pipelines

## Sliding-Window Chunking

```python
from prefect import task, flow
from typing import List, Dict, Any, Optional
import tiktoken
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@task
def load_document(file_path: str) -> str:
    """Load document content from a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        logger.info(f"Successfully loaded document from {file_path}")
        return content
    except Exception as e:
        logger.error(f"Error loading document: {e}")
        raise

@task
def count_tokens(text: str, encoding_name: str = "cl100k_base") -> int:
    """Count the number of tokens in the text using tiktoken."""
    try:
        encoding = tiktoken.get_encoding(encoding_name)
        tokens = encoding.encode(text)
        return len(tokens)
    except Exception as e:
        logger.error(f"Error counting tokens: {e}")
        # Fallback to approximate counting if tiktoken fails
        return len(text.split()) * 1.3  # Rough approximation

@task
def sliding_window_chunking(
    text: str,
    window_size: int = 1000,
    window_overlap: int = 500,
    by_tokens: bool = True,
    encoding_name: str = "cl100k_base"
) -> List[Dict[str, Any]]:
    """Split text using a sliding window approach with significant overlap.

    Args:
        text: The text to split into chunks
        window_size: The size of each window/chunk (in tokens or characters)
        window_overlap: The number of tokens/characters to overlap between windows
        by_tokens: If True, chunk by tokens; if False, chunk by characters
        encoding_name: The name of the tiktoken encoding to use

    Returns:
        A list of dictionaries, each containing a chunk of text and metadata
    """
    # Validate parameters
    if window_overlap >= window_size:
        logger.warning("Overlap size is greater than or equal to window size. Adjusting to 50% overlap.")
        window_overlap = window_size // 2

    chunks = []

    if by_tokens:
        try:
            encoding = tiktoken.get_encoding(encoding_name)
            tokens = encoding.encode(text)

            # Process by tokens
            i = 0
            while i < len(tokens):
                # Get window tokens
                window_end = min(i + window_size, len(tokens))
                window_tokens = tokens[i:window_end]

                # Decode back to text
                window_text = encoding.decode(window_tokens)

                # Create chunk with metadata
                chunk = {
                    "text": window_text,
                    "metadata": {
                        "start_idx": i,
                        "end_idx": window_end,
                        "token_count": len(window_tokens),
                        "chunk_type": "sliding_window_token"
                    }
                }
                chunks.append(chunk)

                # Move to next window position, accounting for overlap
                stride = window_size - window_overlap
                i += max(1, stride)  # Ensure we always move forward at least 1 token

        except Exception as e:
            logger.error(f"Error in token-based chunking: {e}")
            logger.info("Falling back to character-based chunking")
            by_tokens = False

    if not by_tokens:
        # Process by characters
        i = 0
        while i < len(text):
            # Get window text
            window_end = min(i + window_size, len(text))
            window_text = text[i:window_end]

            # Create chunk with metadata
            chunk = {
                "text": window_text,
                "metadata": {
                    "start_idx": i,
                    "end_idx": window_end,
                    "char_count": len(window_text),
                    "chunk_type": "sliding_window_char"
                }
            }
            chunks.append(chunk)

            # Move to next window position, accounting for overlap
            stride = window_size - window_overlap
            i += max(1, stride)  # Ensure we always move forward at least 1 character

    # Add index information to chunks
    for i, chunk in enumerate(chunks):
        chunk["metadata"]["chunk_index"] = i
        chunk["metadata"]["total_chunks"] = len(chunks)

        # Calculate overlap with previous and next chunks
        if i > 0:
            prev_end = chunks[i-1]["metadata"]["end_idx"]
            curr_start = chunk["metadata"]["start_idx"]
            overlap_with_prev = prev_end - curr_start
            chunk["metadata"]["overlap_with_prev"] = max(0, overlap_with_prev)

        if i < len(chunks) - 1:
            curr_end = chunk["metadata"]["end_idx"]
            next_start = chunks[i+1]["metadata"]["start_idx"]
            overlap_with_next = curr_end - next_start
            chunk["metadata"]["overlap_with_next"] = max(0, overlap_with_next)

    logger.info(f"Created {len(chunks)} sliding window chunks with {window_overlap} overlap")
    return chunks

@task
def optimize_window_parameters(
    text: str,
    target_chunk_count: int = 10,
    min_window_size: int = 500,
    max_window_size: int = 2000,
    min_overlap_ratio: float = 0.2,
    max_overlap_ratio: float = 0.8,
    encoding_name: str = "cl100k_base"
) -> Dict[str, int]:
    """Optimize window size and overlap to achieve a target number of chunks.

    Args:
        text: The text to analyze
        target_chunk_count: Desired number of chunks
        min_window_size: Minimum window size to consider
        max_window_size: Maximum window size to consider
        min_overlap_ratio: Minimum overlap as a ratio of window size
        max_overlap_ratio: Maximum overlap as a ratio of window size
        encoding_name: The name of the tiktoken encoding to use

    Returns:
        Dictionary with optimized window_size and window_overlap
    """
    # Get total token count
    try:
        encoding = tiktoken.get_encoding(encoding_name)
        total_tokens = len(encoding.encode(text))
    except Exception as e:
        logger.error(f"Error counting tokens: {e}")
        # Fallback to approximate counting
        total_tokens = len(text.split()) * 1.3  # Rough approximation

    # Start with a reasonable window size
    window_size = min(max_window_size, max(min_window_size, total_tokens // target_chunk_count))

    # Calculate overlap to achieve target chunk count
    # Formula: chunk_count = (total_tokens - window_size) / stride + 1
    # where stride = window_size - overlap
    # Solving for overlap: overlap = window_size - (total_tokens - window_size) / (target_chunk_count - 1)

    if target_chunk_count <= 1:
        # If only one chunk is desired, use the entire text
        return {"window_size": total_tokens, "window_overlap": 0}

    overlap = window_size - (total_tokens - window_size) / (target_chunk_count - 1)

    # Ensure overlap is within bounds
    min_overlap = int(window_size * min_overlap_ratio)
    max_overlap = int(window_size * max_overlap_ratio)

    overlap = max(min_overlap, min(max_overlap, int(overlap)))

    logger.info(f"Optimized parameters: window_size={window_size}, window_overlap={overlap}")
    return {"window_size": int(window_size), "window_overlap": int(overlap)}

@flow(name="Sliding Window Chunking Flow")
def sliding_window_chunking_flow(
    file_path: str,
    window_size: int = 1000,
    window_overlap: int = 500,
    by_tokens: bool = True,
    auto_optimize: bool = False,
    target_chunk_count: int = 10
) -> List[Dict[str, Any]]:
    """Prefect flow for sliding window chunking of a document.

    Args:
        file_path: Path to the document file
        window_size: The size of each window/chunk (in tokens or characters)
        window_overlap: The number of tokens/characters to overlap between windows
        by_tokens: If True, chunk by tokens; if False, chunk by characters
        auto_optimize: If True, automatically optimize window parameters
        target_chunk_count: Target number of chunks if auto_optimize is True
    """
    # Load the document
    document = load_document(file_path)

    # Optimize parameters if requested
    if auto_optimize:
        params = optimize_window_parameters(
            text=document,
            target_chunk_count=target_chunk_count
        )
        window_size = params["window_size"]
        window_overlap = params["window_overlap"]
        logger.info(f"Using optimized parameters: window_size={window_size}, window_overlap={window_overlap}")

    # Perform sliding window chunking
    chunks = sliding_window_chunking(
        text=document,
        window_size=window_size,
        window_overlap=window_overlap,
        by_tokens=by_tokens
    )

    return chunks

# Example usage
if __name__ == "__main__":
    # Example document path
    document_path = "path/to/your/document.txt"

    # Run the flow with auto-optimization
    chunks = sliding_window_chunking_flow(
        file_path=document_path,
        auto_optimize=True,
        target_chunk_count=10  # Aim for 10 chunks
    )

    # Print the first chunk as an example
    if chunks:
        print(f"First chunk: {chunks[0]['text'][:100]}...")
        print(f"Metadata: {chunks[0]['metadata']}")
        print(f"Total chunks created: {len(chunks)}")
        print(f"Overlap with next chunk: {chunks[0]['metadata'].get('overlap_with_next', 0)} tokens")
```

This implementation provides a sliding-window chunking strategy with the following features:

- Creates overlapping chunks by sliding a window across the text
- Supports chunking by tokens or characters
- Configurable window size and overlap amount
- Automatic parameter optimization to achieve a target number of chunks
- Detailed metadata including overlap information
- Wrapped in a Prefect flow for easy integration into data pipelines

