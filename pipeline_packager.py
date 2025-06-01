"""
Pipeline Packager
Creates complete downloadable packages for generated pipelines
"""

import os
import zipfile
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, List
import json
from datetime import datetime

class PipelinePackager:
    """Creates complete downloadable packages for generated pipelines."""
    
    def __init__(self):
        self.temp_dir = None
        
    def create_complete_package(self, 
                              pipeline_result: Dict[str, Any],
                              requirements: str,
                              package_type: str = "standard") -> str:
        """
        Create a complete pipeline package for download.
        
        Args:
            pipeline_result: Result from pipeline generation
            requirements: Original user requirements
            package_type: "standard", "enterprise", or "real_deployable"
            
        Returns:
            Path to the created ZIP file
        """
        
        # Create temporary directory
        self.temp_dir = tempfile.mkdtemp(prefix="pipeline_package_")
        package_dir = Path(self.temp_dir) / "generated_pipeline"
        package_dir.mkdir(parents=True, exist_ok=True)
        
        if package_type == "real_deployable":
            return self._create_real_deployable_package(pipeline_result, requirements, package_dir)
        elif package_type == "enterprise":
            return self._create_enterprise_package(pipeline_result, requirements, package_dir)
        else:
            return self._create_standard_package(pipeline_result, requirements, package_dir)
    
    def _create_standard_package(self, pipeline_result: Dict[str, Any], 
                               requirements: str, package_dir: Path) -> str:
        """Create a standard pipeline package."""
        
        # Main pipeline file
        with open(package_dir / "data_pipeline.py", 'w', encoding='utf-8') as f:
            f.write(pipeline_result["pipeline_code"])
        
        # Configuration file
        with open(package_dir / "config.env", 'w', encoding='utf-8') as f:
            f.write(pipeline_result["config_template"])
        
        # Instructions
        with open(package_dir / "README.md", 'w', encoding='utf-8') as f:
            f.write(pipeline_result["api_instructions"])
        
        # Requirements
        self._create_requirements_file(package_dir, pipeline_result.get("components_used", []))
        
        # Deployment script
        self._create_deployment_script(package_dir, "standard")
        
        # Package metadata
        self._create_package_metadata(package_dir, pipeline_result, requirements, "standard")
        
        return self._create_zip_file(package_dir, "standard_pipeline")
    
    def _create_enterprise_package(self, pipeline_result: Dict[str, Any], 
                                 requirements: str, package_dir: Path) -> str:
        """Create an enterprise pipeline package."""
        
        # Import enterprise generator
        from enterprise_pipeline_system import EnterprisePipelineSystem
        from enterprise_code_generator import EnterpriseCodeGenerator
        
        # Generate enterprise components
        enterprise_system = EnterprisePipelineSystem()
        
        # Create enterprise structure
        (package_dir / "src").mkdir(exist_ok=True)
        (package_dir / "infrastructure").mkdir(exist_ok=True)
        (package_dir / "monitoring").mkdir(exist_ok=True)
        (package_dir / "security").mkdir(exist_ok=True)
        (package_dir / "tests").mkdir(exist_ok=True)
        (package_dir / "docs").mkdir(exist_ok=True)
        
        # Main application
        with open(package_dir / "src" / "main_pipeline.py", 'w', encoding='utf-8') as f:
            f.write(pipeline_result["pipeline_code"])
        
        # Docker files
        self._create_docker_files(package_dir)
        
        # Kubernetes manifests
        self._create_k8s_manifests(package_dir)
        
        # Monitoring setup
        self._create_monitoring_files(package_dir)
        
        # Requirements
        self._create_enterprise_requirements(package_dir)
        
        # Deployment script
        self._create_deployment_script(package_dir, "enterprise")
        
        # Package metadata
        self._create_package_metadata(package_dir, pipeline_result, requirements, "enterprise")
        
        return self._create_zip_file(package_dir, "enterprise_pipeline")
    
    def _create_real_deployable_package(self, pipeline_result: Dict[str, Any], 
                                      requirements: str, package_dir: Path) -> str:
        """Create a real deployable pipeline package."""
        
        # Import real pipeline generator
        from real_working_pipeline import RealWorkingPipelineGenerator
        
        # Generate real pipeline
        generator = RealWorkingPipelineGenerator()
        
        # Copy the real pipeline structure
        real_pipeline_dir = Path("real_working_pipeline")
        if real_pipeline_dir.exists():
            shutil.copytree(real_pipeline_dir, package_dir, dirs_exist_ok=True)
        else:
            # Generate fresh real pipeline
            import asyncio
            asyncio.run(generator.generate_complete_pipeline(requirements))
            shutil.copytree(real_pipeline_dir, package_dir, dirs_exist_ok=True)
        
        # Package metadata
        self._create_package_metadata(package_dir, pipeline_result, requirements, "real_deployable")
        
        return self._create_zip_file(package_dir, "real_deployable_pipeline")
    
    def _create_requirements_file(self, package_dir: Path, components_used: List[str]):
        """Create requirements.txt based on components used."""
        
        base_requirements = [
            "prefect>=2.0.0",
            "python-dotenv>=1.0.0",
            "pydantic>=2.0.0",
            "requests>=2.31.0",
            "aiohttp>=3.8.0"
        ]
        
        # Add component-specific requirements
        component_requirements = {
            "pdf_parsing": ["pymupdf4llm>=0.0.5", "unstructured>=0.10.0"],
            "embeddings": ["sentence-transformers>=2.2.0", "openai>=1.0.0"],
            "vector_stores": ["pinecone-client>=3.0.0", "chromadb>=0.4.0"],
            "llms": ["openai>=1.0.0", "langchain>=0.1.0"]
        }
        
        requirements = base_requirements.copy()
        for component in components_used:
            if component in component_requirements:
                requirements.extend(component_requirements[component])
        
        # Remove duplicates
        requirements = list(set(requirements))
        
        with open(package_dir / "requirements.txt", 'w', encoding='utf-8') as f:
            f.write('\n'.join(sorted(requirements)))
    
    def _create_enterprise_requirements(self, package_dir: Path):
        """Create enterprise-grade requirements.txt."""
        
        requirements = """# Enterprise Pipeline Requirements
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
redis==5.0.1
openai==0.28.1
python-multipart==0.0.6
python-dotenv==1.0.0
requests==2.31.0
aiofiles==23.2.1
prometheus-client==0.19.0
psycopg2-binary==2.9.9
sqlalchemy==2.0.23
alembic==1.13.1
celery==5.3.4
"""
        
        with open(package_dir / "requirements.txt", 'w', encoding='utf-8') as f:
            f.write(requirements)
    
    def _create_docker_files(self, package_dir: Path):
        """Create Docker configuration files."""
        
        dockerfile = """FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Run application
CMD ["python", "src/main_pipeline.py"]
"""
        
        with open(package_dir / "Dockerfile", 'w', encoding='utf-8') as f:
            f.write(dockerfile)
        
        docker_compose = """version: '3.8'

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      redis:
        condition: service_healthy

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
"""
        
        with open(package_dir / "docker-compose.yml", 'w', encoding='utf-8') as f:
            f.write(docker_compose)
    
    def _create_k8s_manifests(self, package_dir: Path):
        """Create Kubernetes manifests."""
        
        k8s_dir = package_dir / "k8s"
        k8s_dir.mkdir(exist_ok=True)
        
        # App deployment
        app_yaml = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: enterprise-pipeline
  namespace: enterprise-pipeline
