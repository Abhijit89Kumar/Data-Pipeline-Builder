"""
Deployment Manager
Handles local deployment of generated pipelines
"""

import os
import subprocess
import tempfile
import shutil
import zipfile
import time
import requests
from pathlib import Path
from typing import Dict, Any, Optional, Callable
import threading
import json

class DeploymentManager:
    """Manages local deployment of generated pipelines."""
    
    def __init__(self):
        self.deployment_dir = None
        self.deployment_process = None
        self.deployment_status = "idle"
        self.deployment_logs = []
        self.status_callback = None
        
    def deploy_pipeline_package(self, 
                               zip_path: str, 
                               status_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Deploy a pipeline package locally.
        
        Args:
            zip_path: Path to the pipeline ZIP package
            status_callback: Callback function for status updates
            
        Returns:
            Deployment result dictionary
        """
        
        self.status_callback = status_callback
        self.deployment_logs = []
        
        try:
            # Extract package
            self._update_status("extracting", "Extracting pipeline package...")
            self.deployment_dir = self._extract_package(zip_path)
            
            # Check prerequisites
            self._update_status("checking", "Checking prerequisites...")
            prereq_check = self._check_prerequisites()
            if not prereq_check["success"]:
                return {
                    "success": False,
                    "error": f"Prerequisites check failed: {prereq_check['error']}",
                    "logs": self.deployment_logs
                }
            
            # Deploy based on package type
            self._update_status("deploying", "Starting deployment...")
            deployment_result = self._deploy_package()
            
            if deployment_result["success"]:
                self._update_status("running", "Pipeline deployed successfully!")
                
                # Wait for services to be ready
                self._update_status("waiting", "Waiting for services to be ready...")
                health_check = self._wait_for_health_check()
                
                if health_check["success"]:
                    self._update_status("ready", "Pipeline is ready and healthy!")
                    return {
                        "success": True,
                        "deployment_dir": str(self.deployment_dir),
                        "endpoints": health_check["endpoints"],
                        "logs": self.deployment_logs
                    }
                else:
                    self._update_status("error", "Health check failed")
                    return {
                        "success": False,
                        "error": f"Health check failed: {health_check['error']}",
                        "logs": self.deployment_logs
                    }
            else:
                self._update_status("error", "Deployment failed")
                return {
                    "success": False,
                    "error": deployment_result["error"],
                    "logs": self.deployment_logs
                }
                
        except Exception as e:
            self._update_status("error", f"Deployment error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "logs": self.deployment_logs
            }
    
    def stop_deployment(self) -> Dict[str, Any]:
        """Stop the current deployment."""
        
        try:
            if self.deployment_dir:
                # Stop Docker Compose services
                result = subprocess.run(
                    ["docker-compose", "down"],
                    cwd=self.deployment_dir,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.returncode == 0:
                    self._update_status("stopped", "Deployment stopped successfully")
                    return {"success": True, "message": "Deployment stopped"}
                else:
                    return {"success": False, "error": result.stderr}
            else:
                return {"success": False, "error": "No active deployment"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_deployment_status(self) -> Dict[str, Any]:
        """Get current deployment status."""
        
        return {
            "status": self.deployment_status,
            "logs": self.deployment_logs[-10:],  # Last 10 log entries
            "deployment_dir": str(self.deployment_dir) if self.deployment_dir else None
        }
    
    def _extract_package(self, zip_path: str) -> Path:
        """Extract the pipeline package."""
        
        extract_dir = Path(tempfile.mkdtemp(prefix="pipeline_deployment_"))
        
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            zipf.extractall(extract_dir)
        
        # Find the actual package directory
        package_dirs = [d for d in extract_dir.iterdir() if d.is_dir()]
        if package_dirs:
            return package_dirs[0]
        else:
            return extract_dir
    
    def _check_prerequisites(self) -> Dict[str, Any]:
        """Check if all prerequisites are installed."""
        
        prerequisites = {
            "docker": ["docker", "--version"],
            "docker-compose": ["docker-compose", "--version"]
        }
        
        missing = []
        
        for name, command in prerequisites.items():
            try:
                result = subprocess.run(command, capture_output=True, text=True, timeout=10)
                if result.returncode != 0:
                    missing.append(name)
                else:
                    self._log(f"✅ {name} is available: {result.stdout.strip()}")
            except (subprocess.TimeoutExpired, FileNotFoundError):
                missing.append(name)
        
        if missing:
            return {
                "success": False,
                "error": f"Missing prerequisites: {', '.join(missing)}"
            }
        
        return {"success": True}
    
    def _deploy_package(self) -> Dict[str, Any]:
        """Deploy the extracted package."""
        
        try:
            # Check package metadata
            metadata_path = self.deployment_dir / "package_metadata.json"
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                package_type = metadata.get("package_type", "standard")
            else:
                package_type = "standard"
            
            self._log(f"Deploying {package_type} package...")
            
            # Check for deployment script
            deploy_script = self.deployment_dir / "deploy_now.sh"
            if deploy_script.exists():
                return self._run_deployment_script(deploy_script)
            
            # Check for Docker Compose
            compose_file = self.deployment_dir / "docker-compose.yml"
            if compose_file.exists():
                return self._deploy_with_docker_compose()
            
            # Fallback to Python execution
            return self._deploy_python_pipeline()
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _run_deployment_script(self, script_path: Path) -> Dict[str, Any]:
        """Run the deployment script."""
        
        try:
            # Make script executable
            script_path.chmod(0o755)
            
            # Run deployment script
            process = subprocess.Popen(
                [str(script_path)],
                cwd=self.deployment_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Stream output
            for line in iter(process.stdout.readline, ''):
                self._log(line.strip())
            
            process.wait()
            
            if process.returncode == 0:
                return {"success": True}
            else:
                return {"success": False, "error": "Deployment script failed"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _deploy_with_docker_compose(self) -> Dict[str, Any]:
        """Deploy using Docker Compose."""
        
        try:
            # Build and start services
            self._log("Building Docker images...")
            build_result = subprocess.run(
                ["docker-compose", "build"],
                cwd=self.deployment_dir,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if build_result.returncode != 0:
                self._log(f"Build error: {build_result.stderr}")
                return {"success": False, "error": "Docker build failed"}
            
            self._log("Starting services...")
            up_result = subprocess.run(
                ["docker-compose", "up", "-d"],
                cwd=self.deployment_dir,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if up_result.returncode == 0:
                self._log("Services started successfully")
                return {"success": True}
            else:
                self._log(f"Startup error: {up_result.stderr}")
                return {"success": False, "error": "Service startup failed"}
                
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Deployment timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _deploy_python_pipeline(self) -> Dict[str, Any]:
        """Deploy Python pipeline directly."""
        
        try:
            # Install requirements
            requirements_file = self.deployment_dir / "requirements.txt"
            if requirements_file.exists():
                self._log("Installing requirements...")
                pip_result = subprocess.run(
                    ["pip", "install", "-r", str(requirements_file)],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                if pip_result.returncode != 0:
                    return {"success": False, "error": "Requirements installation failed"}
            
            # Find main pipeline file
            main_files = ["main_app.py", "data_pipeline.py", "src/main_pipeline.py"]
            main_file = None
            
            for file_name in main_files:
                file_path = self.deployment_dir / file_name
                if file_path.exists():
                    main_file = file_path
                    break
            
            if not main_file:
                return {"success": False, "error": "No main pipeline file found"}
            
            # Start pipeline in background
            self._log(f"Starting pipeline: {main_file}")
            self.deployment_process = subprocess.Popen(
                ["python", str(main_file)],
                cwd=self.deployment_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            return {"success": True}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _wait_for_health_check(self, max_wait: int = 60) -> Dict[str, Any]:
        """Wait for services to be healthy."""
        
        endpoints = [
            "http://localhost:8000/health",
            "http://localhost:8000/"
        ]
        
        for attempt in range(max_wait):
            for endpoint in endpoints:
                try:
                    response = requests.get(endpoint, timeout=5)
                    if response.status_code == 200:
                        self._log(f"✅ Service healthy at {endpoint}")
                        return {
                            "success": True,
                            "endpoints": {
                                "api": "http://localhost:8000",
                                "docs": "http://localhost:8000/docs",
                                "health": "http://localhost:8000/health"
                            }
                        }
                except requests.RequestException:
                    pass
            
            time.sleep(1)
            if attempt % 10 == 0:
                self._log(f"Waiting for services... ({attempt}/{max_wait})")
        
        return {"success": False, "error": "Health check timeout"}
    
    def _update_status(self, status: str, message: str):
        """Update deployment status."""
        self.deployment_status = status
        self._log(message)
        
        if self.status_callback:
            self.status_callback(status, message)
    
    def _log(self, message: str):
        """Add log message."""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.deployment_logs.append(log_entry)
        print(log_entry)  # Also print to console
    
    def cleanup(self):
        """Clean up deployment resources."""
        if self.deployment_dir and Path(self.deployment_dir).exists():
            try:
                # Stop services first
                subprocess.run(
                    ["docker-compose", "down"],
                    cwd=self.deployment_dir,
                    capture_output=True,
                    timeout=30
                )
            except:
                pass
            
            # Clean up directory
            shutil.rmtree(self.deployment_dir, ignore_errors=True)
