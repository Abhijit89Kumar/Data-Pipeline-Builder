"""
Multi-Agent Data Pipeline System
A system that uses AutoGen agents to build custom data pipelines by selecting and combining
code from the Data_Eng_Database directory.
"""

import os
import json
import asyncio
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
import autogen
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager

# Azure OpenAI Configuration
AZURE_CONFIG = {} #Use your cnfig here

class DataPipelineAgentSystem:
    """Main orchestrator for the multi-agent data pipeline system."""
    
    def __init__(self):
        self.agents = {}
        self.code_database_path = Path("Data_Eng_Database")
        self.output_path = Path("generated_pipelines")
        self.output_path.mkdir(exist_ok=True)
        
        # Initialize all agents
        self._initialize_agents()
        
    def _initialize_agents(self):
        """Initialize all specialized agents."""
        
        # Planner Agent
        self.agents["planner"] = AssistantAgent(
            name="PlannerAgent",
            system_message="""You are a Data Pipeline Planner Agent. Your role is to:
1. Analyze user requirements for data pipelines
2. Break down the requirements into specific components
3. Create a detailed plan specifying which agents should handle which parts
4. Coordinate the overall pipeline architecture

When a user describes their pipeline needs, create a structured plan that includes:
- Data sources (PDFs, web scraping, etc.)
- Processing requirements (chunking strategy, embedding model)
- Storage requirements (vector database type)
- Retrieval and generation requirements (LLM model, RAG setup)
- External integrations needed
- API keys and configuration needed

Respond with a JSON structure containing the plan.""",
            llm_config={"config_list": [AZURE_CONFIG]}
        )
        
        # Data Loading Agent
        self.agents["data_loader"] = AssistantAgent(
            name="DataLoadingAgent", 
            system_message="""You are a Data Loading Agent. Your role is to:
1. Select appropriate PDF parsing strategies (Unstructured, LlamaParse, PyMuPDF4LLM, Docling, VLM)
2. Select web scraping approaches (RecursiveUrlLoader)
3. Modify and customize the code from Data_Eng_Database/data_loading/ based on requirements
4. Ensure proper Prefect flow integration

Available PDF parsing options:
- Unstructured: Good for general documents, supports images
- LlamaParse: Premium parsing with advanced layout understanding
- PyMuPDF4LLM: Fast and efficient for text-heavy documents
- Docling: Advanced document understanding with OCR
- VLM: Vision Language Model based parsing for complex layouts

Available web scraping:
- RecursiveUrlLoader: For crawling websites with depth control

Return the selected and customized code blocks.""",
            llm_config={"config_list": [AZURE_CONFIG]}
        )
        
        # Chunking Agent
        self.agents["chunker"] = AssistantAgent(
            name="ChunkingAgent",
            system_message="""You are a Chunking Strategy Agent. Your role is to:
1. Select appropriate chunking strategies from Data_Eng_Database/chunking/
2. Customize chunk sizes, overlap, and splitting methods based on requirements
3. Ensure compatibility with the chosen embedding model and use case

Available chunking strategies:
- Fixed-Size Chunking: Simple, consistent chunk sizes with overlap
- Recursive Chunking: Hierarchical splitting with specialized splitters
- Semantic Chunking: Groups semantically related content
- Smart/Adaptive Chunking: Adapts to document structure
- Sliding-Window Chunking: Overlapping windows for context preservation

Consider the document type, embedding model context window, and downstream use case.""",
            llm_config={"config_list": [AZURE_CONFIG]}
        )
        
        # Embedding Agent
        self.agents["embedder"] = AssistantAgent(
            name="EmbeddingAgent",
            system_message="""You are an Embedding Agent. Your role is to:
1. Select appropriate embedding models from Data_Eng_Database/embeddings/
2. Customize embedding parameters based on requirements
3. Ensure compatibility with the chosen vector database

Available embedding options:
- OpenAI Embeddings: High quality, good for general use
- Cohere Embeddings: Good for multilingual and specialized domains
- Jina Embeddings: Optimized for various tasks
- Gemini Embeddings: Google's embedding models
- Azure OpenAI Embeddings: Enterprise-grade OpenAI embeddings

Consider factors like embedding dimensions, cost, latency, and domain specificity.""",
            llm_config={"config_list": [AZURE_CONFIG]}
        )
        
        # Vector Store Agent
        self.agents["vector_store"] = AssistantAgent(
            name="VectorStoreAgent",
            system_message="""You are a Vector Store Agent. Your role is to:
1. Select appropriate vector databases from Data_Eng_Database/vector_stores/
2. Configure storage and retrieval parameters
3. Ensure compatibility with chosen embedding dimensions

Available vector stores:
- Pinecone: Managed vector database, good for production
- Qdrant: Open source, good for self-hosting
- Weaviate: Feature-rich with built-in vectorization
- Chroma: Simple and lightweight for development

Consider factors like scalability, cost, features, and deployment requirements.""",
            llm_config={"config_list": [AZURE_CONFIG]}
        )
        
        # LLM Agent
        self.agents["llm"] = AssistantAgent(
            name="LLMAgent",
            system_message="""You are an LLM Agent. Your role is to:
1. Select appropriate language models from Data_Eng_Database/llms/
2. Configure model parameters for the specific use case
3. Set up RAG (Retrieval Augmented Generation) workflows

Available LLM options:
- Azure OpenAI: Enterprise-grade GPT models
- AWS Bedrock: Various models (Claude, Llama, etc.)
- Groq: Fast inference for supported models
- Local models: For privacy-sensitive applications

Consider factors like model capabilities, cost, latency, and privacy requirements.""",
            llm_config={"config_list": [AZURE_CONFIG]}
        )
        
        # Tools Agent
        self.agents["tools"] = AssistantAgent(
            name="ToolsAgent",
            system_message="""You are a Tools Agent. Your role is to:
1. Select and configure external tools from Data_Eng_Database/tools/
2. Set up integrations for web search, productivity tools, etc.
3. Configure API connections and parameters

Available tools:
- Tavily: Web search and content extraction
- Serper: Google Search API integration
- Slack: Team communication integration
- Jira: Project management integration

Configure these tools based on the pipeline requirements.""",
            llm_config={"config_list": [AZURE_CONFIG]}
        )
        
        # API Key Manager Agent
        self.agents["api_manager"] = AssistantAgent(
            name="APIManagerAgent",
            system_message="""You are an API Key Manager Agent. Your role is to:
1. Identify all required API keys and credentials for the pipeline
2. Create a configuration template for users to fill in their credentials
3. Ensure secure handling of sensitive information
4. Provide clear instructions for obtaining required API keys

Create a comprehensive configuration file that includes:
- All required API keys with descriptions
- Optional API keys for enhanced features
- Environment variable names
- Instructions for obtaining each API key""",
            llm_config={"config_list": [AZURE_CONFIG]}
        )
        
        # Pipeline Builder Agent
        self.agents["builder"] = AssistantAgent(
            name="PipelineBuilderAgent",
            system_message="""You are a Pipeline Builder Agent. Your role is to:
1. Combine all selected code components into a cohesive pipeline
2. Ensure proper imports and dependencies
3. Create a main Prefect flow that orchestrates all components
4. Add error handling and logging
5. Generate a complete, runnable Python file

The final pipeline should:
- Be a complete Python file with all necessary imports
- Include proper error handling and logging
- Have a main flow that orchestrates all components
- Include configuration management
- Be well-documented with comments""",
            llm_config={"config_list": [AZURE_CONFIG]}
        )
        
        # User Proxy Agent
        self.agents["user_proxy"] = UserProxyAgent(
            name="UserProxy",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=0,
            code_execution_config=False
        )

    def create_pipeline(self, user_requirements: str) -> Dict[str, Any]:
        """
        Create a data pipeline based on user requirements.

        Args:
            user_requirements: Natural language description of pipeline needs

        Returns:
            Dictionary containing pipeline code, config, and metadata
        """
        from agents.code_selector import CodeSelector, CodeCustomizer
        from pipeline_templates.pipeline_generator import PipelineGenerator, ConfigurationManager

        # Initialize utilities
        code_selector = CodeSelector()
        code_customizer = CodeCustomizer()
        pipeline_generator = PipelineGenerator()
        config_manager = ConfigurationManager()

        # Step 1: Planning phase
        plan_result = self._execute_planning_phase(user_requirements)

        # Step 2: Component selection phase
        components = self._execute_component_selection_phase(plan_result, code_selector, code_customizer)

        # Step 3: Configuration phase
        config_template = self._execute_configuration_phase(plan_result, config_manager)

        # Step 4: Pipeline building phase
        final_pipeline = self._execute_building_phase(components, config_template, pipeline_generator)

        # Step 5: Save pipeline to file
        pipeline_filename = self._save_pipeline(final_pipeline, user_requirements)

        return {
            "pipeline_code": final_pipeline["code"],
            "config_template": final_pipeline["config"],
            "api_instructions": final_pipeline["instructions"],
            "filename": pipeline_filename,
            "components_used": list(components.keys()),
            "plan": plan_result
        }

    def _execute_planning_phase(self, user_requirements: str) -> Dict[str, Any]:
        """Execute the planning phase with the planner agent."""
        planning_prompt = f"""
        Analyze the following user requirements and create a detailed technical plan:

        User Requirements: {user_requirements}

        Create a JSON plan with the following structure:
        {{
            "data_sources": ["pdf", "web_scraping", "documents"],
            "pdf_parsing_strategy": "unstructured|llamaparse|pymupdf4llm|docling|vlm",
            "chunking_strategy": "fixed_size|recursive|semantic|smart|sliding_window",
            "embedding_provider": "openai|cohere|jina|gemini|azure",
            "vector_store": "pinecone|qdrant|weaviate|chroma",
            "llm_provider": "azure_openai|bedrock|groq",
            "external_tools": ["tavily", "slack", "jira"],
            "use_case": "rag|search|classification|summarization",
            "requirements": {{
                "chunk_size": 1000,
                "chunk_overlap": 200,
                "max_results": 10,
                "temperature": 0.7
            }}
        }}

        Provide only the JSON response.
        """

        # Execute planning conversation
        result = self.agents["user_proxy"].initiate_chat(
            self.agents["planner"],
            message=planning_prompt,
            max_turns=1
        )

        # Extract JSON from response
        try:
            response_text = result.chat_history[-1]["content"]
            # Find JSON in the response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                plan = json.loads(json_match.group())
            else:
                # Fallback plan
                plan = self._get_default_plan()
        except:
            plan = self._get_default_plan()

        return plan

    def _get_default_plan(self) -> Dict[str, Any]:
        """Get a default plan if planning fails."""
        return {
            "data_sources": ["pdf"],
            "pdf_parsing_strategy": "unstructured",
            "chunking_strategy": "recursive",
            "embedding_provider": "openai",
            "vector_store": "pinecone",
            "llm_provider": "azure_openai",
            "external_tools": [],
            "use_case": "rag",
            "requirements": {
                "chunk_size": 1000,
                "chunk_overlap": 200,
                "max_results": 10,
                "temperature": 0.7
            }
        }

    def _execute_component_selection_phase(self, plan: Dict[str, Any],
                                         code_selector: 'CodeSelector',
                                         code_customizer: 'CodeCustomizer') -> Dict[str, str]:
        """Execute component selection phase with specialist agents."""
        components = {}

        # Helper function to safely get string values from plan
        def safe_get_string(key: str, default: str = "") -> str:
            value = plan.get(key, default)
            if isinstance(value, dict):
                # If it's a dict, try to get a 'type' or 'name' field, or use default
                return value.get('type', value.get('name', default))
            elif isinstance(value, list) and value:
                # If it's a list, take the first item if it's a string
                first_item = value[0]
                if isinstance(first_item, str):
                    return first_item
                elif isinstance(first_item, dict):
                    return first_item.get('type', first_item.get('name', default))
            elif isinstance(value, str):
                return value
            return default

        # Helper function to safely get list values from plan
        def safe_get_list(key: str, default: list = None) -> list:
            if default is None:
                default = []
            value = plan.get(key, default)
            if isinstance(value, list):
                # Filter out any non-string items and extract strings from dicts
                result = []
                for item in value:
                    if isinstance(item, str):
                        result.append(item)
                    elif isinstance(item, dict):
                        item_name = item.get('type', item.get('name', ''))
                        if item_name:
                            result.append(item_name)
                return result
            elif isinstance(value, str):
                return [value]
            return default

        # Data loading component
        data_sources = safe_get_list("data_sources")
        if "pdf" in data_sources:
            pdf_strategy = safe_get_string("pdf_parsing_strategy", "unstructured")
            components["data_loading"] = code_selector.get_pdf_parsing_code(pdf_strategy)

        if "web_scraping" in data_sources:
            web_code = code_selector.get_web_scraping_code()
            if "data_loading" in components:
                components["data_loading"] += "\n\n" + web_code
            else:
                components["data_loading"] = web_code

        # Chunking component
        chunking_strategy = safe_get_string("chunking_strategy", "recursive")
        components["chunking"] = code_selector.get_chunking_code(chunking_strategy)

        # Embedding component
        embedding_provider = safe_get_string("embedding_provider", "openai")
        components["embedding"] = code_selector.get_embedding_code(embedding_provider)

        # Vector store component
        vector_store = safe_get_string("vector_store", "pinecone")
        components["vector_store"] = code_selector.get_vector_store_code(vector_store)

        # LLM component
        llm_provider = safe_get_string("llm_provider", "azure_openai")
        components["llm"] = code_selector.get_llm_code(llm_provider)

        # External tools
        external_tools = safe_get_list("external_tools")
        for tool in external_tools:
            if tool in ["tavily", "serper"]:
                components[f"tool_{tool}"] = code_selector.get_tools_code("websearch")
            elif tool in ["slack", "jira"]:
                components[f"tool_{tool}"] = code_selector.get_tools_code("productivity")

        return components

    def _execute_configuration_phase(self, plan: Dict[str, Any],
                                   config_manager: 'ConfigurationManager') -> Dict[str, Any]:
        """Execute configuration phase with API manager agent."""
        # Determine required API keys based on plan
        required_keys = []

        # Helper function to safely get string values from plan
        def safe_get_string(key: str, default: str = "") -> str:
            value = plan.get(key, default)
            if isinstance(value, dict):
                # If it's a dict, try to get a 'type' or 'name' field, or use default
                return value.get('type', value.get('name', default))
            elif isinstance(value, list) and value:
                # If it's a list, take the first item if it's a string
                first_item = value[0]
                if isinstance(first_item, str):
                    return first_item
                elif isinstance(first_item, dict):
                    return first_item.get('type', first_item.get('name', default))
            elif isinstance(value, str):
                return value
            return default

        # Helper function to safely get list values from plan
        def safe_get_list(key: str, default: list = None) -> list:
            if default is None:
                default = []
            value = plan.get(key, default)
            if isinstance(value, list):
                # Filter out any non-string items and extract strings from dicts
                result = []
                for item in value:
                    if isinstance(item, str):
                        result.append(item)
                    elif isinstance(item, dict):
                        item_name = item.get('type', item.get('name', ''))
                        if item_name:
                            result.append(item_name)
                return result
            elif isinstance(value, str):
                return [value]
            return default

        embedding_provider = safe_get_string("embedding_provider")
        if embedding_provider == "openai":
            required_keys.append("OPENAI_API_KEY")
        elif embedding_provider == "azure":
            required_keys.extend(["AZURE_OPENAI_API_KEY", "AZURE_OPENAI_ENDPOINT"])
        elif embedding_provider == "cohere":
            required_keys.append("COHERE_API_KEY")
        elif embedding_provider == "jina":
            required_keys.append("JINA_API_KEY")
        elif embedding_provider == "gemini":
            required_keys.append("GEMINI_API_KEY")

        vector_store = safe_get_string("vector_store")
        if vector_store == "pinecone":
            required_keys.append("PINECONE_API_KEY")
        elif vector_store == "qdrant":
            required_keys.extend(["QDRANT_URL", "QDRANT_API_KEY"])
        elif vector_store == "weaviate":
            required_keys.extend(["WEAVIATE_URL", "WEAVIATE_API_KEY"])

        llm_provider = safe_get_string("llm_provider")
        if llm_provider == "azure_openai":
            required_keys.extend(["AZURE_OPENAI_API_KEY", "AZURE_OPENAI_ENDPOINT"])

        external_tools = safe_get_list("external_tools")
        if "tavily" in external_tools:
            required_keys.append("TAVILY_API_KEY")
        if "serper" in external_tools:
            required_keys.append("SERPER_API_KEY")
        if "slack" in external_tools:
            required_keys.append("SLACK_USER_TOKEN")
        if "jira" in external_tools:
            required_keys.extend(["JIRA_API_TOKEN", "JIRA_USERNAME", "JIRA_INSTANCE_URL"])

        pdf_parsing_strategy = safe_get_string("pdf_parsing_strategy")
        if pdf_parsing_strategy == "llamaparse":
            required_keys.append("LLAMAPARSE_API_KEY")

        # Remove duplicates - now safe since all items are strings
        required_keys = list(set(required_keys))

        config_template = config_manager.generate_config_template(required_keys)
        api_instructions = config_manager.get_api_key_instructions(required_keys)

        return {
            "template": config_template,
            "instructions": api_instructions,
            "required_keys": required_keys,
            "plan_config": plan.get("requirements", {})
        }

    def _execute_building_phase(self, components: Dict[str, str],
                              config_template: Dict[str, Any],
                              pipeline_generator: 'PipelineGenerator') -> Dict[str, str]:
        """Execute pipeline building phase."""
        # Combine configuration
        config = {
            "chunk_size": config_template.get("plan_config", {}).get("chunk_size", 1000),
            "chunk_overlap": config_template.get("plan_config", {}).get("chunk_overlap", 200),
            "max_results": config_template.get("plan_config", {}).get("max_results", 10),
            "temperature": config_template.get("plan_config", {}).get("temperature", 0.7)
        }

        # Generate pipeline
        pipeline_code = pipeline_generator.generate_pipeline(
            components=components,
            config=config,
            pipeline_name="custom_data_pipeline"
        )

        return {
            "code": pipeline_code,
            "config": config_template["template"],
            "instructions": config_template["instructions"]
        }

    def _save_pipeline(self, final_pipeline: Dict[str, str], user_requirements: str) -> str:
        """Save the generated pipeline to files."""
        import hashlib
        import re

        # Create a safe filename from user requirements
        safe_name = re.sub(r'[^\w\s-]', '', user_requirements.lower())
        safe_name = re.sub(r'[-\s]+', '_', safe_name)
        safe_name = safe_name[:50]  # Limit length

        # Add timestamp hash for uniqueness
        timestamp_hash = hashlib.md5(str(datetime.now()).encode()).hexdigest()[:8]
        filename_base = f"{safe_name}_{timestamp_hash}"

        # Save main pipeline file
        pipeline_file = self.output_path / f"{filename_base}.py"
        with open(pipeline_file, 'w', encoding='utf-8') as f:
            f.write(final_pipeline["code"])

        # Save configuration template
        config_file = self.output_path / f"{filename_base}_config.env"
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(final_pipeline["config"])

        # Save API instructions
        instructions_file = self.output_path / f"{filename_base}_instructions.md"
        with open(instructions_file, 'w', encoding='utf-8') as f:
            f.write(final_pipeline["instructions"])

        return str(pipeline_file)

    def get_available_options(self) -> Dict[str, List[str]]:
        """Get available options for each component type."""
        return {
            "pdf_parsing_strategies": ["unstructured", "llamaparse", "pymupdf4llm", "docling", "vlm"],
            "chunking_strategies": ["fixed_size", "recursive", "semantic", "smart", "sliding_window"],
            "embedding_providers": ["openai", "cohere", "jina", "gemini", "azure"],
            "vector_stores": ["pinecone", "qdrant", "weaviate", "chroma"],
            "llm_providers": ["azure_openai", "bedrock", "groq"],
            "external_tools": ["tavily", "serper", "slack", "jira"]
        }

    def create_custom_pipeline(self, custom_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Create a pipeline with a custom plan instead of using the planner agent."""
        from agents.code_selector import CodeSelector, CodeCustomizer
        from pipeline_templates.pipeline_generator import PipelineGenerator, ConfigurationManager

        # Initialize utilities
        code_selector = CodeSelector()
        code_customizer = CodeCustomizer()
        pipeline_generator = PipelineGenerator()
        config_manager = ConfigurationManager()

        # Use the provided plan directly
        plan_result = custom_plan

        # Execute remaining phases
        components = self._execute_component_selection_phase(plan_result, code_selector, code_customizer)
        config_template = self._execute_configuration_phase(plan_result, config_manager)
        final_pipeline = self._execute_building_phase(components, config_template, pipeline_generator)
        pipeline_filename = self._save_pipeline(final_pipeline, "custom_pipeline")

        return {
            "pipeline_code": final_pipeline["code"],
            "config_template": final_pipeline["config"],
            "api_instructions": final_pipeline["instructions"],
            "filename": pipeline_filename,
            "components_used": list(components.keys()),
            "plan": plan_result
        }

def create_web_interface():
    """Create a simple web interface for the pipeline system."""
    try:
        import streamlit as st

        st.title("Multi-Agent Data Pipeline Generator")
        st.write("Generate custom data pipelines using AI agents")

        # Initialize system
        if 'system' not in st.session_state:
            st.session_state.system = DataPipelineAgentSystem()

        # User input
        user_requirements = st.text_area(
            "Describe your data pipeline requirements:",
            placeholder="I want to build a pipeline that processes PDF documents and creates a RAG system for question answering...",
            height=100
        )

        # Get available options
        options = st.session_state.system.get_available_options()

        # Advanced options
        with st.expander("Advanced Options"):

            col1, col2 = st.columns(2)

            with col1:
                pdf_strategy = st.selectbox("PDF Parsing Strategy", options["pdf_parsing_strategies"])
                chunking_strategy = st.selectbox("Chunking Strategy", options["chunking_strategies"])
                embedding_provider = st.selectbox("Embedding Provider", options["embedding_providers"])

            with col2:
                vector_store = st.selectbox("Vector Store", options["vector_stores"])
                llm_provider = st.selectbox("LLM Provider", options["llm_providers"])
                external_tools = st.multiselect("External Tools", options["external_tools"])

        # Generate pipeline
        if st.button("Generate Pipeline"):
            if user_requirements:
                with st.spinner("Generating pipeline..."):
                    try:
                        result = st.session_state.system.create_pipeline(user_requirements)

                        st.success("Pipeline generated successfully!")

                        # Display results
                        st.subheader("Generated Pipeline")
                        st.code(result["pipeline_code"][:1000] + "..." if len(result["pipeline_code"]) > 1000 else result["pipeline_code"], language="python")

                        # Download buttons
                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.download_button(
                                "Download Pipeline",
                                result["pipeline_code"],
                                file_name="data_pipeline.py",
                                mime="text/python"
                            )

                        with col2:
                            st.download_button(
                                "Download Config",
                                result["config_template"],
                                file_name="config.env",
                                mime="text/plain"
                            )

                        with col3:
                            st.download_button(
                                "Download Instructions",
                                result["api_instructions"],
                                file_name="instructions.md",
                                mime="text/markdown"
                            )

                        # Display plan
                        st.subheader("Pipeline Plan")
                        st.json(result["plan"])

                    except Exception as e:
                        st.error(f"Error generating pipeline: {str(e)}")
            else:
                st.warning("Please enter your pipeline requirements.")

    except ImportError:
        print("Streamlit not installed. Install with: pip install streamlit")
        print("Then run with: streamlit run multi_agent_pipeline_system.py")

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "web":
        create_web_interface()
    else:
        # Example usage
        system = DataPipelineAgentSystem()

        user_input = """I want you to build a pipeline which intakes a set of documents and treats that as a historical reference material and uses it to answer questions from another questionnaire document"""

        result = system.create_pipeline(user_input)
        print("Pipeline generation completed!")
        print(f"Pipeline saved to: {result['filename']}")
        print(f"Components used: {result['components_used']}")
        print(f"Plan: {result['plan']}")
