"""
Code Selector Utilities
Helper functions for agents to select and customize code from the Data_Eng_Database
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Any, Optional

class CodeSelector:
    """Utility class for selecting and customizing code from the database."""
    
    def __init__(self, database_path: str = "Data_Eng_Database"):
        self.database_path = Path(database_path)
        
    def get_pdf_parsing_code(self, strategy: str) -> str:
        """Get PDF parsing code for a specific strategy."""
        pdf_code_file = self.database_path / "data_loading" / "pdf_parsing_code.md"
        
        if not pdf_code_file.exists():
            raise FileNotFoundError(f"PDF parsing code file not found: {pdf_code_file}")
            
        content = pdf_code_file.read_text(encoding='utf-8')
        
        # Extract specific strategy code
        strategy_map = {
            "unstructured": "## Unstructured",
            "llamaparse": "## LlamaParse", 
            "pymupdf4llm": "## PyMuPDF4LLM",
            "docling": "## Docling",
            "vlm": "## VLM Based PDF Parsing"
        }
        
        if strategy.lower() not in strategy_map:
            raise ValueError(f"Unknown PDF parsing strategy: {strategy}")
            
        return self._extract_section(content, strategy_map[strategy.lower()])
    
    def get_web_scraping_code(self) -> str:
        """Get web scraping code."""
        web_code_file = self.database_path / "data_loading" / "web_scraping_code.md"
        
        if not web_code_file.exists():
            raise FileNotFoundError(f"Web scraping code file not found: {web_code_file}")
            
        return web_code_file.read_text(encoding='utf-8')
    
    def get_chunking_code(self, strategy: str) -> str:
        """Get chunking code for a specific strategy."""
        chunking_code_file = self.database_path / "chunking" / "chunking_strategies_code.md"
        
        if not chunking_code_file.exists():
            raise FileNotFoundError(f"Chunking code file not found: {chunking_code_file}")
            
        content = chunking_code_file.read_text(encoding='utf-8')
        
        strategy_map = {
            "fixed_size": "## Fixed-Size Chunking",
            "recursive": "## Recursive Chunking", 
            "semantic": "## Semantic Chunking",
            "smart": "## Smart/Adaptive Chunking",
            "sliding_window": "## Sliding-Window Chunking"
        }
        
        if strategy.lower() not in strategy_map:
            raise ValueError(f"Unknown chunking strategy: {strategy}")
            
        return self._extract_section(content, strategy_map[strategy.lower()])
    
    def get_embedding_code(self, provider: str) -> str:
        """Get embedding code for a specific provider."""
        embedding_code_file = self.database_path / "embeddings" / "embeddings_code.md"
        
        if not embedding_code_file.exists():
            raise FileNotFoundError(f"Embedding code file not found: {embedding_code_file}")
            
        content = embedding_code_file.read_text(encoding='utf-8')
        
        # Extract specific provider code based on flow names
        provider_map = {
            "openai": "sentence_embedding_flow",  # Using the available sentence embedding flow
            "cohere": "cohere_embedding_flow",
            "jina": "jina_embeddings_flow",
            "gemini": "gemini_embeddings_flow",
            "azure": "azure_openai_embeddings_flow"
        }
        
        if provider.lower() not in provider_map:
            raise ValueError(f"Unknown embedding provider: {provider}")
            
        flow_name = provider_map[provider.lower()]
        return self._extract_flow_code(content, flow_name)
    
    def get_vector_store_code(self, store_type: str) -> str:
        """Get vector store code for a specific type."""
        vector_code_file = self.database_path / "vector_stores" / "vector_store_code.md"
        
        if not vector_code_file.exists():
            raise FileNotFoundError(f"Vector store code file not found: {vector_code_file}")
            
        content = vector_code_file.read_text(encoding='utf-8')
        
        # Extract specific vector store code
        store_map = {
            "pinecone": "# PINECONE",
            "qdrant": "# QDRANT",
            "weaviate": "```python",  # Weaviate code starts at the beginning
            "chroma": "# QDRANT"  # Use Qdrant as fallback for Chroma since it's not available
        }
        
        if store_type.lower() not in store_map:
            raise ValueError(f"Unknown vector store type: {store_type}")
            
        return self._extract_section(content, store_map[store_type.lower()])
    
    def get_llm_code(self, provider: str) -> str:
        """Get LLM code for a specific provider."""
        llm_code_file = self.database_path / "llms" / "llm_code.md"
        
        if not llm_code_file.exists():
            raise FileNotFoundError(f"LLM code file not found: {llm_code_file}")
            
        content = llm_code_file.read_text(encoding='utf-8')
        
        # Extract specific provider code
        provider_map = {
            "azure_openai": "azure_openai_flow",
            "bedrock": "bedrock_flow",
            "groq": "groq_flow"
        }
        
        if provider.lower() not in provider_map:
            raise ValueError(f"Unknown LLM provider: {provider}")
            
        flow_name = provider_map[provider.lower()]
        return self._extract_flow_code(content, flow_name)
    
    def get_tools_code(self, tool_type: str) -> str:
        """Get tools code for a specific type."""
        if tool_type.lower() == "websearch":
            tools_code_file = self.database_path / "tools" / "websearch_code.md"
        elif tool_type.lower() == "productivity":
            tools_code_file = self.database_path / "tools" / "productivity_code.md"
        else:
            raise ValueError(f"Unknown tool type: {tool_type}")
            
        if not tools_code_file.exists():
            raise FileNotFoundError(f"Tools code file not found: {tools_code_file}")
            
        return tools_code_file.read_text(encoding='utf-8')
    
    def _extract_section(self, content: str, section_header: str) -> str:
        """Extract a section from markdown content."""
        lines = content.split('\n')
        start_idx = None
        end_idx = None
        
        for i, line in enumerate(lines):
            if line.strip().startswith(section_header):
                start_idx = i
            elif start_idx is not None and line.strip().startswith('##') and not line.strip().startswith(section_header):
                end_idx = i
                break
        
        if start_idx is None:
            raise ValueError(f"Section '{section_header}' not found")
            
        if end_idx is None:
            end_idx = len(lines)
            
        return '\n'.join(lines[start_idx:end_idx])
    
    def _extract_flow_code(self, content: str, flow_name: str) -> str:
        """Extract code for a specific Prefect flow."""
        # Look for @flow decorator with the flow name
        pattern = rf'@flow\(name="{flow_name}"\)'
        lines = content.split('\n')
        
        start_idx = None
        for i, line in enumerate(lines):
            if re.search(pattern, line):
                start_idx = i
                break
        
        if start_idx is None:
            raise ValueError(f"Flow '{flow_name}' not found")
        
        # Find the end of the function (next @flow or @task decorator)
        end_idx = len(lines)
        for i in range(start_idx + 1, len(lines)):
            if lines[i].strip().startswith('@flow') or lines[i].strip().startswith('@task'):
                end_idx = i
                break
        
        # Also include any @task functions that come before the flow
        task_start_idx = start_idx
        for i in range(start_idx - 1, -1, -1):
            if lines[i].strip().startswith('@task'):
                task_start_idx = i
            elif lines[i].strip().startswith('@flow'):
                break
        
        return '\n'.join(lines[task_start_idx:end_idx])

class CodeCustomizer:
    """Utility class for customizing code based on requirements."""
    
    @staticmethod
    def customize_parameters(code: str, parameter_updates: Dict[str, Any]) -> str:
        """Customize function parameters in code."""
        for param_name, new_value in parameter_updates.items():
            # Handle different parameter types
            if isinstance(new_value, str):
                pattern = rf'{param_name}:\s*str\s*=\s*["\'][^"\']*["\']'
                replacement = f'{param_name}: str = "{new_value}"'
            elif isinstance(new_value, int):
                pattern = rf'{param_name}:\s*int\s*=\s*\d+'
                replacement = f'{param_name}: int = {new_value}'
            elif isinstance(new_value, float):
                pattern = rf'{param_name}:\s*float\s*=\s*[\d.]+'
                replacement = f'{param_name}: float = {new_value}'
            elif isinstance(new_value, bool):
                pattern = rf'{param_name}:\s*bool\s*=\s*(True|False)'
                replacement = f'{param_name}: bool = {new_value}'
            else:
                continue
                
            code = re.sub(pattern, replacement, code)
        
        return code
    
    @staticmethod
    def add_imports(code: str, additional_imports: List[str]) -> str:
        """Add additional imports to code."""
        lines = code.split('\n')
        
        # Find where to insert imports (after existing imports)
        insert_idx = 0
        for i, line in enumerate(lines):
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                insert_idx = i + 1
        
        # Insert new imports
        for import_stmt in additional_imports:
            lines.insert(insert_idx, import_stmt)
            insert_idx += 1
        
        return '\n'.join(lines)
    
    @staticmethod
    def update_flow_name(code: str, new_flow_name: str) -> str:
        """Update the flow name in code."""
        pattern = r'@flow\(name="[^"]*"\)'
        replacement = f'@flow(name="{new_flow_name}")'
        return re.sub(pattern, replacement, code)
