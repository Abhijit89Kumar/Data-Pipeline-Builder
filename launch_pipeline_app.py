#!/usr/bin/env python3
"""
Pipeline App Launcher
Easy launcher for the Streamlit Pipeline Generator App
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed."""
    
    required_packages = [
        "streamlit",
        "ag2", 
        "openai",
        "prefect",
        "langchain",
        "requests",
        "redis"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n💡 Install missing packages with:")
        print("   pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are installed")
    return True

def check_docker():
    """Check if Docker is available."""
    
    try:
        result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Docker is available: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    
    print("⚠️ Docker is not available - local deployment will be limited")
    return False

def check_environment():
    """Check environment setup."""
    
    print("🔍 Checking environment...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print(f"❌ Python 3.8+ required, found {python_version.major}.{python_version.minor}")
        return False
    
    print(f"✅ Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Check dependencies
    if not check_dependencies():
        return False
    
    # Check Docker
    check_docker()
    
    # Check Azure OpenAI configuration
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    azure_key = os.getenv("AZURE_OPENAI_KEY")
    
    if not azure_endpoint or not azure_key:
        print("⚠️ Azure OpenAI not configured - using default settings")
        print("   Set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_KEY environment variables")
    else:
        print("✅ Azure OpenAI configuration found")
    
    return True

def launch_app(port=8501, debug=False):
    """Launch the Streamlit app."""
    
    app_file = Path(__file__).parent / "streamlit_pipeline_app.py"
    
    if not app_file.exists():
        print(f"❌ App file not found: {app_file}")
        return False
    
    print(f"🚀 Launching Pipeline Generator App on port {port}...")
    print(f"📱 App will be available at: http://localhost:{port}")
    print("🛑 Press Ctrl+C to stop the app")
    print("-" * 50)
    
    try:
        cmd = [
            "streamlit", "run", str(app_file),
            "--server.port", str(port),
            "--server.headless", "true" if not debug else "false",
            "--browser.gatherUsageStats", "false"
        ]
        
        if debug:
            cmd.extend(["--logger.level", "debug"])
        
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n🛑 App stopped by user")
    except FileNotFoundError:
        print("❌ Streamlit not found. Install with: pip install streamlit")
        return False
    except Exception as e:
        print(f"❌ Error launching app: {e}")
        return False
    
    return True

def install_dependencies():
    """Install required dependencies."""
    
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    if not requirements_file.exists():
        print(f"❌ Requirements file not found: {requirements_file}")
        return False
    
    print("📦 Installing dependencies...")
    
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ], check=True)
        
        print("✅ Dependencies installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_environment():
    """Setup environment configuration."""
    
    env_file = Path(__file__).parent / ".env"
    
    if env_file.exists():
        print("✅ Environment file already exists")
        return True
    
    print("🔧 Setting up environment configuration...")
    
    # Get user input for configuration
    azure_endpoint = input("Enter Azure OpenAI Endpoint (or press Enter for default): ").strip()
    if not azure_endpoint:
        azure_endpoint = "https://admins.openai.azure.com/"
    
    azure_key = input("Enter Azure OpenAI API Key (or press Enter for default): ").strip()
    if not azure_key:
        azure_key = "ab75735c129449b78343771a136adb54"
    
    azure_model = input("Enter Azure OpenAI Model (or press Enter for gpt-4o): ").strip()
    if not azure_model:
        azure_model = "gpt-4o"
    
    # Create .env file
    env_content = f"""# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT={azure_endpoint}
AZURE_OPENAI_KEY={azure_key}
AZURE_OPENAI_MODEL={azure_model}

# Redis Configuration (for local deployment)
REDIS_URL=redis://localhost:6379/0

# Application Configuration
HOST=0.0.0.0
PORT=8000
"""
    
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print(f"✅ Environment configuration saved to {env_file}")
    return True

def main():
    """Main launcher function."""
    
    parser = argparse.ArgumentParser(description="Launch the AI Pipeline Generator App")
    parser.add_argument("--port", type=int, default=8501, help="Port to run the app on")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--install", action="store_true", help="Install dependencies")
    parser.add_argument("--setup", action="store_true", help="Setup environment")
    parser.add_argument("--check", action="store_true", help="Check environment only")
    
    args = parser.parse_args()
    
    print("🚀 AI Pipeline Generator App Launcher")
    print("=" * 40)
    
    if args.install:
        if install_dependencies():
            print("✅ Dependencies installation completed")
        else:
            print("❌ Dependencies installation failed")
        return
    
    if args.setup:
        if setup_environment():
            print("✅ Environment setup completed")
        else:
            print("❌ Environment setup failed")
        return
    
    if args.check:
        if check_environment():
            print("✅ Environment check passed")
        else:
            print("❌ Environment check failed")
        return
    
    # Default: check environment and launch app
    if not check_environment():
        print("\n💡 Try running with --install to install dependencies")
        print("💡 Try running with --setup to configure environment")
        return
    
    # Launch the app
    launch_app(args.port, args.debug)

if __name__ == "__main__":
    main()