spec:
  replicas: 3
  selector:
    matchLabels:
      app: enterprise-pipeline
  template:
    metadata:
      labels:
        app: enterprise-pipeline
    spec:
      containers:
      - name: app
        image: enterprise-pipeline:latest
        ports:
        - containerPort: 8000
        env:
        - name: REDIS_URL
          value: "redis://redis-service:6379/0"
---
apiVersion: v1
kind: Service
metadata:
  name: enterprise-pipeline-service
  namespace: enterprise-pipeline
spec:
  selector:
    app: enterprise-pipeline
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
"""
        
        with open(k8s_dir / "app.yaml", 'w', encoding='utf-8') as f:
            f.write(app_yaml)
    
    def _create_monitoring_files(self, package_dir: Path):
        """Create monitoring configuration files."""
        
        monitoring_dir = package_dir / "monitoring"
        monitoring_dir.mkdir(exist_ok=True)
        
        prometheus_config = """global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'enterprise-pipeline'
    static_configs:
      - targets: ['app:8000']
    metrics_path: /metrics
    scrape_interval: 10s
"""
        
        with open(monitoring_dir / "prometheus.yml", 'w', encoding='utf-8') as f:
            f.write(prometheus_config)
    
    def _create_deployment_script(self, package_dir: Path, package_type: str):
        """Create deployment script."""
        
        if package_type == "real_deployable":
            # Copy existing deployment script
            if Path("deploy_now.sh").exists():
                shutil.copy("deploy_now.sh", package_dir / "deploy_now.sh")
            return
        
        script_content = """#!/bin/bash
# Pipeline Deployment Script

set -e

echo "🚀 Deploying Pipeline..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "🛠️ Starting services with Docker Compose..."
docker-compose up -d

echo "⏳ Waiting for services to be ready..."
sleep 30

echo "🔍 Checking service health..."
curl -f http://localhost:8000/health || {
    echo "❌ Health check failed"
    docker-compose logs
    exit 1
}

echo "✅ Deployment complete!"
echo "🌐 Application: http://localhost:8000"
echo "📖 API Docs: http://localhost:8000/docs"
"""
        
        script_path = package_dir / "deploy.sh"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        # Make script executable
        script_path.chmod(0o755)
    
    def _create_package_metadata(self, package_dir: Path, pipeline_result: Dict[str, Any], 
                                requirements: str, package_type: str):
        """Create package metadata file."""
        
        metadata = {
            "package_type": package_type,
            "generated_at": datetime.now().isoformat(),
            "user_requirements": requirements,
            "components_used": pipeline_result.get("components_used", []),
            "plan": pipeline_result.get("plan", {}),
            "version": "1.0.0",
            "deployment_instructions": {
                "local": "Run ./deploy.sh for local deployment",
                "docker": "Use docker-compose up -d",
                "kubernetes": "Apply k8s manifests with kubectl"
            }
        }
        
        with open(package_dir / "package_metadata.json", 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
    
    def _create_zip_file(self, package_dir: Path, package_name: str) -> str:
        """Create ZIP file from package directory."""
        
        zip_path = Path(self.temp_dir) / f"{package_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(package_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(package_dir)
                    zipf.write(file_path, arcname)
        
        return str(zip_path)
    
    def cleanup(self):
        """Clean up temporary files."""
        if self.temp_dir and Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
