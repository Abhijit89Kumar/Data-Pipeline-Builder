# 🏢 Enterprise AI Pipeline Generator - Streamlit App

A comprehensive Streamlit application that generates **ENTERPRISE-GRADE** production-ready data engineering pipelines from natural language descriptions using AI agents, with complete package download and one-click local deployment capabilities.

## 🌟 Features

### 🏢 Enterprise-Grade Pipeline Generation
- **Natural Language Input**: Describe your enterprise pipeline requirements in plain English
- **Enterprise AI System**: Leverages AutoGen with specialized enterprise AI agents
- **ENTERPRISE GRADE ONLY**:
  - **Production-ready** with comprehensive monitoring, security, and auto-scaling
  - **Fully deployable** with Docker and Kubernetes
  - **Enterprise governance** and compliance features
  - **Complete CI/CD** pipeline integration

### 📦 Complete Enterprise Package Creation
- **Full Enterprise Pipeline Packages**: Everything needed for production deployment
- **Enterprise-Grade Components**:
  - Main pipeline code with enterprise patterns
  - Production configuration files
  - Docker and Kubernetes setup
  - Monitoring and security configurations
  - Deployment scripts and automation
  - Comprehensive documentation
  - Enterprise requirements and dependencies

### 🚀 One-Click Local Deployment
- **Automated Deployment**: Deploy generated pipelines locally with one click
- **Docker Integration**: Automatic containerization and orchestration
- **Health Monitoring**: Real-time deployment status and health checks
- **Service Management**: Start, stop, and monitor deployed services

### 📊 Real-Time Monitoring
- **Live Status Updates**: Track generation and deployment progress
- **Deployment Logs**: View real-time deployment logs
- **Service Health**: Monitor running services and endpoints
- **Metrics Integration**: Built-in Prometheus metrics

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 Enterprise Streamlit Interface             │
├─────────────────────────────────────────────────────────────┤
│  Natural Language Input  │  Enterprise Configuration      │
│  Progress Tracking       │  Status Monitoring              │
│  Download Management     │  Deployment Controls            │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│              Enterprise AI Agent Pipeline System           │
├─────────────────────────────────────────────────────────────┤
│  Enterprise Generator    │  Production Components          │
│  Security & Compliance   │  Auto-scaling Configuration    │
│  Monitoring Setup        │  Enterprise Code Generation    │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                    Pipeline Packager                        │
├─────────────────────────────────────────────────────────────┤
│  Package Creation        │  File Organization              │
│  Dependency Management   │  Documentation Generation       │
│  Docker Configuration    │  Kubernetes Manifests          │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                   Deployment Manager                        │
├─────────────────────────────────────────────────────────────┤
│  Local Deployment        │  Docker Orchestration           │
│  Health Monitoring       │  Service Management             │
│  Log Streaming          │  Status Reporting               │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd data_Eng_db-main

# Install dependencies
python launch_pipeline_app.py --install

# Setup environment
python launch_pipeline_app.py --setup
```

### 2. Launch the App

```bash
# Quick launch
python launch_pipeline_app.py

# Custom port
python launch_pipeline_app.py --port 8502

# Debug mode
python launch_pipeline_app.py --debug
```

### 3. Access the App

Open your browser and navigate to: `http://localhost:8501`

## 📋 Usage Guide

### Step 1: Describe Your Pipeline
1. Open the app in your browser
2. In the main text area, describe your pipeline requirements in natural language
3. Be as detailed as possible about:
   - Data sources and formats
   - Processing requirements
   - Storage needs
   - API requirements
   - Deployment preferences

**Example Description:**
```
I want to build an enterprise pipeline that:
- Processes PDF documents from a folder
- Extracts text and creates embeddings using Azure OpenAI
- Stores embeddings in a production-grade vector database
- Provides a scalable RAG-based question answering API
- Includes comprehensive monitoring, security, and logging
- Has auto-scaling and load balancing
- Can be deployed with Docker and Kubernetes
- Includes CI/CD pipeline and enterprise governance
```

