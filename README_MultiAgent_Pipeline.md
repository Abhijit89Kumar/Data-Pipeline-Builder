# Multi-Agent Data Pipeline System

A sophisticated multi-agent system built with AutoGen that automatically generates custom data pipelines by intelligently selecting and combining code components from the Data_Eng_Database directory.

## 🌟 Features

- **Intelligent Planning**: AI planner agent analyzes requirements and creates optimal pipeline architecture
- **Specialized Agents**: Each agent specializes in specific components (data loading, chunking, embeddings, etc.)
- **Code Reuse**: Leverages existing Prefect-based code from Data_Eng_Database
- **Multiple Options**: Supports various PDF parsers, chunking strategies, embedding models, vector stores, and LLMs
- **Configuration Management**: Automatic API key management and configuration templates
- **Web Interface**: Optional Streamlit interface for easy interaction
- **Complete Pipelines**: Generates ready-to-run Python files with proper error handling

## 🏗️ System Architecture

### Agent Roles

1. **PlannerAgent**: Analyzes user requirements and creates technical plans
2. **DataLoadingAgent**: Selects PDF parsing and web scraping strategies
3. **ChunkingAgent**: Chooses optimal text chunking approaches
4. **EmbeddingAgent**: Selects appropriate embedding models
5. **VectorStoreAgent**: Configures vector database solutions
6. **LLMAgent**: Sets up language models for RAG
7. **ToolsAgent**: Manages external API integrations
8. **APIManagerAgent**: Handles credentials and configuration
9. **PipelineBuilderAgent**: Assembles final pipeline code

### Supported Components

#### PDF Parsing Strategies
- **Unstructured**: General documents with image support
- **LlamaParse**: Premium parsing with advanced layout understanding
- **PyMuPDF4LLM**: Fast and efficient for text-heavy documents
- **Docling**: Advanced document understanding with OCR
- **VLM**: Vision Language Model based parsing for complex layouts

#### Chunking Strategies
- **Fixed-Size**: Simple, consistent chunk sizes with overlap
- **Recursive**: Hierarchical splitting with specialized splitters
- **Semantic**: Groups semantically related content
- **Smart/Adaptive**: Adapts to document structure
- **Sliding-Window**: Overlapping windows for context preservation

#### Embedding Providers
- **OpenAI**: High quality, general purpose
- **Azure OpenAI**: Enterprise-grade OpenAI embeddings
- **Cohere**: Multilingual and specialized domains
- **Jina**: Optimized for various tasks
- **Gemini**: Google's embedding models

#### Vector Stores
- **Pinecone**: Managed vector database for production
- **Qdrant**: Open source, self-hosting friendly
- **Weaviate**: Feature-rich with built-in vectorization
- **Chroma**: Simple and lightweight for development

#### LLM Providers
- **Azure OpenAI**: Enterprise-grade GPT models
- **AWS Bedrock**: Various models (Claude, Llama, etc.)
- **Groq**: Fast inference for supported models

#### External Tools
- **Tavily**: Web search and content extraction
- **Serper**: Google Search API integration
- **Slack**: Team communication integration
- **Jira**: Project management integration

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd data_Eng_db-main

# Install dependencies
pip install -r requirements.txt
```

### 2. Run Demo

```bash
# Run the demo to see how it works
python demo_pipeline_system.py
```

### 3. Basic Usage

```python
from multi_agent_pipeline_system import DataPipelineAgentSystem

# Initialize the system
system = DataPipelineAgentSystem()

# Define your requirements
user_requirements = """
I want to build a pipeline that processes PDF documents 
and creates a RAG system for question answering
"""

# Generate pipeline
result = system.create_pipeline(user_requirements)

print(f"Pipeline saved to: {result['filename']}")
print(f"Components used: {result['components_used']}")
```

### 4. Web Interface

```bash
# Launch the Streamlit web interface
python multi_agent_pipeline_system.py web

# Or directly with streamlit
streamlit run multi_agent_pipeline_system.py
```

## 📋 Configuration

### Azure OpenAI Setup

Update the configuration in `multi_agent_pipeline_system.py`:

```python
AZURE_CONFIG = {
    "model": "gpt-4o",
    "api_type": "azure", 
    "base_url": "https://your-endpoint.openai.azure.com/",
    "api_key": "your-api-key",
    "api_version": "2023-05-15"
}
```

### API Keys Required

The system will automatically detect which API keys you need based on your pipeline configuration:

- `OPENAI_API_KEY`: For OpenAI embeddings/models
- `AZURE_OPENAI_API_KEY`: For Azure OpenAI services
- `AZURE_OPENAI_ENDPOINT`: Azure OpenAI endpoint URL
- `PINECONE_API_KEY`: For Pinecone vector database
- `COHERE_API_KEY`: For Cohere embeddings
- `TAVILY_API_KEY`: For web search capabilities
- And more based on selected components...

## 🎯 Example Use Cases

### 1. Document Q&A System
```python
user_requirements = """
Build a pipeline that processes PDF documents and creates 
a question-answering system using historical documents as reference
"""
```

### 2. Web Content RAG
```python
user_requirements = """
Create a pipeline that scrapes web content, chunks it semantically,
and builds a RAG system for content-based queries
"""
```

### 3. Multi-Modal Document Processing
```python
user_requirements = """
Process documents with complex layouts including tables and images,
use VLM parsing, and create embeddings for visual content
"""
```

## 📁 Generated Output

The system generates three files for each pipeline:

1. **`{name}.py`**: Complete pipeline code with Prefect flows
2. **`{name}_config.env`**: Configuration template with required API keys
3. **`{name}_instructions.md`**: Instructions for obtaining API keys

## 🔧 Advanced Usage

### Custom Pipeline Plans

```python
# Create a custom plan instead of using the planner agent
custom_plan = {
    "data_sources": ["pdf", "web_scraping"],
    "pdf_parsing_strategy": "llamaparse",
    "chunking_strategy": "semantic",
    "embedding_provider": "cohere",
    "vector_store": "qdrant",
    "llm_provider": "azure_openai",
    "external_tools": ["tavily"],
    "use_case": "rag",
    "requirements": {
        "chunk_size": 1500,
        "chunk_overlap": 300,
        "max_results": 15,
        "temperature": 0.5
    }
}

result = system.create_custom_pipeline(custom_plan)
```

### Available Options

```python
# Get all available component options
options = system.get_available_options()
print(options)
```

## 🧪 Testing

```bash
# Run the demo
python demo_pipeline_system.py

# Test with different requirements
python -c "
from multi_agent_pipeline_system import DataPipelineAgentSystem
system = DataPipelineAgentSystem()
result = system.create_pipeline('Build a semantic search system for research papers')
print('Success!')
"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add new components to the appropriate Data_Eng_Database subdirectory
4. Update the agent system to recognize new components
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the generated instructions file for API key setup
2. Review the demo script for usage examples
3. Ensure all required dependencies are installed
4. Verify your Azure OpenAI configuration

## 🔮 Future Enhancements

- Support for more embedding providers
- Additional vector database integrations
- Custom agent creation capabilities
- Pipeline optimization suggestions
- Automated testing and validation
- Cost estimation and optimization
