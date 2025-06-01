"""
Pipeline Generator
Generates complete data pipeline code by combining selected components
"""

from typing import Dict, List, Any, Optional
from pathlib import Path
import json
from datetime import datetime

class PipelineGenerator:
    """Generates complete data pipeline code from selected components."""
    
    def __init__(self):
        self.template_header = '''"""
Generated Data Pipeline
Created by Multi-Agent Pipeline System
Generated on: {timestamp}

This pipeline was automatically generated based on your requirements.
Please ensure you have all required API keys and dependencies installed.
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from prefect import task, flow
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

'''
    
    def generate_pipeline(self, 
                         components: Dict[str, str],
                         config: Dict[str, Any],
                         pipeline_name: str = "custom_data_pipeline") -> str:
        """
        Generate a complete pipeline from components.
        
        Args:
            components: Dictionary of component code blocks
            config: Configuration parameters
            pipeline_name: Name for the main pipeline
            
        Returns:
            Complete pipeline code as string
        """
        
        # Start with header
        pipeline_code = self.template_header.format(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        # Add configuration section
        pipeline_code += self._generate_config_section(config)
        
        # Add component imports and functions
        pipeline_code += self._combine_components(components)
        
        # Add main pipeline flow
        pipeline_code += self._generate_main_flow(components, pipeline_name)
        
        # Add execution section
        pipeline_code += self._generate_execution_section(pipeline_name)
        
        return pipeline_code
    
    def _generate_config_section(self, config: Dict[str, Any]) -> str:
        """Generate configuration section."""
        config_code = '''
# Configuration
CONFIG = {
'''
        
        for key, value in config.items():
            if isinstance(value, str):
                config_code += f'    "{key}": "{value}",\n'
            else:
                config_code += f'    "{key}": {value},\n'
        
        config_code += '''
}

def load_config():
    """Load configuration from environment variables or config file."""
    config = CONFIG.copy()
    
    # Override with environment variables if available
    for key in config:
        env_key = key.upper()
        if env_key in os.environ:
            config[key] = os.environ[env_key]
    
    return config

'''
        return config_code
    
    def _combine_components(self, components: Dict[str, str]) -> str:
        """Combine all component code blocks."""
        combined_code = "\n# Component Functions\n"
        
        # Extract and combine all code blocks
        for component_name, code in components.items():
            combined_code += f"\n# {component_name.upper()} COMPONENT\n"
            combined_code += self._clean_code_block(code)
            combined_code += "\n"
        
        return combined_code
    
    def _clean_code_block(self, code: str) -> str:
        """Clean and format code block."""
        lines = code.split('\n')
        cleaned_lines = []
        
        in_code_block = False
        for line in lines:
            # Skip markdown code block markers
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                continue
            
            # Skip markdown headers and comments outside code blocks
            if not in_code_block and (line.strip().startswith('#') or line.strip().startswith('##')):
                continue
            
            if in_code_block or line.strip():
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _generate_main_flow(self, components: Dict[str, str], pipeline_name: str) -> str:
        """Generate the main orchestrating flow."""
        main_flow = f'''
@flow(name="{pipeline_name}")
def {pipeline_name}_flow(
    config_override: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Main data pipeline flow that orchestrates all components.
    
    Args:
        config_override: Optional configuration overrides
        
    Returns:
        Dictionary containing pipeline results
    """
    # Load configuration
    config = load_config()
    if config_override:
        config.update(config_override)
    
    logger.info(f"Starting {pipeline_name} pipeline")
    results = {{}}
    
    try:
'''
        
        # Add component execution based on what's available
        if "data_loading" in components:
            main_flow += '''
        # Data Loading Phase
        logger.info("Starting data loading phase")
        loaded_data = data_loading_task(config)
        results["loaded_data"] = loaded_data
        logger.info(f"Loaded {len(loaded_data)} documents")
'''
        
        if "chunking" in components:
            main_flow += '''
        # Chunking Phase
        logger.info("Starting chunking phase")
        chunks = chunking_task(loaded_data, config)
        results["chunks"] = chunks
        logger.info(f"Created {len(chunks)} chunks")
'''
        
        if "embedding" in components:
            main_flow += '''
        # Embedding Phase
        logger.info("Starting embedding phase")
        embeddings = embedding_task(chunks, config)
        results["embeddings"] = embeddings
        logger.info(f"Generated embeddings for {len(embeddings)} chunks")
'''
        
        if "vector_store" in components:
            main_flow += '''
        # Vector Store Phase
        logger.info("Starting vector store phase")
        vector_store_result = vector_store_task(chunks, embeddings, config)
        results["vector_store"] = vector_store_result
        logger.info("Data stored in vector database")
'''
        
        if "llm" in components:
            main_flow += '''
        # LLM Setup Phase
        logger.info("Setting up LLM for RAG")
        llm_setup = llm_setup_task(config)
        results["llm_setup"] = llm_setup
        logger.info("LLM configured for retrieval and generation")
'''
        
        main_flow += '''
        logger.info(f"{pipeline_name} pipeline completed successfully")
        return results
        
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        raise

'''
        return main_flow
    
    def _generate_execution_section(self, pipeline_name: str) -> str:
        """Generate the execution section."""
        execution_code = f'''
# RAG Query Function
@task(name="rag_query_task")
def rag_query_task(query: str, config: Dict[str, Any]) -> str:
    """
    Perform RAG query using the configured pipeline.
    
    Args:
        query: User query
        config: Pipeline configuration
        
    Returns:
        Generated response
    """
    # This function should be customized based on your specific RAG setup
    # It should retrieve relevant chunks and generate a response using the LLM
    logger.info(f"Processing query: {{query}}")
    
    # Placeholder implementation - customize based on your components
    response = "This is a placeholder response. Customize this function based on your RAG setup."
    
    return response

@flow(name="rag_query_flow")
def rag_query_flow(query: str, config_override: Optional[Dict[str, Any]] = None) -> str:
    """
    Flow for performing RAG queries.
    
    Args:
        query: User query
        config_override: Optional configuration overrides
        
    Returns:
        Generated response
    """
    config = load_config()
    if config_override:
        config.update(config_override)
    
    return rag_query_task(query, config)

if __name__ == "__main__":
    # Example usage
    print("Running {pipeline_name} pipeline...")
    
    # Run the main pipeline
    result = {pipeline_name}_flow()
    print("Pipeline completed successfully!")
    print(f"Results: {{result}}")
    
    # Example RAG query
    query = "What information do you have about the documents?"
    response = rag_query_flow(query)
    print(f"Query: {{query}}")
    print(f"Response: {{response}}")
'''
        return execution_code

class ConfigurationManager:
    """Manages configuration templates and API key requirements."""
    
    def __init__(self):
        self.api_key_descriptions = {
            "OPENAI_API_KEY": "OpenAI API key for GPT models and embeddings",
            "AZURE_OPENAI_API_KEY": "Azure OpenAI API key",
            "AZURE_OPENAI_ENDPOINT": "Azure OpenAI endpoint URL",
            "COHERE_API_KEY": "Cohere API key for embeddings and models",
            "JINA_API_KEY": "Jina AI API key for embeddings",
            "GEMINI_API_KEY": "Google Gemini API key",
            "PINECONE_API_KEY": "Pinecone vector database API key",
            "QDRANT_URL": "Qdrant database URL",
            "QDRANT_API_KEY": "Qdrant API key (if using cloud)",
            "WEAVIATE_URL": "Weaviate database URL",
            "WEAVIATE_API_KEY": "Weaviate API key",
            "TAVILY_API_KEY": "Tavily web search API key",
            "SERPER_API_KEY": "Serper Google Search API key",
            "SLACK_USER_TOKEN": "Slack user token for integration",
            "JIRA_API_TOKEN": "Jira API token",
            "JIRA_USERNAME": "Jira username",
            "JIRA_INSTANCE_URL": "Jira instance URL",
            "LLAMAPARSE_API_KEY": "LlamaParse API key for document parsing"
        }
    
    def generate_config_template(self, required_keys: List[str]) -> str:
        """Generate a configuration template file."""
        template = '''# Configuration Template
# Fill in your API keys and configuration values

'''
        
        for key in required_keys:
            description = self.api_key_descriptions.get(key, "API key or configuration value")
            template += f'# {description}\n'
            template += f'{key}=your_{key.lower()}_here\n\n'
        
        template += '''
# Additional Configuration
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
MAX_RESULTS=10
TEMPERATURE=0.7

# Instructions:
# 1. Replace the placeholder values with your actual API keys
# 2. Save this file as .env in your project directory
# 3. Install python-dotenv: pip install python-dotenv
# 4. Load environment variables in your code: from dotenv import load_dotenv; load_dotenv()
'''
        
        return template
    
    def get_api_key_instructions(self, required_keys: List[str]) -> str:
        """Generate instructions for obtaining API keys."""
        instructions = "# API Key Instructions\n\n"
        
        key_sources = {
            "OPENAI_API_KEY": "https://platform.openai.com/api-keys",
            "AZURE_OPENAI_API_KEY": "https://portal.azure.com/",
            "COHERE_API_KEY": "https://dashboard.cohere.ai/api-keys",
            "JINA_API_KEY": "https://jina.ai/",
            "GEMINI_API_KEY": "https://makersuite.google.com/app/apikey",
            "PINECONE_API_KEY": "https://app.pinecone.io/",
            "TAVILY_API_KEY": "https://tavily.com/",
            "SERPER_API_KEY": "https://serper.dev/",
            "LLAMAPARSE_API_KEY": "https://cloud.llamaindex.ai/"
        }
        
        for key in required_keys:
            if key in key_sources:
                instructions += f"## {key}\n"
                instructions += f"Get your API key from: {key_sources[key]}\n"
                instructions += f"Description: {self.api_key_descriptions.get(key, 'API key')}\n\n"
        
        return instructions
