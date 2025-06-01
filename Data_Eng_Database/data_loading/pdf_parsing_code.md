# PDF Parsing Code Implementations

This document contains code implementations for the PDF parsing strategies described in `pdf_parsing.md`. All implementations use the Prefect library for workflow management.

## Table of Contents

1. [Unstructured](#unstructured)
2. [LlamaParse](#llamaparse)
3. [PyMuPDF4LLM](#pymupdf4llm)
4. [Docling](#docling)
5. [VLM Based PDF Parsing](#vlm-based-pdf-parsing)

## Unstructured

```python
from prefect import task, flow
from typing import List, Dict, Any, Optional, Union
import os
import logging
from pathlib import Path
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from unstructured.partition.pdf import partition_pdf
    from unstructured.partition.auto import partition
    from unstructured.chunking.title import chunk_by_title
    UNSTRUCTURED_AVAILABLE = True
except ImportError:
    logger.warning("Unstructured package not available. Install with: pip install unstructured[pdf]")
    UNSTRUCTURED_AVAILABLE = False

@task(name="check_unstructured_dependencies")
def check_unstructured_dependencies() -> bool:
    """Check if unstructured and its dependencies are installed."""
    if not UNSTRUCTURED_AVAILABLE:
        logger.error("Unstructured package is required but not installed.")
        logger.info("Install with: pip install unstructured[pdf]")
        return False
    return True

@task(name="partition_pdf_with_unstructured")
def partition_pdf_with_unstructured(
    pdf_path: str,
    strategy: str = "hi_res",
    extract_images_in_pdf: bool = False,
    extract_image_block_types: Optional[List[str]] = None,
    include_metadata: bool = True
) -> List[Dict[str, Any]]:
    """
    Extract content from a PDF file using Unstructured.

    Args:
        pdf_path: Path to the PDF file
        strategy: Extraction strategy ('fast', 'hi_res', or 'ocr_only')
        extract_images_in_pdf: Whether to extract images from the PDF
        extract_image_block_types: Types of image blocks to extract
        include_metadata: Whether to include metadata in the output

    Returns:
        List of extracted elements with their metadata
    """
    if not UNSTRUCTURED_AVAILABLE:
        raise ImportError("Unstructured package is required but not installed.")

    logger.info(f"Partitioning PDF: {pdf_path} with strategy: {strategy}")
    start_time = time.time()

    # Default image block types if not specified
    if extract_images_in_pdf and extract_image_block_types is None:
        extract_image_block_types = ["Image", "Table"]

    try:
        # Extract content from PDF
        elements = partition_pdf(
            filename=pdf_path,
            strategy=strategy,
            extract_images_in_pdf=extract_images_in_pdf,
            extract_image_block_types=extract_image_block_types,
            include_metadata=include_metadata
        )

        # Convert elements to dictionaries for easier serialization
        result = []
        for element in elements:
            element_dict = {
                "type": element.category,
                "text": str(element),
                "metadata": {}
            }

            # Include metadata if available
            if include_metadata and hasattr(element, "metadata"):
                element_dict["metadata"] = {
                    k: str(v) if not isinstance(v, (int, float, bool, type(None))) else v
                    for k, v in element.metadata.items()
                }

            result.append(element_dict)

        elapsed_time = time.time() - start_time
        logger.info(f"PDF partitioning completed in {elapsed_time:.2f} seconds. Extracted {len(result)} elements.")

        return result

    except Exception as e:
        logger.error(f"Error partitioning PDF: {e}")
        raise

@task(name="chunk_unstructured_elements")
def chunk_unstructured_elements(
    elements: List[Dict[str, Any]],
    chunk_size: int = 1000,
    max_characters: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Chunk the extracted elements from Unstructured.

    Args:
        elements: List of elements extracted from the PDF
        chunk_size: Maximum number of characters per chunk
        max_characters: Maximum number of characters to include from the document

    Returns:
        List of chunked elements
    """
    if not UNSTRUCTURED_AVAILABLE:
        raise ImportError("Unstructured package is required but not installed.")

    logger.info(f"Chunking {len(elements)} elements with chunk size: {chunk_size}")

    # Convert dictionary elements back to unstructured elements for chunking
    # This is a simplified version - in a real implementation, you would use the actual elements
    from unstructured.documents.elements import (
        Title, NarrativeText, ListItem, Table, Image
    )

    # Map element types to classes (simplified)
    type_to_class = {
        "Title": Title,
        "NarrativeText": NarrativeText,
        "ListItem": ListItem,
        "Table": Table,
        "Image": Image,
    }

    # Convert dict elements to unstructured elements (simplified)
    unstructured_elements = []
    for element in elements:
        element_class = type_to_class.get(element["type"], NarrativeText)
        elem = element_class(text=element["text"])
        if "metadata" in element:
            elem.metadata = element["metadata"]
        unstructured_elements.append(elem)

    # Apply chunking
    try:
        chunked_elements = chunk_by_title(
            unstructured_elements,
            max_characters=chunk_size,
            combine_text_under_n_chars=200  # Combine small elements
        )

        # Convert chunked elements to dictionaries
        result = []
        for element in chunked_elements:
            element_dict = {
                "type": element.category,
                "text": str(element),
                "metadata": {}
            }

            if hasattr(element, "metadata"):
                element_dict["metadata"] = {
                    k: str(v) if not isinstance(v, (int, float, bool, type(None))) else v
                    for k, v in element.metadata.items()
                }

            result.append(element_dict)

        # Limit total content if max_characters is specified
        if max_characters is not None:
            total_chars = 0
            limited_result = []

            for element in result:
                element_chars = len(element["text"])
                if total_chars + element_chars <= max_characters:
                    limited_result.append(element)
                    total_chars += element_chars
                else:
                    # Add partial element to reach exactly max_characters
                    chars_remaining = max_characters - total_chars
                    if chars_remaining > 0:
                        truncated_element = element.copy()
                        truncated_element["text"] = element["text"][:chars_remaining]
                        truncated_element["metadata"]["truncated"] = True
                        limited_result.append(truncated_element)
                    break

            result = limited_result

        logger.info(f"Chunking completed. Created {len(result)} chunks.")
        return result

    except Exception as e:
        logger.error(f"Error chunking elements: {e}")
        raise

@flow(name="Unstructured PDF Parsing Flow")
def unstructured_pdf_parsing_flow(
    pdf_path: str,
    strategy: str = "hi_res",
    extract_images: bool = False,
    chunk_size: int = 1000,
    max_characters: Optional[int] = None
) -> Dict[str, Any]:
    """
    Prefect flow for parsing PDFs using Unstructured.

    Args:
        pdf_path: Path to the PDF file
        strategy: Extraction strategy ('fast', 'hi_res', or 'ocr_only')
        extract_images: Whether to extract images from the PDF
        chunk_size: Maximum number of characters per chunk
        max_characters: Maximum number of characters to include from the document

    Returns:
        Dictionary containing the extracted and chunked elements
    """
    # Check dependencies
    dependencies_ok = check_unstructured_dependencies()
    if not dependencies_ok:
        return {"error": "Unstructured package is not installed"}

    # Validate PDF path
    if not os.path.exists(pdf_path):
        return {"error": f"PDF file not found: {pdf_path}"}

    # Extract content from PDF
    elements = partition_pdf_with_unstructured(
        pdf_path=pdf_path,
        strategy=strategy,
        extract_images_in_pdf=extract_images
    )

    # Chunk the extracted elements
    chunked_elements = chunk_unstructured_elements(
        elements=elements,
        chunk_size=chunk_size,
        max_characters=max_characters
    )

    # Prepare result
    result = {
        "pdf_path": pdf_path,
        "strategy": strategy,
        "extract_images": extract_images,
        "chunk_size": chunk_size,
        "raw_elements_count": len(elements),
        "chunked_elements_count": len(chunked_elements),
        "chunked_elements": chunked_elements
    }

    return result

# Example usage
if __name__ == "__main__":
    # Example PDF path
    pdf_path = "path/to/your/document.pdf"

    # Run the flow
    result = unstructured_pdf_parsing_flow(
        pdf_path=pdf_path,
        strategy="hi_res",  # Options: 'fast', 'hi_res', 'ocr_only'
        extract_images=True,
        chunk_size=1000,
        max_characters=50000  # Limit total content (optional)
    )

    # Print summary
    print(f"Processed PDF: {result['pdf_path']}")
    print(f"Extraction strategy: {result['strategy']}")
    print(f"Raw elements extracted: {result['raw_elements_count']}")
    print(f"Chunks created: {result['chunked_elements_count']}")

    # Print first chunk as example
    if result['chunked_elements']:
        first_chunk = result['chunked_elements'][0]
        print("\nExample chunk:")
        print(f"Type: {first_chunk['type']}")
        print(f"Text: {first_chunk['text'][:200]}...")
        print(f"Metadata: {first_chunk['metadata']}")
```

This implementation provides a comprehensive workflow for parsing PDFs using the Unstructured library with the following features:

- Flexible extraction strategies (fast, hi_res, ocr_only)
- Image extraction capabilities
- Intelligent chunking based on document structure
- Metadata preservation
- Configurable chunk sizes and content limits
- Proper error handling and logging
- Wrapped in a Prefect flow for easy integration into data pipelines

## LlamaParse

```python
from prefect import task, flow
from typing import List, Dict, Any, Optional, Union
import os
import logging
import time
import json
import requests
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@task(name="check_llamaparse_api_key")
def check_llamaparse_api_key(api_key: Optional[str] = None) -> bool:
    """
    Check if LlamaParse API key is available.

    Args:
        api_key: LlamaParse API key

    Returns:
        True if API key is available, False otherwise
    """
    if api_key is None:
        api_key = os.environ.get("LLAMAPARSE_API_KEY")

    if not api_key:
        logger.error("LlamaParse API key is required but not provided.")
        logger.info("Set the LLAMAPARSE_API_KEY environment variable or provide it as a parameter.")
        return False

    return True

@task(name="upload_file_to_llamaparse")
def upload_file_to_llamaparse(
    file_path: str,
    api_key: str,
    api_base: str = "https://api.llamaindex.ai/v1"
) -> Dict[str, Any]:
    """
    Upload a file to LlamaParse API.

    Args:
        file_path: Path to the file to upload
        api_key: LlamaParse API key
        api_base: LlamaParse API base URL

    Returns:
        Response from the API containing the file ID
    """
    logger.info(f"Uploading file to LlamaParse: {file_path}")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    upload_url = f"{api_base}/files"

    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    try:
        with open(file_path, "rb") as file:
            files = {"file": (os.path.basename(file_path), file)}
            response = requests.post(upload_url, headers=headers, files=files)

        if response.status_code != 200:
            logger.error(f"Error uploading file: {response.text}")
            raise Exception(f"Error uploading file: {response.status_code} - {response.text}")

        result = response.json()
        logger.info(f"File uploaded successfully. File ID: {result.get('id')}")
        return result

    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise

@task(name="parse_file_with_llamaparse")
def parse_file_with_llamaparse(
    file_id: str,
    api_key: str,
    parsing_mode: str = "balanced",
    output_format: str = "markdown",
    api_base: str = "https://api.llamaindex.ai/v1",
    max_wait_seconds: int = 300
) -> Dict[str, Any]:
    """
    Parse a file using LlamaParse API.

    Args:
        file_id: ID of the uploaded file
        api_key: LlamaParse API key
        parsing_mode: Parsing mode ('fast', 'balanced', 'premium', or 'custom')
        output_format: Output format ('markdown', 'text', or 'json')
        api_base: LlamaParse API base URL
        max_wait_seconds: Maximum time to wait for parsing to complete

    Returns:
        Parsed content and metadata
    """
    logger.info(f"Parsing file with LlamaParse. File ID: {file_id}, Mode: {parsing_mode}")

    parse_url = f"{api_base}/parse"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "file_id": file_id,
        "parsing_mode": parsing_mode,
        "result_type": output_format
    }

    try:
        # Start parsing
        response = requests.post(parse_url, headers=headers, json=payload)

        if response.status_code != 200:
            logger.error(f"Error starting parsing: {response.text}")
            raise Exception(f"Error starting parsing: {response.status_code} - {response.text}")

        parse_result = response.json()
        task_id = parse_result.get("task_id")

        if not task_id:
            raise Exception("No task ID returned from parsing request")

        logger.info(f"Parsing started. Task ID: {task_id}")

        # Poll for results
        status_url = f"{api_base}/tasks/{task_id}"
        start_time = time.time()

        while time.time() - start_time < max_wait_seconds:
            status_response = requests.get(status_url, headers=headers)

            if status_response.status_code != 200:
                logger.error(f"Error checking parsing status: {status_response.text}")
                raise Exception(f"Error checking parsing status: {status_response.status_code} - {status_response.text}")

            status_result = status_response.json()
            status = status_result.get("status")

            if status == "completed":
                logger.info(f"Parsing completed successfully in {time.time() - start_time:.2f} seconds")
                return status_result

            if status == "failed":
                error = status_result.get("error", "Unknown error")
                logger.error(f"Parsing failed: {error}")
                raise Exception(f"Parsing failed: {error}")

            # Wait before polling again
            time.sleep(5)

        # If we get here, we've timed out
        logger.error(f"Parsing timed out after {max_wait_seconds} seconds")
        raise Exception(f"Parsing timed out after {max_wait_seconds} seconds")

    except Exception as e:
        logger.error(f"Error parsing file: {e}")
        raise

@task(name="chunk_llamaparse_content")
def chunk_llamaparse_content(
    content: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    output_format: str = "markdown"
) -> List[Dict[str, Any]]:
    """
    Chunk the content parsed by LlamaParse.

    Args:
        content: Content parsed by LlamaParse
        chunk_size: Maximum number of characters per chunk
        chunk_overlap: Number of characters to overlap between chunks
        output_format: Format of the content ('markdown', 'text', or 'json')

    Returns:
        List of chunked content with metadata
    """
    logger.info(f"Chunking LlamaParse content with chunk size: {chunk_size}, overlap: {chunk_overlap}")

    # For JSON format, we need to parse it first
    if output_format == "json":
        try:
            parsed_content = json.loads(content)
            # Process JSON content based on its structure
            # This is a simplified example - adjust based on actual JSON structure
            chunks = []

            # Assuming the JSON has a list of sections or elements
            if isinstance(parsed_content, list):
                current_chunk = ""
                current_metadata = {}

                for item in parsed_content:
                    item_text = json.dumps(item)

                    if len(current_chunk) + len(item_text) > chunk_size and current_chunk:
                        # Save current chunk and start a new one
                        chunks.append({
                            "text": current_chunk,
                            "metadata": current_metadata
                        })

                        # Start new chunk with overlap
                        if chunk_overlap > 0 and chunks:
                            # Get the last part of the previous chunk for overlap
                            last_chunk = chunks[-1]["text"]
                            overlap_text = last_chunk[-chunk_overlap:] if len(last_chunk) > chunk_overlap else last_chunk
                            current_chunk = overlap_text
                        else:
                            current_chunk = ""

                        current_metadata = {}

                    current_chunk += (item_text + "\n")

                    # Add metadata if available
                    if isinstance(item, dict):
                        if "title" in item:
                            current_metadata["title"] = item["title"]
                        if "page" in item:
                            current_metadata["page"] = item["page"]

                # Add the last chunk if not empty
                if current_chunk:
                    chunks.append({
                        "text": current_chunk,
                        "metadata": current_metadata
                    })

            return chunks

        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON content. Falling back to text chunking.")
            # Fall back to text chunking

    # For markdown or text (or JSON fallback)
    lines = content.split("\n")
    chunks = []
    current_chunk = ""
    current_metadata = {}

    # Extract headers for metadata
    header_pattern = r"^(#+)\s+(.+)$"
    import re

    for line in lines:
        # Check if line is a header
        header_match = re.match(header_pattern, line)
        if header_match:
            level = len(header_match.group(1))
            title = header_match.group(2).strip()

            # Update metadata with header info
            if level == 1:
                current_metadata["title"] = title
            elif level == 2:
                current_metadata["section"] = title
            elif level == 3:
                current_metadata["subsection"] = title

        # Check if adding this line would exceed chunk size
        if len(current_chunk) + len(line) + 1 > chunk_size and current_chunk:
            # Save current chunk and start a new one
            chunks.append({
                "text": current_chunk,
                "metadata": current_metadata.copy()
            })

            # Start new chunk with overlap
            if chunk_overlap > 0 and current_chunk:
                # Get the last part of the previous chunk for overlap
                overlap_lines = current_chunk.split("\n")
                overlap_text = ""
                overlap_size = 0

                for ol in reversed(overlap_lines):
                    if overlap_size + len(ol) + 1 <= chunk_overlap:
                        overlap_text = ol + "\n" + overlap_text
                        overlap_size += len(ol) + 1
                    else:
                        break

                current_chunk = overlap_text
            else:
                current_chunk = ""

        current_chunk += (line + "\n")

    # Add the last chunk if not empty
    if current_chunk:
        chunks.append({
            "text": current_chunk,
            "metadata": current_metadata
        })

    logger.info(f"Chunking completed. Created {len(chunks)} chunks.")
    return chunks

@flow(name="LlamaParse PDF Parsing Flow")
def llamaparse_pdf_parsing_flow(
    pdf_path: str,
    api_key: Optional[str] = None,
    parsing_mode: str = "balanced",
    output_format: str = "markdown",
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    max_wait_seconds: int = 300
) -> Dict[str, Any]:
    """
    Prefect flow for parsing PDFs using LlamaParse.

    Args:
        pdf_path: Path to the PDF file
        api_key: LlamaParse API key (optional if set as environment variable)
        parsing_mode: Parsing mode ('fast', 'balanced', 'premium', or 'custom')
        output_format: Output format ('markdown', 'text', or 'json')
        chunk_size: Maximum number of characters per chunk
        chunk_overlap: Number of characters to overlap between chunks
        max_wait_seconds: Maximum time to wait for parsing to complete

    Returns:
        Dictionary containing the parsed and chunked content
    """
    # Use environment variable if API key not provided
    if api_key is None:
        api_key = os.environ.get("LLAMAPARSE_API_KEY")

    # Check API key
    api_key_ok = check_llamaparse_api_key(api_key)
    if not api_key_ok:
        return {"error": "LlamaParse API key is not available"}

    # Validate PDF path
    if not os.path.exists(pdf_path):
        return {"error": f"PDF file not found: {pdf_path}"}

    # Upload file to LlamaParse
    upload_result = upload_file_to_llamaparse(
        file_path=pdf_path,
        api_key=api_key
    )

    file_id = upload_result.get("id")
    if not file_id:
        return {"error": "Failed to get file ID from upload response"}

    # Parse file with LlamaParse
    parse_result = parse_file_with_llamaparse(
        file_id=file_id,
        api_key=api_key,
        parsing_mode=parsing_mode,
        output_format=output_format,
        max_wait_seconds=max_wait_seconds
    )

    # Extract content from parse result
    content = parse_result.get("result", "")
    if not content:
        return {"error": "No content returned from parsing"}

    # Chunk the parsed content
    chunked_content = chunk_llamaparse_content(
        content=content,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        output_format=output_format
    )

    # Prepare result
    result = {
        "pdf_path": pdf_path,
        "parsing_mode": parsing_mode,
        "output_format": output_format,
        "file_id": file_id,
        "task_id": parse_result.get("task_id"),
        "chunks_count": len(chunked_content),
        "chunks": chunked_content
    }

    return result

# Example usage
if __name__ == "__main__":
    # Example PDF path
    pdf_path = "path/to/your/document.pdf"

    # Run the flow
    result = llamaparse_pdf_parsing_flow(
        pdf_path=pdf_path,
        parsing_mode="balanced",  # Options: 'fast', 'balanced', 'premium', 'custom'
        output_format="markdown",  # Options: 'markdown', 'text', 'json'
        chunk_size=1000,
        chunk_overlap=200,
        max_wait_seconds=300
    )

    # Print summary
    print(f"Processed PDF: {result['pdf_path']}")
    print(f"Parsing mode: {result['parsing_mode']}")
    print(f"Output format: {result['output_format']}")
    print(f"Chunks created: {result['chunks_count']}")

    # Print first chunk as example
    if result['chunks']:
        first_chunk = result['chunks'][0]
        print("\nExample chunk:")
        print(f"Text: {first_chunk['text'][:200]}...")
        print(f"Metadata: {first_chunk['metadata']}")
```

This implementation provides a comprehensive workflow for parsing PDFs using the LlamaParse API with the following features:

- Multiple parsing modes (fast, balanced, premium, custom)
- Support for different output formats (markdown, text, JSON)
- Intelligent chunking with configurable size and overlap
- Metadata extraction from document structure
- Proper error handling and logging
- Asynchronous processing with status polling
- Wrapped in a Prefect flow for easy integration into data pipelines

## PyMuPDF4LLM

```python
from prefect import task, flow
from typing import List, Dict, Any, Optional, Union, Tuple
import os
import logging
import time
import json
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    logger.warning("PyMuPDF package not available. Install with: pip install pymupdf")
    PYMUPDF_AVAILABLE = False

@task(name="check_pymupdf_dependencies")
def check_pymupdf_dependencies() -> bool:
    """Check if PyMuPDF and its dependencies are installed."""
    if not PYMUPDF_AVAILABLE:
        logger.error("PyMuPDF package is required but not installed.")
        logger.info("Install with: pip install pymupdf")
        return False
    return True

@task(name="extract_pdf_metadata")
def extract_pdf_metadata(pdf_path: str) -> Dict[str, Any]:
    """Extract metadata from a PDF file.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        Dictionary containing PDF metadata
    """
    if not PYMUPDF_AVAILABLE:
        raise ImportError("PyMuPDF package is required but not installed.")

    logger.info(f"Extracting metadata from PDF: {pdf_path}")

    try:
        doc = fitz.open(pdf_path)
        metadata = {
            "title": doc.metadata.get("title", ""),
            "author": doc.metadata.get("author", ""),
            "subject": doc.metadata.get("subject", ""),
            "keywords": doc.metadata.get("keywords", ""),
            "creator": doc.metadata.get("creator", ""),
            "producer": doc.metadata.get("producer", ""),
            "creation_date": doc.metadata.get("creationDate", ""),
            "modification_date": doc.metadata.get("modDate", ""),
            "page_count": len(doc),
            "file_size": os.path.getsize(pdf_path),
            "file_name": os.path.basename(pdf_path)
        }
        doc.close()
        return metadata

    except Exception as e:
        logger.error(f"Error extracting PDF metadata: {e}")
        raise

@task(name="extract_pdf_toc")
def extract_pdf_toc(pdf_path: str) -> List[Dict[str, Any]]:
    """Extract table of contents (TOC) from a PDF file.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        List of TOC entries with title, page, and level
    """
    if not PYMUPDF_AVAILABLE:
        raise ImportError("PyMuPDF package is required but not installed.")

    logger.info(f"Extracting TOC from PDF: {pdf_path}")

    try:
        doc = fitz.open(pdf_path)
        toc = doc.get_toc()

        # Convert TOC to a more usable format
        result = []
        for entry in toc:
            level, title, page = entry
            result.append({
                "level": level,
                "title": title,
                "page": page
            })

        doc.close()
        return result

    except Exception as e:
        logger.error(f"Error extracting PDF TOC: {e}")
        raise

@task(name="extract_pdf_text")
def extract_pdf_text(
    pdf_path: str,
    start_page: int = 0,
    end_page: Optional[int] = None,
    extract_images: bool = False,
    extract_tables: bool = False
) -> List[Dict[str, Any]]:
    """Extract text and optionally images and tables from a PDF file.

    Args:
        pdf_path: Path to the PDF file
        start_page: First page to extract (0-based index)
        end_page: Last page to extract (0-based index, None for all pages)
        extract_images: Whether to extract images
        extract_tables: Whether to attempt table extraction

    Returns:
        List of dictionaries containing page content
    """
    if not PYMUPDF_AVAILABLE:
        raise ImportError("PyMuPDF package is required but not installed.")

    logger.info(f"Extracting text from PDF: {pdf_path}")
    start_time = time.time()

    try:
        doc = fitz.open(pdf_path)

        # Validate page range
        if end_page is None:
            end_page = len(doc) - 1
        else:
            end_page = min(end_page, len(doc) - 1)

        start_page = max(0, start_page)
        if start_page > end_page:
            raise ValueError(f"Invalid page range: {start_page} to {end_page}")

        pages = []
        for page_num in range(start_page, end_page + 1):
            page = doc[page_num]
            page_dict = {
                "page_number": page_num + 1,  # 1-based for user-friendly display
                "text": page.get_text(),
                "images": [],
                "tables": []
            }

            # Extract images if requested
            if extract_images:
                image_list = page.get_images(full=True)
                for img_index, img_info in enumerate(image_list):
                    xref = img_info[0]  # Image reference number
                    try:
                        base_image = doc.extract_image(xref)
                        image_data = {
                            "index": img_index,
                            "width": base_image["width"],
                            "height": base_image["height"],
                            "format": base_image["ext"],
                            # We don't include the binary data in the result
                            # but you could save it to a file here if needed
                        }
                        page_dict["images"].append(image_data)
                    except Exception as e:
                        logger.warning(f"Error extracting image {img_index} on page {page_num + 1}: {e}")

            # Extract tables if requested
            # This is a simplified approach - for better table extraction,
            # consider using specialized libraries like camelot-py or tabula-py
            if extract_tables:
                # Simple heuristic: look for blocks that might be tables
                blocks = page.get_text("blocks")
                for block_index, block in enumerate(blocks):
                    # Check if block contains multiple lines with similar structure
                    # This is a very basic heuristic and won't catch all tables
                    lines = block[4].split('\n')
                    if len(lines) > 3:  # At least 3 rows to be considered a table
                        # Check if lines have similar structure (e.g., same number of spaces or tabs)
                        space_counts = [line.count(' ') for line in lines]
                        tab_counts = [line.count('\t') for line in lines]

                        # If consistent pattern of spaces or tabs, might be a table
                        if (max(space_counts) - min(space_counts) <= 3) or (max(tab_counts) - min(tab_counts) <= 1):
                            table_data = {
                                "index": block_index,
                                "bbox": block[:4],  # Bounding box
                                "text": block[4],
                                "rows": lines
                            }
                            page_dict["tables"].append(table_data)

            pages.append(page_dict)

        doc.close()

        elapsed_time = time.time() - start_time
        logger.info(f"PDF text extraction completed in {elapsed_time:.2f} seconds. Extracted {len(pages)} pages.")

        return pages

    except Exception as e:
        logger.error(f"Error extracting PDF text: {e}")
        raise

@task(name="convert_pdf_to_markdown")
def convert_pdf_to_markdown(
    pages: List[Dict[str, Any]],
    metadata: Dict[str, Any],
    toc: List[Dict[str, Any]]
) -> str:
    """Convert extracted PDF content to markdown format.

    Args:
        pages: List of page dictionaries with extracted content
        metadata: PDF metadata
        toc: Table of contents

    Returns:
        Markdown representation of the PDF
    """
    logger.info("Converting PDF content to markdown")

    markdown = []

    # Add title and metadata
    if metadata.get("title"):
        markdown.append(f"# {metadata['title']}\n")
    else:
        markdown.append(f"# {metadata['file_name']}\n")

    # Add metadata section
    markdown.append("## Document Information\n")
    if metadata.get("author"):
        markdown.append(f"* **Author:** {metadata['author']}\n")
    if metadata.get("creation_date"):
        markdown.append(f"* **Created:** {metadata['creation_date']}\n")
    if metadata.get("modification_date"):
        markdown.append(f"* **Modified:** {metadata['modification_date']}\n")
    markdown.append(f"* **Pages:** {metadata['page_count']}\n")

    # Add table of contents if available
    if toc:
        markdown.append("\n## Table of Contents\n")
        for entry in toc:
            indent = "  " * (entry["level"] - 1)
            markdown.append(f"{indent}* [{entry['title']}](#page-{entry['page']})\n")

    # Add content for each page
    for page in pages:
        page_num = page["page_number"]
        markdown.append(f"\n## Page {page_num}\n")

        # Add page text
        text = page["text"]
        # Clean up text - remove excessive newlines, etc.
        text = "\n".join(line for line in text.split("\n") if line.strip())
        markdown.append(text + "\n")

        # Add image placeholders if any
        if page["images"]:
            markdown.append("\n### Images\n")
            for img in page["images"]:
                markdown.append(f"* Image {img['index']+1}: {img['width']}x{img['height']} {img['format']}\n")

        # Add table content if any
        if page["tables"]:
            markdown.append("\n### Tables\n")
            for table in page["tables"]:
                markdown.append("\n```\n")
                markdown.append(table["text"])
                markdown.append("\n```\n")

    return "".join(markdown)

@task(name="chunk_markdown_content")
def chunk_markdown_content(
    markdown: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200
) -> List[Dict[str, Any]]:
    """Chunk markdown content into smaller pieces.

    Args:
        markdown: Markdown content to chunk
        chunk_size: Maximum number of characters per chunk
        chunk_overlap: Number of characters to overlap between chunks

    Returns:
        List of chunked content with metadata
    """
    logger.info(f"Chunking markdown content with chunk size: {chunk_size}, overlap: {chunk_overlap}")

    # Split by headers to preserve document structure
    import re
    header_pattern = r"(^#{1,6}\s.+$)"
    sections = re.split(header_pattern, markdown, flags=re.MULTILINE)

    # Pair headers with their content
    chunks = []
    current_chunk = ""
    current_metadata = {}
    current_headers = {}

    for i in range(0, len(sections)):
        section = sections[i]
        if not section.strip():
            continue

        # Check if this is a header
        header_match = re.match(r"^(#{1,6})\s(.+)$", section)
        if header_match:
            level = len(header_match.group(1))
            title = header_match.group(2).strip()

            # Update current headers based on level
            for l in range(level, 7):
                if l in current_headers:
                    del current_headers[l]
            current_headers[level] = title

            # Update metadata with header info
            if level == 1:
                current_metadata["title"] = title
            elif level == 2:
                current_metadata["section"] = title
            elif level == 3:
                current_metadata["subsection"] = title

            # Add header to current chunk
            if len(current_chunk) + len(section) + 1 > chunk_size and current_chunk:
                # Save current chunk and start a new one
                chunks.append({
                    "text": current_chunk,
                    "metadata": current_metadata.copy()
                })

                # Start new chunk with overlap
                if chunk_overlap > 0 and current_chunk:
                    # Get the last part of the previous chunk for overlap
                    overlap_chars = min(chunk_overlap, len(current_chunk))
                    current_chunk = current_chunk[-overlap_chars:]
                else:
                    current_chunk = ""

            current_chunk += section + "\n"
        else:
            # This is content, add it to the current chunk
            # Check if adding this content would exceed chunk size
            if len(current_chunk) + len(section) + 1 > chunk_size and current_chunk:
                # Save current chunk and start a new one
                chunks.append({
                    "text": current_chunk,
                    "metadata": current_metadata.copy()
                })

                # Start new chunk with overlap
                if chunk_overlap > 0 and current_chunk:
                    overlap_chars = min(chunk_overlap, len(current_chunk))
                    current_chunk = current_chunk[-overlap_chars:]
                else:
                    current_chunk = ""

            current_chunk += section + "\n"

    # Add the last chunk if not empty
    if current_chunk:
        chunks.append({
            "text": current_chunk,
            "metadata": current_metadata.copy()
        })

    logger.info(f"Chunking completed. Created {len(chunks)} chunks.")
    return chunks

@flow(name="PyMuPDF4LLM PDF Parsing Flow")
def pymupdf_pdf_parsing_flow(
    pdf_path: str,
    start_page: int = 0,
    end_page: Optional[int] = None,
    extract_images: bool = False,
    extract_tables: bool = False,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    output_format: str = "markdown"
) -> Dict[str, Any]:
    """Prefect flow for parsing PDFs using PyMuPDF.

    Args:
        pdf_path: Path to the PDF file
        start_page: First page to extract (0-based index)
        end_page: Last page to extract (0-based index, None for all pages)
        extract_images: Whether to extract images
        extract_tables: Whether to attempt table extraction
        chunk_size: Maximum number of characters per chunk
        chunk_overlap: Number of characters to overlap between chunks
        output_format: Output format ('markdown' or 'text')

    Returns:
        Dictionary containing the parsed and chunked content
    """
    # Check dependencies
    dependencies_ok = check_pymupdf_dependencies()
    if not dependencies_ok:
        return {"error": "PyMuPDF package is not installed"}

    # Validate PDF path
    if not os.path.exists(pdf_path):
        return {"error": f"PDF file not found: {pdf_path}"}

    # Extract metadata
    metadata = extract_pdf_metadata(pdf_path)

    # Extract table of contents
    toc = extract_pdf_toc(pdf_path)

    # Extract text and other content
    pages = extract_pdf_text(
        pdf_path=pdf_path,
        start_page=start_page,
        end_page=end_page,
        extract_images=extract_images,
        extract_tables=extract_tables
    )

    # Convert to markdown
    markdown_content = convert_pdf_to_markdown(
        pages=pages,
        metadata=metadata,
        toc=toc
    )

    # Chunk the content
    chunked_content = chunk_markdown_content(
        markdown=markdown_content,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )

    # Prepare result
    result = {
        "pdf_path": pdf_path,
        "metadata": metadata,
        "toc": toc,
        "page_count": len(pages),
        "chunks_count": len(chunked_content),
        "chunks": chunked_content
    }

    # Include full markdown if requested
    if output_format == "markdown":
        result["markdown"] = markdown_content

    return result

# Example usage
if __name__ == "__main__":
    # Example PDF path
    pdf_path = "path/to/your/document.pdf"

    # Run the flow
    result = pymupdf_pdf_parsing_flow(
        pdf_path=pdf_path,
        start_page=0,  # Start from first page
        end_page=None,  # Process all pages
        extract_images=True,
        extract_tables=True,
        chunk_size=1000,
        chunk_overlap=200,
        output_format="markdown"
    )

    # Print summary
    print(f"Processed PDF: {result['pdf_path']}")
    print(f"Title: {result['metadata'].get('title', 'N/A')}")
    print(f"Author: {result['metadata'].get('author', 'N/A')}")
    print(f"Pages: {result['page_count']}")
    print(f"Chunks created: {result['chunks_count']}")

    # Print first chunk as example
    if result['chunks']:
        first_chunk = result['chunks'][0]
        print("\nExample chunk:")
        print(f"Text: {first_chunk['text'][:200]}...")
        print(f"Metadata: {first_chunk['metadata']}")
```

This implementation provides a comprehensive workflow for parsing PDFs using the PyMuPDF (fitz) library with the following features:

- Fast and efficient PDF text extraction
- Metadata and table of contents extraction
- Support for image and table detection
- Conversion to markdown format with proper structure
- Intelligent chunking with configurable size and overlap
- Page range selection for processing subsets of documents
- Proper error handling and logging
- Wrapped in a Prefect flow for easy integration into data pipelines

## Docling

```python
from prefect import task, flow
from typing import List, Dict, Any, Optional, Union
import os
import logging
import time
import json
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import docling
    from docling import DoclingDocument
    DOCLING_AVAILABLE = True
except ImportError:
    logger.warning("Docling package not available. Install with: pip install docling")
    DOCLING_AVAILABLE = False

@task(name="check_docling_dependencies")
def check_docling_dependencies() -> bool:
    """Check if Docling and its dependencies are installed."""
    if not DOCLING_AVAILABLE:
        logger.error("Docling package is required but not installed.")
        logger.info("Install with: pip install docling")
        return False
    return True

@task(name="parse_pdf_with_docling")
def parse_pdf_with_docling(
    pdf_path: str,
    ocr_enabled: bool = False,
    extract_images: bool = False,
    extract_tables: bool = True,
    extract_formulas: bool = True
) -> Dict[str, Any]:
    """Parse a PDF file using Docling.

    Args:
        pdf_path: Path to the PDF file
        ocr_enabled: Whether to use OCR for scanned documents
        extract_images: Whether to extract images
        extract_tables: Whether to extract tables
        extract_formulas: Whether to extract mathematical formulas

    Returns:
        Parsed document as a dictionary
    """
    if not DOCLING_AVAILABLE:
        raise ImportError("Docling package is required but not installed.")

    logger.info(f"Parsing PDF with Docling: {pdf_path}")
    start_time = time.time()

    try:
        # Load and parse the document
        doc = DoclingDocument.from_pdf(
            pdf_path,
            ocr_enabled=ocr_enabled,
            extract_images=extract_images,
            extract_tables=extract_tables,
            extract_formulas=extract_formulas
        )

        # Convert to dictionary for easier serialization
        result = {
            "metadata": {
                "title": doc.metadata.get("title", ""),
                "author": doc.metadata.get("author", ""),
                "creation_date": doc.metadata.get("creation_date", ""),
                "page_count": len(doc.pages),
                "file_name": os.path.basename(pdf_path),
                "file_size": os.path.getsize(pdf_path)
            },
            "pages": []
        }

        # Process each page
        for page_idx, page in enumerate(doc.pages):
            page_dict = {
                "page_number": page_idx + 1,
                "elements": []
            }

            # Process page elements
            for element in page.elements:
                element_dict = {
                    "type": element.type,
                    "text": element.text if hasattr(element, "text") else "",
                    "bbox": element.bbox.to_dict() if hasattr(element, "bbox") else None,
                }

                # Add element-specific attributes
                if element.type == "table":
                    element_dict["rows"] = len(element.rows) if hasattr(element, "rows") else 0
                    element_dict["columns"] = len(element.columns) if hasattr(element, "columns") else 0
                    element_dict["cells"] = []

                    # Extract table cells if available
                    if hasattr(element, "cells"):
                        for row_idx, row in enumerate(element.cells):
                            for col_idx, cell in enumerate(row):
                                cell_dict = {
                                    "row": row_idx,
                                    "column": col_idx,
                                    "text": cell.text if hasattr(cell, "text") else ""
                                }
                                element_dict["cells"].append(cell_dict)

                elif element.type == "image":
                    element_dict["width"] = element.width if hasattr(element, "width") else 0
                    element_dict["height"] = element.height if hasattr(element, "height") else 0
                    # We don't include the binary data in the result

                elif element.type == "formula":
                    element_dict["latex"] = element.latex if hasattr(element, "latex") else ""

                page_dict["elements"].append(element_dict)

            result["pages"].append(page_dict)

        elapsed_time = time.time() - start_time
        logger.info(f"PDF parsing completed in {elapsed_time:.2f} seconds. Extracted {len(result['pages'])} pages.")

        return result

    except Exception as e:
        logger.error(f"Error parsing PDF with Docling: {e}")
        raise

@task(name="convert_docling_to_markdown")
def convert_docling_to_markdown(parsed_document: Dict[str, Any]) -> str:
    """Convert Docling parsed document to markdown format.

    Args:
        parsed_document: Document parsed by Docling

    Returns:
        Markdown representation of the document
    """
    logger.info("Converting Docling document to markdown")

    markdown = []
    metadata = parsed_document["metadata"]

    # Add title and metadata
    if metadata.get("title"):
        markdown.append(f"# {metadata['title']}\n")
    else:
        markdown.append(f"# {metadata['file_name']}\n")

    # Add metadata section
    markdown.append("## Document Information\n")
    if metadata.get("author"):
        markdown.append(f"* **Author:** {metadata['author']}\n")
    if metadata.get("creation_date"):
        markdown.append(f"* **Created:** {metadata['creation_date']}\n")
    markdown.append(f"* **Pages:** {metadata['page_count']}\n")

    # Process each page
    for page in parsed_document["pages"]:
        page_num = page["page_number"]
        markdown.append(f"\n## Page {page_num}\n")

        # Group elements by type for better organization
        text_elements = []
        table_elements = []
        image_elements = []
        formula_elements = []

        for element in page["elements"]:
            if element["type"] == "text" or element["type"] == "paragraph" or element["type"] == "heading":
                text_elements.append(element)
            elif element["type"] == "table":
                table_elements.append(element)
            elif element["type"] == "image":
                image_elements.append(element)
            elif element["type"] == "formula":
                formula_elements.append(element)

        # Add text elements
        for element in text_elements:
            markdown.append(f"{element['text']}\n\n")

        # Add tables
        if table_elements:
            markdown.append("\n### Tables\n")
            for table_idx, table in enumerate(table_elements):
                markdown.append(f"\n**Table {table_idx + 1}**\n\n")

                # Create markdown table if cells are available
                if "cells" in table and table["cells"]:
                    # Determine number of rows and columns
                    max_row = max([cell["row"] for cell in table["cells"]]) if table["cells"] else 0
                    max_col = max([cell["column"] for cell in table["cells"]]) if table["cells"] else 0

                    # Create a 2D grid for the table
                    grid = [["" for _ in range(max_col + 1)] for _ in range(max_row + 1)]

                    # Fill in the grid with cell values
                    for cell in table["cells"]:
                        row, col = cell["row"], cell["column"]
                        grid[row][col] = cell["text"]

                    # Generate markdown table
                    # Header row
                    markdown.append("| " + " | ".join(grid[0]) + " |\n")
                    # Separator row
                    markdown.append("| " + " | ".join(["---" for _ in range(max_col + 1)]) + " |\n")
                    # Data rows
                    for row in grid[1:]:
                        markdown.append("| " + " | ".join(row) + " |\n")
                else:
                    # Fallback if structured cells aren't available
                    markdown.append(f"```\n{table['text']}\n```\n")

        # Add images
        if image_elements:
            markdown.append("\n### Images\n")
            for img_idx, img in enumerate(image_elements):
                markdown.append(f"* Image {img_idx + 1}: {img.get('width', 'N/A')}x{img.get('height', 'N/A')}\n")

        # Add formulas
        if formula_elements:
            markdown.append("\n### Formulas\n")
            for formula_idx, formula in enumerate(formula_elements):
                if formula.get("latex"):
                    markdown.append(f"* Formula {formula_idx + 1}: `{formula['latex']}`\n")
                else:
                    markdown.append(f"* Formula {formula_idx + 1}: {formula['text']}\n")

    return "".join(markdown)

@task(name="chunk_docling_document")
def chunk_docling_document(
    parsed_document: Dict[str, Any],
    markdown_content: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200
) -> List[Dict[str, Any]]:
    """Chunk the Docling document into smaller pieces.

    Args:
        parsed_document: Document parsed by Docling
        markdown_content: Markdown representation of the document
        chunk_size: Maximum number of characters per chunk
        chunk_overlap: Number of characters to overlap between chunks

    Returns:
        List of chunked content with metadata
    """
    logger.info(f"Chunking Docling document with chunk size: {chunk_size}, overlap: {chunk_overlap}")

    # We'll use a similar approach to the PyMuPDF chunking, but with awareness of Docling's structure
    import re
    header_pattern = r"(^#{1,6}\s.+$)"
    sections = re.split(header_pattern, markdown_content, flags=re.MULTILINE)

    chunks = []
    current_chunk = ""
    current_metadata = {
        "title": parsed_document["metadata"].get("title", ""),
        "author": parsed_document["metadata"].get("author", "")
    }
    current_page = 1

    for i in range(0, len(sections)):
        section = sections[i]
        if not section.strip():
            continue

        # Check if this is a header
        header_match = re.match(r"^(#{1,6})\s(.+)$", section)
        if header_match:
            level = len(header_match.group(1))
            title = header_match.group(2).strip()

            # Check for page headers to track current page
            page_match = re.match(r"Page (\d+)", title)
            if page_match:
                current_page = int(page_match.group(1))
                current_metadata["page"] = current_page

            # Update metadata with header info
            if level == 1:
                current_metadata["document_title"] = title
            elif level == 2 and not page_match:
                current_metadata["section"] = title
            elif level == 3:
                current_metadata["subsection"] = title

        # Check if adding this section would exceed chunk size
        if len(current_chunk) + len(section) + 1 > chunk_size and current_chunk:
            # Save current chunk and start a new one
            chunks.append({
                "text": current_chunk,
                "metadata": current_metadata.copy()
            })

            # Start new chunk with overlap
            if chunk_overlap > 0 and current_chunk:
                # Get the last part of the previous chunk for overlap
                overlap_chars = min(chunk_overlap, len(current_chunk))
                current_chunk = current_chunk[-overlap_chars:]
            else:
                current_chunk = ""

        current_chunk += section + "\n"

    # Add the last chunk if not empty
    if current_chunk:
        chunks.append({
            "text": current_chunk,
            "metadata": current_metadata.copy()
        })

    logger.info(f"Chunking completed. Created {len(chunks)} chunks.")
    return chunks

@flow(name="Docling PDF Parsing Flow")
def docling_pdf_parsing_flow(
    pdf_path: str,
    ocr_enabled: bool = False,
    extract_images: bool = False,
    extract_tables: bool = True,
    extract_formulas: bool = True,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    output_format: str = "markdown"
) -> Dict[str, Any]:
    """Prefect flow for parsing PDFs using Docling.

    Args:
        pdf_path: Path to the PDF file
        ocr_enabled: Whether to use OCR for scanned documents
        extract_images: Whether to extract images
        extract_tables: Whether to extract tables
        extract_formulas: Whether to extract mathematical formulas
        chunk_size: Maximum number of characters per chunk
        chunk_overlap: Number of characters to overlap between chunks
        output_format: Output format ('markdown', 'json', or 'html')

    Returns:
        Dictionary containing the parsed and chunked content
    """
    # Check dependencies
    dependencies_ok = check_docling_dependencies()
    if not dependencies_ok:
        return {"error": "Docling package is not installed"}

    # Validate PDF path
    if not os.path.exists(pdf_path):
        return {"error": f"PDF file not found: {pdf_path}"}

    # Parse PDF with Docling
    parsed_document = parse_pdf_with_docling(
        pdf_path=pdf_path,
        ocr_enabled=ocr_enabled,
        extract_images=extract_images,
        extract_tables=extract_tables,
        extract_formulas=extract_formulas
    )

    # Convert to markdown
    markdown_content = convert_docling_to_markdown(parsed_document)

    # Chunk the content
    chunked_content = chunk_docling_document(
        parsed_document=parsed_document,
        markdown_content=markdown_content,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )

    # Prepare result
    result = {
        "pdf_path": pdf_path,
        "metadata": parsed_document["metadata"],
        "page_count": len(parsed_document["pages"]),
        "chunks_count": len(chunked_content),
        "chunks": chunked_content
    }

    # Include full content in requested format
    if output_format == "markdown":
        result["markdown"] = markdown_content
    elif output_format == "json":
        result["json"] = json.dumps(parsed_document, indent=2)
    elif output_format == "html":
        # Convert markdown to HTML (simplified)
        try:
            import markdown
            result["html"] = markdown.markdown(markdown_content)
        except ImportError:
            logger.warning("Python-markdown package not available. Install with: pip install markdown")
            result["html"] = f"<pre>{markdown_content}</pre>"

    return result

# Example usage
if __name__ == "__main__":
    # Example PDF path
    pdf_path = "path/to/your/document.pdf"

    # Run the flow
    result = docling_pdf_parsing_flow(
        pdf_path=pdf_path,
        ocr_enabled=True,  # Enable OCR for scanned documents
        extract_images=True,
        extract_tables=True,
        extract_formulas=True,
        chunk_size=1000,
        chunk_overlap=200,
        output_format="markdown"
    )

    # Print summary
    print(f"Processed PDF: {result['pdf_path']}")
    print(f"Title: {result['metadata'].get('title', 'N/A')}")
    print(f"Author: {result['metadata'].get('author', 'N/A')}")
    print(f"Pages: {result['page_count']}")
    print(f"Chunks created: {result['chunks_count']}")

    # Print first chunk as example
    if result['chunks']:
        first_chunk = result['chunks'][0]
        print("\nExample chunk:")
        print(f"Text: {first_chunk['text'][:200]}...")
        print(f"Metadata: {first_chunk['metadata']}")
```

This implementation provides a comprehensive workflow for parsing PDFs using the Docling library with the following features:

- Advanced document understanding with layout analysis
- OCR support for scanned documents
- Table, image, and formula extraction
- Multiple output formats (markdown, JSON, HTML)
- Intelligent chunking with configurable size and overlap
- Metadata preservation and enrichment
- Proper error handling and logging
- Wrapped in a Prefect flow for easy integration into data pipelines

## VLM Based PDF Parsing

```python
from prefect import task, flow
from typing import List, Dict, Any, Optional, Union
import os
import logging
import time
import json
import base64
import tempfile
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import fitz  # PyMuPDF for PDF to image conversion
    import requests
    from PIL import Image
    import io
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    logger.warning("Some dependencies are not available. Install with: pip install pymupdf pillow requests")
    DEPENDENCIES_AVAILABLE = False

@task(name="check_vlm_dependencies")
def check_vlm_dependencies() -> bool:
    """Check if required dependencies are installed."""
    if not DEPENDENCIES_AVAILABLE:
        logger.error("Required packages are not installed.")
        logger.info("Install with: pip install pymupdf pillow requests")
        return False
    return True

@task(name="convert_pdf_to_images")
def convert_pdf_to_images(
    pdf_path: str,
    dpi: int = 300,
    output_format: str = "png",
    start_page: int = 0,
    end_page: Optional[int] = None
) -> List[Dict[str, Any]]:
    """Convert PDF pages to images.

    Args:
        pdf_path: Path to the PDF file
        dpi: Resolution for the output images
        output_format: Format for the output images ('png', 'jpeg', etc.)
        start_page: First page to convert (0-based index)
        end_page: Last page to convert (0-based index, None for all pages)

    Returns:
        List of dictionaries containing image data and metadata
    """
    if not DEPENDENCIES_AVAILABLE:
        raise ImportError("Required packages are not installed.")

    logger.info(f"Converting PDF to images: {pdf_path} with DPI: {dpi}")
    start_time = time.time()

    try:
        doc = fitz.open(pdf_path)

        # Validate page range
        if end_page is None:
            end_page = len(doc) - 1
        else:
            end_page = min(end_page, len(doc) - 1)

        start_page = max(0, start_page)
        if start_page > end_page:
            raise ValueError(f"Invalid page range: {start_page} to {end_page}")

        images = []
        for page_num in range(start_page, end_page + 1):
            page = doc[page_num]

            # Get the page dimensions
            rect = page.rect

            # Calculate zoom factor based on DPI
            # 72 is the default PDF DPI
            zoom = dpi / 72

            # Create a matrix for rendering
            matrix = fitz.Matrix(zoom, zoom)

            # Render page to pixmap
            pixmap = page.get_pixmap(matrix=matrix, alpha=False)

            # Convert pixmap to image data
            img_data = pixmap.tobytes(output_format)

            # Create image metadata
            image_info = {
                "page_number": page_num + 1,  # 1-based for user-friendly display
                "width": pixmap.width,
                "height": pixmap.height,
                "format": output_format,
                "data": img_data,
                "base64": base64.b64encode(img_data).decode("utf-8")
            }

            images.append(image_info)

        doc.close()

        elapsed_time = time.time() - start_time
        logger.info(f"PDF to image conversion completed in {elapsed_time:.2f} seconds. Converted {len(images)} pages.")

        return images

    except Exception as e:
        logger.error(f"Error converting PDF to images: {e}")
        raise

@task(name="process_image_with_vlm")
def process_image_with_vlm(
    image_data: Dict[str, Any],
    api_key: str,
    model: str = "gpt-4-vision-preview",  # Example model, replace with actual VLM model
    api_url: str = "https://api.openai.com/v1/chat/completions",  # Example API URL
    max_tokens: int = 4000,
    temperature: float = 0.2,
    prompt_template: Optional[str] = None
) -> Dict[str, Any]:
    """Process an image with a Vision Language Model (VLM).

    Args:
        image_data: Dictionary containing image data and metadata
        api_key: API key for the VLM service
        model: Name of the VLM model to use
        api_url: URL for the VLM API
        max_tokens: Maximum number of tokens in the response
        temperature: Temperature for the model's output
        prompt_template: Template for the prompt to the VLM

    Returns:
        Dictionary containing the VLM response and metadata
    """
    if not DEPENDENCIES_AVAILABLE:
        raise ImportError("Required packages are not installed.")

    page_num = image_data["page_number"]
    logger.info(f"Processing page {page_num} with VLM model: {model}")

    # Default prompt template if none provided
    if prompt_template is None:
        prompt_template = """
        You are an expert document analyzer. Please extract all the content from this PDF page image.

        Provide your response in the following JSON format:
        {{
            "page_number": {page_number},
            "content": {{
                "text": "The main text content of the page",
                "tables": [{{"caption": "Table caption", "content": "Table content as markdown"}}],
                "images": [{{"caption": "Image description", "content": "Detailed description of what's in the image"}}],
                "formulas": [{{"latex": "LaTeX representation of formula", "explanation": "Explanation of the formula"}}],
                "diagrams": [{{"description": "Description of the diagram", "explanation": "Explanation of what the diagram shows"}}]
            }},
            "metadata": {{
                "document_type": "Type of document (e.g., academic paper, report, etc.)",
                "section": "Section name if identifiable",
                "layout": "Description of the page layout"
            }}
        }}

        Important guidelines:
        1. Extract ALL text content from the page, preserving paragraphs and formatting.
        2. For tables, represent them in markdown format.
        3. For images, provide detailed descriptions of what they contain.
        4. For formulas, provide both LaTeX representation and explanation.
        5. For diagrams, describe what they show and explain their meaning.
        6. If any section is not present (e.g., no tables), use an empty array [].
        7. Ensure your response is valid JSON.
        """

    # Format the prompt with page number
    formatted_prompt = prompt_template.format(page_number=page_num)

    # Prepare the API request
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    # Prepare the payload with the image
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": formatted_prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/{image_data['format']};base64,{image_data['base64']}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": max_tokens,
        "temperature": temperature
    }

    try:
        # Make the API request
        response = requests.post(api_url, headers=headers, json=payload)

        if response.status_code != 200:
            logger.error(f"Error from VLM API: {response.text}")
            raise Exception(f"Error from VLM API: {response.status_code} - {response.text}")

        result = response.json()

        # Extract the content from the response
        content = result["choices"][0]["message"]["content"]

        # Parse the JSON content
        try:
            parsed_content = json.loads(content)
        except json.JSONDecodeError:
            logger.warning("VLM response is not valid JSON. Returning raw content.")
            parsed_content = {"raw_content": content}

        # Prepare the result
        vlm_result = {
            "page_number": page_num,
            "model": model,
            "parsed_content": parsed_content,
            "raw_response": result
        }

        return vlm_result

    except Exception as e:
        logger.error(f"Error processing image with VLM: {e}")
        raise

@task(name="combine_vlm_results")
def combine_vlm_results(
    vlm_results: List[Dict[str, Any]],
    metadata: Dict[str, Any]
) -> Dict[str, Any]:
    """Combine results from multiple VLM calls into a single document.

    Args:
        vlm_results: List of VLM results for each page
        metadata: Document metadata

    Returns:
        Combined document with all page contents
    """
    logger.info(f"Combining results from {len(vlm_results)} pages")

    # Sort results by page number
    sorted_results = sorted(vlm_results, key=lambda x: x["page_number"])

    # Prepare the combined document
    combined_doc = {
        "metadata": metadata,
        "pages": []
    }

    # Process each page result
    for result in sorted_results:
        page_content = result.get("parsed_content", {})

        # Add page to the combined document
        combined_doc["pages"].append(page_content)

    return combined_doc

@task(name="convert_vlm_results_to_markdown")
def convert_vlm_results_to_markdown(combined_doc: Dict[str, Any]) -> str:
    """Convert combined VLM results to markdown format.

    Args:
        combined_doc: Combined document with all page contents

    Returns:
        Markdown representation of the document
    """
    logger.info("Converting VLM results to markdown")

    markdown = []
    metadata = combined_doc["metadata"]

    # Add title and metadata
    if metadata.get("title"):
        markdown.append(f"# {metadata['title']}\n")
    else:
        markdown.append(f"# {metadata['file_name']}\n")

    # Add metadata section
    markdown.append("## Document Information\n")
    for key, value in metadata.items():
        if key not in ["title", "file_name"] and value:
            markdown.append(f"* **{key.replace('_', ' ').title()}:** {value}\n")

    # Process each page
    for page in combined_doc["pages"]:
        page_num = page.get("page_number", "Unknown")
        markdown.append(f"\n## Page {page_num}\n")

        # Add page metadata if available
        if "metadata" in page:
            page_metadata = page["metadata"]
            for key, value in page_metadata.items():
                if value:
                    markdown.append(f"*{key.replace('_', ' ').title()}: {value}*\n\n")

        # Add content if available
        if "content" in page:
            content = page["content"]

            # Add main text
            if "text" in content and content["text"]:
                markdown.append(f"{content['text']}\n\n")

            # Add tables
            if "tables" in content and content["tables"]:
                markdown.append("\n### Tables\n")
                for table_idx, table in enumerate(content["tables"]):
                    if "caption" in table and table["caption"]:
                        markdown.append(f"**{table['caption']}**\n\n")
                    if "content" in table and table["content"]:
                        markdown.append(f"{table['content']}\n\n")

            # Add images
            if "images" in content and content["images"]:
                markdown.append("\n### Images\n")
                for img_idx, img in enumerate(content["images"]):
                    if "caption" in img and img["caption"]:
                        markdown.append(f"**{img['caption']}**\n\n")
                    if "content" in img and img["content"]:
                        markdown.append(f"{img['content']}\n\n")

            # Add formulas
            if "formulas" in content and content["formulas"]:
                markdown.append("\n### Formulas\n")
                for formula_idx, formula in enumerate(content["formulas"]):
                    if "latex" in formula and formula["latex"]:
                        markdown.append(f"```latex\n{formula['latex']}\n```\n\n")
                    if "explanation" in formula and formula["explanation"]:
                        markdown.append(f"{formula['explanation']}\n\n")

            # Add diagrams
            if "diagrams" in content and content["diagrams"]:
                markdown.append("\n### Diagrams\n")
                for diagram_idx, diagram in enumerate(content["diagrams"]):
                    if "description" in diagram and diagram["description"]:
                        markdown.append(f"**{diagram['description']}**\n\n")
                    if "explanation" in diagram and diagram["explanation"]:
                        markdown.append(f"{diagram['explanation']}\n\n")
        else:
            # Fallback for raw content
            if "raw_content" in page:
                markdown.append(f"{page['raw_content']}\n\n")

    return "".join(markdown)

@task(name="chunk_vlm_markdown")
def chunk_vlm_markdown(
    markdown_content: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200
) -> List[Dict[str, Any]]:
    """Chunk the markdown content into smaller pieces.

    Args:
        markdown_content: Markdown content to chunk
        chunk_size: Maximum number of characters per chunk
        chunk_overlap: Number of characters to overlap between chunks

    Returns:
        List of chunked content with metadata
    """
    logger.info(f"Chunking markdown content with chunk size: {chunk_size}, overlap: {chunk_overlap}")

    # Split by headers to preserve document structure
    import re
    header_pattern = r"(^#{1,6}\s.+$)"
    sections = re.split(header_pattern, markdown_content, flags=re.MULTILINE)

    chunks = []
    current_chunk = ""
    current_metadata = {}
    current_page = None

    for i in range(0, len(sections)):
        section = sections[i]
        if not section.strip():
            continue

        # Check if this is a header
        header_match = re.match(r"^(#{1,6})\s(.+)$", section)
        if header_match:
            level = len(header_match.group(1))
            title = header_match.group(2).strip()

            # Check for page headers to track current page
            page_match = re.match(r"Page (\d+)", title)
            if page_match:
                current_page = int(page_match.group(1))
                current_metadata["page"] = current_page

            # Update metadata with header info
            if level == 1:
                current_metadata["title"] = title
            elif level == 2 and not page_match:
                current_metadata["section"] = title
            elif level == 3:
                current_metadata["subsection"] = title

        # Check if adding this section would exceed chunk size
        if len(current_chunk) + len(section) + 1 > chunk_size and current_chunk:
            # Save current chunk and start a new one
            chunks.append({
                "text": current_chunk,
                "metadata": current_metadata.copy()
            })

            # Start new chunk with overlap
            if chunk_overlap > 0 and current_chunk:
                # Get the last part of the previous chunk for overlap
                overlap_chars = min(chunk_overlap, len(current_chunk))
                current_chunk = current_chunk[-overlap_chars:]
            else:
                current_chunk = ""

        current_chunk += section + "\n"

    # Add the last chunk if not empty
    if current_chunk:
        chunks.append({
            "text": current_chunk,
            "metadata": current_metadata.copy()
        })

    logger.info(f"Chunking completed. Created {len(chunks)} chunks.")
    return chunks

@flow(name="VLM PDF Parsing Flow")
def vlm_pdf_parsing_flow(
    pdf_path: str,
    api_key: str,
    model: str = "gpt-4-vision-preview",  # Example model, replace with actual VLM model
    api_url: str = "https://api.openai.com/v1/chat/completions",  # Example API URL
    dpi: int = 300,
    start_page: int = 0,
    end_page: Optional[int] = None,
    max_tokens: int = 4000,
    temperature: float = 0.2,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    prompt_template: Optional[str] = None
) -> Dict[str, Any]:
    """Prefect flow for parsing PDFs using Vision Language Models (VLMs).

    Args:
        pdf_path: Path to the PDF file
        api_key: API key for the VLM service
        model: Name of the VLM model to use
        api_url: URL for the VLM API
        dpi: Resolution for the output images
        start_page: First page to process (0-based index)
        end_page: Last page to process (0-based index, None for all pages)
        max_tokens: Maximum number of tokens in the VLM response
        temperature: Temperature for the model's output
        chunk_size: Maximum number of characters per chunk
        chunk_overlap: Number of characters to overlap between chunks
        prompt_template: Template for the prompt to the VLM

    Returns:
        Dictionary containing the parsed and chunked content
    """
    # Check dependencies
    dependencies_ok = check_vlm_dependencies()
    if not dependencies_ok:
        return {"error": "Required packages are not installed"}

    # Validate PDF path
    if not os.path.exists(pdf_path):
        return {"error": f"PDF file not found: {pdf_path}"}

    # Extract basic metadata
    metadata = {
        "file_name": os.path.basename(pdf_path),
        "file_size": os.path.getsize(pdf_path),
        "file_path": pdf_path
    }

    # Convert PDF pages to images
    images = convert_pdf_to_images(
        pdf_path=pdf_path,
        dpi=dpi,
        start_page=start_page,
        end_page=end_page
    )

    # Update metadata with page count
    metadata["page_count"] = len(images)

    # Process each page with the VLM
    vlm_results = []
    for image_data in images:
        result = process_image_with_vlm(
            image_data=image_data,
            api_key=api_key,
            model=model,
            api_url=api_url,
            max_tokens=max_tokens,
            temperature=temperature,
            prompt_template=prompt_template
        )
        vlm_results.append(result)

    # Combine results from all pages
    combined_doc = combine_vlm_results(
        vlm_results=vlm_results,
        metadata=metadata
    )

    # Convert to markdown
    markdown_content = convert_vlm_results_to_markdown(combined_doc)

    # Chunk the content
    chunked_content = chunk_vlm_markdown(
        markdown_content=markdown_content,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )

    # Prepare result
    result = {
        "pdf_path": pdf_path,
        "metadata": metadata,
        "model": model,
        "page_count": len(vlm_results),
        "chunks_count": len(chunked_content),
        "chunks": chunked_content,
        "markdown": markdown_content
    }

    return result

# Example usage
if __name__ == "__main__":
    # Example PDF path
    pdf_path = "path/to/your/document.pdf"

    # Example API key (replace with your actual API key)
    api_key = "your-api-key-here"

    # Run the flow
    result = vlm_pdf_parsing_flow(
        pdf_path=pdf_path,
        api_key=api_key,
        model="gpt-4-vision-preview",  # Example model
        start_page=0,  # Start from first page
        end_page=2,  # Process first 3 pages (0, 1, 2)
        dpi=300,
        max_tokens=4000,
        temperature=0.2,
        chunk_size=1000,
        chunk_overlap=200
    )

    # Print summary
    print(f"Processed PDF: {result['pdf_path']}")
    print(f"Model used: {result['model']}")
    print(f"Pages processed: {result['page_count']}")
    print(f"Chunks created: {result['chunks_count']}")

    # Print first chunk as example
    if result['chunks']:
        first_chunk = result['chunks'][0]
        print("\nExample chunk:")
        print(f"Text: {first_chunk['text'][:200]}...")
        print(f"Metadata: {first_chunk['metadata']}")
```

This implementation provides a comprehensive workflow for parsing PDFs using Vision Language Models (VLMs) with the following features:

- PDF to image conversion with configurable resolution
- Integration with VLM APIs (e.g., GPT-4 Vision)
- Structured JSON output with text, tables, images, formulas, and diagrams
- Customizable prompting for different extraction needs
- Conversion to markdown for easy viewing and integration
- Intelligent chunking with configurable size and overlap
- Metadata preservation and enrichment
- Proper error handling and logging
- Wrapped in a Prefect flow for easy integration into data pipelines
