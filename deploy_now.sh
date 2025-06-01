#!/bin/bash
# 🚀 ONE-COMMAND ENTERPRISE PIPELINE DEPLOYMENT

set -e

echo "🚀 ENTERPRISE PIPELINE - ONE COMMAND DEPLOYMENT"
echo "================================================"

# Check if we're in the right directory
if [ ! -f "main_app.py" ]; then
    echo "❌ Please run this script from the pipeline directory"
    exit 1
fi

echo "Choose deployment type:"
echo "1) Local Development (Docker Compose)"
echo "2) Production Kubernetes"
read -p "Enter choice (1 or 2): " choice

case $choice in
    1)
        echo "🛠️ DEPLOYING LOCAL DEVELOPMENT ENVIRONMENT..."

        # Start with Docker Compose
        docker-compose up -d

        echo "⏳ Waiting for services to be ready..."
        sleep 30

        # Check health
        echo "🔍 Checking service health..."
        curl -f http://localhost:8000/health || {
            echo "❌ Health check failed"
            docker-compose logs
            exit 1
        }

        echo "✅ LOCAL DEPLOYMENT COMPLETE!"
        echo "🌐 Application: http://localhost:8000"
        echo "📖 API Docs: http://localhost:8000/docs"
        echo "📊 Grafana: http://localhost:3000 (admin/admin)"
        echo "📈 Prometheus: http://localhost:9090"
        ;;

    2)
        echo "🚀 DEPLOYING TO PRODUCTION KUBERNETES..."

        # Check prerequisites
        command -v kubectl >/dev/null 2>&1 || {
            echo "❌ kubectl required but not installed"
            exit 1
        }

        command -v docker >/dev/null 2>&1 || {
            echo "❌ Docker required but not installed"
            exit 1
        }

        # Create namespace
        kubectl create namespace enterprise-pipeline --dry-run=client -o yaml | kubectl apply -f -

        # Build and push image
        echo "🏗️ Building Docker image..."
        docker build -t enterprise-pipeline:latest .

        # Deploy Redis
        echo "🔴 Deploying Redis..."
        kubectl apply -f k8s/redis.yaml

        # Wait for Redis
        echo "⏳ Waiting for Redis..."
        kubectl wait --for=condition=ready pod -l app=redis -n enterprise-pipeline --timeout=300s

        # Deploy application
        echo "🚀 Deploying application..."
        kubectl apply -f k8s/app.yaml

        # Wait for deployment
        echo "⏳ Waiting for deployment..."
        kubectl wait --for=condition=available deployment/enterprise-pipeline -n enterprise-pipeline --timeout=300s

        # Get service URL
        echo "✅ PRODUCTION DEPLOYMENT COMPLETE!"
        echo "🌐 Getting service URL..."
        kubectl get service enterprise-pipeline-service -n enterprise-pipeline
        ;;

    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "🎉 ENTERPRISE PIPELINE DEPLOYED SUCCESSFULLY!"
echo "================================================"
