# 🚀 AI Pipeline Generator - Complete System

A comprehensive AI-powered data pipeline generation system with Streamlit interface, multi-agent AI, and one-click deployment capabilities.

## 🌟 Features

### 🎯 **Main Application: Streamlit Pipeline Generator**
- **Natural Language Pipeline Generation**: Describe pipelines in plain English
- **Three Pipeline Types**: Standard Multi-Agent, Enterprise Grade, Real Deployable
- **Complete Package Download**: ZIP files with all deployment components
- **One-Click Local Deployment**: Automated Docker-based deployment
- **Real-time Monitoring**: Live status updates and deployment logs

### 🤖 **AI-Powered Generation**
- **Multi-Agent System**: AutoGen-based specialized AI agents
- **Enterprise Architecture**: Production-ready enterprise pipelines
- **Real Deployable Systems**: Complete working applications

### 📦 **Complete Pipeline Packages**
- Docker configurations and Kubernetes manifests
- Monitoring setup (Prometheus, Grafana)
- Security configurations and compliance
- Documentation and deployment scripts

## Flowchart
https://www.mermaidchart.com/app/projects/0a148600-e0cb-4c4e-9c9e-2fac3aad4192/diagrams/fdebe39b-14cd-42c8-b1e8-8f66060b0d3c/version/v0.1/edit

## 🚀 Quick Start

### 1. Launch the Streamlit App
```bash
# Start the AI Pipeline Generator
streamlit run streamlit_pipeline_app.py

# Or use the launcher
python launch_pipeline_app.py
```

### 2. Access the App
Open your browser to: **http://localhost:8501**

### 3. Generate Your Pipeline
1. **Describe** your pipeline in natural language
2. **Select** pipeline type (Standard/Enterprise/Real Deployable)
3. **Generate** with AI agents
4. **Download** complete package
5. **Deploy** locally with one click

## 📋 Example Pipeline Description
```
I want to build a pipeline that:
- Processes PDF documents from a folder
- Extracts text and creates embeddings using OpenAI
- Stores embeddings in Pinecone vector database
- Provides a FastAPI-based RAG question answering service
- Includes Redis caching for performance
- Has monitoring with Prometheus and Grafana
- Can be deployed with Docker Compose
```

## 🔧 Available Endpoints After Deployment
- **Main Application**: `http://localhost:8000`
- **API Documentation**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/health`
- **Metrics**: `http://localhost:8000/metrics`
- **Grafana**: `http://localhost:3000` (admin/admin)
- **Prometheus**: `http://localhost:9090`

## 📁 Core Components

### Essential Files
- `streamlit_pipeline_app.py` - Main Streamlit application
- `multi_agent_pipeline_system.py` - Multi-agent pipeline generator
- `enterprise_pipeline_system.py` - Enterprise-grade pipeline generator
- `real_working_pipeline.py` - Real deployable pipeline generator
- `pipeline_packager.py` - Complete package creation utility
- `deployment_manager.py` - Local deployment management
- `launch_pipeline_app.py` - Easy launcher with environment checking

### Data Engineering Database
- `Data_Eng_Database/` - Core data engineering components
  - `chunking/` - Text chunking strategies
  - `data_loading/` - Data loading utilities
  - `embeddings/` - Embedding generation tools
  - `llms/` - Language model integrations
  - `tools/` - Utility tools
  - `vector_stores/` - Vector database integrations

## 🛠️ Installation & Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Environment Setup
```bash
# Option 1: Use the launcher
python launch_pipeline_app.py --setup

# Option 2: Manual setup
# Create .env file with:
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_KEY=your-api-key
AZURE_OPENAI_MODEL=gpt-4o
```

### 3. Check Environment
```bash
python launch_pipeline_app.py --check
```

## 🎯 Pipeline Types

### 1. Standard Multi-Agent
- Flexible component-based pipelines
- Configurable PDF parsing, chunking, embeddings
- Multiple vector store and LLM options
- External tool integrations

### 2. Enterprise Grade
- Production-ready with monitoring and security
- Auto-scaling and compliance features
- Comprehensive logging and metrics
- Multi-cloud deployment support

### 3. Real Deployable
- Complete working applications
- One-command deployment scripts
- Full Docker and Kubernetes setup
- Production monitoring included

## 📊 Management Commands

```bash
# Launch with custom port
python launch_pipeline_app.py --port 8502

# Debug mode
python launch_pipeline_app.py --debug

# Install dependencies
python launch_pipeline_app.py --install

# Setup environment
python launch_pipeline_app.py --setup
```

## 🎉 What Makes This Special

1. **Production-Ready**: All generated pipelines are deployable and functional
2. **Enterprise-Grade**: Includes monitoring, security, scaling, and compliance
3. **One-Command Deployment**: True one-click deployment with health monitoring
4. **AI-Powered**: Uses AutoGen multi-agent system with Azure OpenAI
5. **Complete Packages**: Everything needed for deployment in one ZIP
6. **Real-Time Monitoring**: Live status updates and deployment logs

## 📖 Documentation

- `README_STREAMLIT_APP.md` - Detailed Streamlit app documentation
- `README_MultiAgent_Pipeline.md` - Multi-agent system documentation

## 🚀 Ready to Use!

Your AI Pipeline Generator is ready! Launch the Streamlit app and start generating production-ready data pipelines from natural language descriptions.

**🌐 Access the app at: http://localhost:8501**