### Step 2: Configure Enterprise Pipeline
1. The pipeline type is automatically set to **Enterprise Grade**
2. Configure enterprise options in the sidebar:
   - Architecture Pattern (Microservices, Monolithic, Serverless)
   - Database (PostgreSQL, MongoDB, Redis)
   - Message Queue (Redis, RabbitMQ, Apache Kafka)
   - Deployment Target (Docker Compose, Kubernetes, Both)
   - Enable enterprise features (Monitoring, Security, Auto-scaling, CI/CD)

### Step 3: Generate Enterprise Pipeline
1. Click "🚀 Generate Enterprise Pipeline"
2. Watch the real-time progress as enterprise AI agents work
3. Review the generated enterprise code, configuration, and deployment plan

### Step 4: Create Enterprise Package
1. Click "📦 Create Package" to bundle everything for enterprise deployment
2. The package includes all necessary files for production deployment
3. Download the complete enterprise package ZIP file

### Step 5: Deploy Locally
1. Click "🚀 Deploy Locally" for one-click enterprise deployment
2. Monitor deployment progress in real-time
3. Access your deployed enterprise pipeline through provided endpoints

## 🔧 Configuration

### Environment Variables

Create a `.env` file or set environment variables:

```bash
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_KEY=your-api-key
AZURE_OPENAI_MODEL=gpt-4o

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Application Configuration
HOST=0.0.0.0
PORT=8000
```

### Enterprise Pipeline Configuration

#### Enterprise Grade (ONLY OPTION)
- **Architecture**: Microservices, Monolithic, Serverless
- **Databases**: PostgreSQL, MongoDB, Redis
- **Message Queues**: Redis, RabbitMQ, Apache Kafka
- **Deployment**: Docker Compose, Kubernetes, Both
- **Monitoring**: Prometheus, Grafana, ELK Stack
- **Security**: Authentication, Authorization, Encryption
- **Auto-scaling**: Horizontal and vertical scaling
- **CI/CD**: Complete pipeline automation
- **Governance**: Enterprise compliance and auditing

## 📦 Package Contents

Generated packages include:

```
generated_pipeline/
├── src/
│   └── main_pipeline.py          # Main application code
├── infrastructure/
│   ├── Dockerfile                # Container configuration
│   ├── docker-compose.yml        # Multi-service setup
│   └── k8s/                      # Kubernetes manifests
├── monitoring/
│   ├── prometheus.yml            # Metrics configuration
│   └── grafana/                  # Dashboard configs
├── security/
│   └── auth.py                   # Authentication setup
├── tests/
│   └── test_pipeline.py          # Test suite
├── docs/
│   └── README.md                 # Documentation
├── requirements.txt              # Dependencies
├── config.env                    # Configuration template
├── deploy.sh                     # Deployment script
└── package_metadata.json         # Package information
```

## 🚀 Deployment Options

### Local Development
```bash
# Extract package and run
unzip generated_pipeline.zip
cd generated_pipeline
./deploy.sh
```

### Docker Compose
```bash
docker-compose up -d
```

### Kubernetes
```bash
kubectl apply -f k8s/
```

## 📊 Monitoring and Management

### Available Endpoints
- **Main Application**: `http://localhost:8000`
- **API Documentation**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/health`
- **Metrics**: `http://localhost:8000/metrics`
- **Prometheus**: `http://localhost:9090`
- **Grafana**: `http://localhost:3000`

### Management Commands
```bash
# Check deployment status
python launch_pipeline_app.py --check

# Stop all services
docker-compose down

# View logs
docker-compose logs -f
```

## 🛠️ Troubleshooting

### Common Issues

1. **Dependencies Missing**
   ```bash
   python launch_pipeline_app.py --install
   ```

2. **Docker Not Available**
   - Install Docker Desktop
   - Ensure Docker daemon is running

3. **Port Conflicts**
   ```bash
   python launch_pipeline_app.py --port 8502
   ```

4. **Azure OpenAI Issues**
   - Check API key and endpoint
   - Verify model availability

### Debug Mode
```bash
python launch_pipeline_app.py --debug
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Check the troubleshooting section
- Review the logs in debug mode
- Open an issue on GitHub

---

**Built with ❤️ using Streamlit, AutoGen, and enterprise-grade AI agents**
