"""
Enhanced Streamlit Pipeline Generator App
Complete pipeline generation with AI agents, download, and local deployment
"""

import streamlit as st
import asyncio
import time
from pathlib import Path

# Import our custom modules
# Removed unused imports - Enterprise Grade only

try:
    from enterprise_pipeline_system import EnterpriseAgentOrchestrator, EnterpriseConfig, PipelineRequirements, PipelineComplexity, DeploymentTarget
except ImportError:
    EnterpriseAgentOrchestrator = None
    EnterpriseConfig = None
    PipelineRequirements = None
    PipelineComplexity = None
    DeploymentTarget = None

try:
    from pipeline_packager import PipelinePackager
except ImportError:
    PipelinePackager = None

try:
    from deployment_manager import DeploymentManager
except ImportError:
    DeploymentManager = None

# Page configuration
st.set_page_config(
    page_title="Enterprise AI Pipeline Generator",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    
    .feature-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    
    .status-success {
        background: #d4edda;
        color: #155724;
        padding: 0.75rem;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
    }
    
    .status-error {
        background: #f8d7da;
        color: #721c24;
        padding: 0.75rem;
        border-radius: 5px;
        border: 1px solid #f5c6cb;
    }
    
    .status-warning {
        background: #fff3cd;
        color: #856404;
        padding: 0.75rem;
        border-radius: 5px;
        border: 1px solid #ffeaa7;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    """Initialize session state variables."""
    # Enterprise Grade only - no multi-agent system needed

    if 'packager' not in st.session_state:
        if PipelinePackager:
            st.session_state.packager = PipelinePackager()
        else:
            st.session_state.packager = None

    if 'deployment_manager' not in st.session_state:
        if DeploymentManager:
            st.session_state.deployment_manager = DeploymentManager()
        else:
            st.session_state.deployment_manager = None
    
    if 'generated_pipeline' not in st.session_state:
        st.session_state.generated_pipeline = None
    
    if 'package_path' not in st.session_state:
        st.session_state.package_path = None
    
    if 'deployment_status' not in st.session_state:
        st.session_state.deployment_status = "idle"
    
    if 'deployment_logs' not in st.session_state:
        st.session_state.deployment_logs = []

def main():
    """Main application function."""
    
    init_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">🏢 Enterprise AI Pipeline Generator</h1>', unsafe_allow_html=True)
    st.markdown("### Generate enterprise-grade, production-ready data pipelines with full deployment capabilities")
    
    # Sidebar
    with st.sidebar:
        st.header("🎛️ Configuration")
        
        # Pipeline type selection - ENTERPRISE GRADE ONLY
        pipeline_type = st.selectbox(
            "Pipeline Type",
            ["Enterprise Grade"],
            help="Enterprise-grade production-ready pipeline with full deployment capabilities"
        )
        
        # Advanced options
        with st.expander("🔧 Enterprise Configuration"):
            show_enterprise_options()
        
        # System status
        st.header("📊 System Status")
        show_system_status()
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Pipeline description input
        st.header("📝 Describe Your Enterprise Pipeline")

        user_requirements = st.text_area(
            "Natural Language Description",
            placeholder="""Example: I want to build an enterprise pipeline that:
- Processes PDF documents from a folder
- Extracts text and creates embeddings using Azure OpenAI
- Stores them in a production-grade vector database
- Provides a scalable RAG-based question answering API
- Includes comprehensive monitoring, security, and logging
- Has auto-scaling and load balancing
- Can be deployed with Docker and Kubernetes
- Includes CI/CD pipeline and enterprise governance""",
            height=150,
            help="Describe your enterprise pipeline requirements in natural language. Be as detailed as possible."
        )
        
        # Generation controls
        col_gen1, col_gen2, col_gen3 = st.columns(3)
        
        with col_gen1:
            generate_btn = st.button("🚀 Generate Enterprise Pipeline", type="primary", use_container_width=True)
        
        with col_gen2:
            if st.session_state.generated_pipeline:
                package_btn = st.button("📦 Create Package", use_container_width=True)
            else:
                st.button("📦 Create Package", disabled=True, use_container_width=True)
        
        with col_gen3:
            if st.session_state.package_path:
                deploy_btn = st.button("🚀 Deploy Locally", use_container_width=True)
            else:
                st.button("🚀 Deploy Locally", disabled=True, use_container_width=True)
        
        # Handle generation
        if generate_btn and user_requirements:
            generate_pipeline(user_requirements, pipeline_type)
        
        # Handle packaging
        if 'package_btn' in locals() and package_btn:
            create_pipeline_package(pipeline_type)
        
        # Handle deployment
        if 'deploy_btn' in locals() and deploy_btn:
            deploy_pipeline_locally()
        
        # Display results
        display_pipeline_results()
    
    with col2:
        # Status panel
        st.header("📊 Status Panel")
        display_status_panel()
        
        # Quick actions
        st.header("⚡ Quick Actions")
        display_quick_actions()



def show_enterprise_options():
    """Show options for enterprise pipeline."""

    st.selectbox("Architecture Pattern", ["Microservices", "Monolithic", "Serverless"])
    st.selectbox("Database", ["PostgreSQL", "MongoDB", "Redis"])
    st.selectbox("Message Queue", ["Redis", "RabbitMQ", "Apache Kafka"])
    st.selectbox("Deployment Target", ["Docker Compose", "Kubernetes", "Both"])
    st.checkbox("Enable Monitoring", value=True)
    st.checkbox("Enable Security", value=True)
    st.checkbox("Enable Auto-scaling", value=True)
    st.checkbox("Include CI/CD Pipeline", value=True)

def show_system_status():
    """Show system status in sidebar."""

    # Check enterprise system components only
    status_items = [
        ("Enterprise Generator", "✅ Ready" if EnterpriseAgentOrchestrator else "❌ Not Available"),
        ("Package Manager", "✅ Ready" if PipelinePackager else "❌ Not Available"),
        ("Deployment Manager", "✅ Ready" if DeploymentManager else "❌ Not Available")
    ]

    for component, status in status_items:
        st.text(f"{component}: {status}")

def generate_pipeline(requirements: str, pipeline_type: str = "Enterprise Grade"):
    """Generate Enterprise Grade pipeline."""
    # Note: pipeline_type is always "Enterprise Grade" but kept for interface compatibility

    with st.spinner("Generating Enterprise Grade pipeline..."):
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            status_text.text("🏢 Generating enterprise components...")
            progress_bar.progress(20)

            if EnterpriseAgentOrchestrator and EnterpriseConfig and PipelineRequirements:
                config = EnterpriseConfig()
                orchestrator = EnterpriseAgentOrchestrator(config)

                # Create pipeline requirements
                pipeline_req = PipelineRequirements(
                    description=requirements,
                    use_case="enterprise_rag",
                    complexity=PipelineComplexity.ENTERPRISE if PipelineComplexity else None,
                    deployment_target=DeploymentTarget.PRODUCTION if DeploymentTarget else None
                )

                result = asyncio.run(orchestrator.generate_enterprise_pipeline(pipeline_req))
                progress_bar.progress(100)

                st.session_state.generated_pipeline = result
                status_text.text("✅ Enterprise pipeline generated successfully!")
            else:
                st.error("Enterprise system not available. Please check imports.")
                return

            st.success("Enterprise pipeline generated successfully! 🎉")

        except Exception as e:
            st.error(f"Pipeline generation failed: {str(e)}")
            st.session_state.generated_pipeline = None

def create_pipeline_package(pipeline_type: str = "Enterprise Grade"):
    """Create downloadable package for the generated Enterprise pipeline."""
    # Note: pipeline_type is always "Enterprise Grade" but kept for interface compatibility

    if not st.session_state.generated_pipeline:
        st.error("No pipeline to package!")
        return

    if not st.session_state.packager:
        st.error("Pipeline packager not available. Please check imports.")
        return

    with st.spinner("Creating enterprise pipeline package..."):
        try:
            package_path = st.session_state.packager.create_complete_package(
                st.session_state.generated_pipeline,
                "User requirements",  # You might want to store this
                "enterprise"
            )

            st.session_state.package_path = package_path
            st.success("Enterprise package created successfully! 📦")

        except Exception as e:
            st.error(f"Package creation failed: {str(e)}")

def deploy_pipeline_locally():
    """Deploy the pipeline package locally."""

    if not st.session_state.package_path:
        st.error("No package to deploy!")
        return

    if not st.session_state.deployment_manager:
        st.error("Deployment manager not available. Please check imports.")
        return

    def status_callback(status: str, message: str):
        """Callback for deployment status updates."""
        st.session_state.deployment_status = status
        st.session_state.deployment_logs.append(f"[{time.strftime('%H:%M:%S')}] {message}")

    with st.spinner("Deploying pipeline locally..."):
        try:
            result = st.session_state.deployment_manager.deploy_pipeline_package(
                st.session_state.package_path,
                status_callback
            )
            
            if result["success"]:
                st.success("Pipeline deployed successfully! 🚀")
                
                # Show endpoints
                if "endpoints" in result:
                    st.info("**Available Endpoints:**")
                    for name, url in result["endpoints"].items():
                        st.write(f"- **{name.title()}**: {url}")
            else:
                st.error(f"Deployment failed: {result['error']}")
                
        except Exception as e:
            st.error(f"Deployment error: {str(e)}")

def display_pipeline_results():
    """Display the generated pipeline results."""
    
    if st.session_state.generated_pipeline:
        st.header("📋 Generated Pipeline")
        
        # Create tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["📄 Code Preview", "⚙️ Configuration", "📖 Instructions", "📊 Plan"])
        
        with tab1:
            if "pipeline_code" in st.session_state.generated_pipeline:
                code = st.session_state.generated_pipeline["pipeline_code"]
                st.code(code[:2000] + "..." if len(code) > 2000 else code, language="python")
            else:
                st.info("Code preview not available for this pipeline type")
        
        with tab2:
            if "config_template" in st.session_state.generated_pipeline:
                st.code(st.session_state.generated_pipeline["config_template"], language="bash")
            else:
                st.info("Configuration not available for this pipeline type")
        
        with tab3:
            if "api_instructions" in st.session_state.generated_pipeline:
                st.markdown(st.session_state.generated_pipeline["api_instructions"])
            else:
                st.info("Instructions not available for this pipeline type")
        
        with tab4:
            if "plan" in st.session_state.generated_pipeline:
                st.json(st.session_state.generated_pipeline["plan"])
            else:
                st.info("Plan not available for this pipeline type")
        
        # Download section
        st.header("💾 Downloads")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if "pipeline_code" in st.session_state.generated_pipeline:
                st.download_button(
                    "📄 Download Code",
                    st.session_state.generated_pipeline["pipeline_code"],
                    file_name="pipeline.py",
                    mime="text/python"
                )
        
        with col2:
            if "config_template" in st.session_state.generated_pipeline:
                st.download_button(
                    "⚙️ Download Config",
                    st.session_state.generated_pipeline["config_template"],
                    file_name="config.env",
                    mime="text/plain"
                )
        
        with col3:
            if st.session_state.package_path:
                with open(st.session_state.package_path, 'rb') as f:
                    st.download_button(
                        "📦 Download Package",
                        f.read(),
                        file_name=Path(st.session_state.package_path).name,
                        mime="application/zip"
                    )

def display_status_panel():
    """Display the status panel."""
    
    # Generation status
    if st.session_state.generated_pipeline:
        st.markdown('<div class="status-success">✅ Pipeline Generated</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-warning">⏳ No Pipeline Generated</div>', unsafe_allow_html=True)
    
    # Package status
    if st.session_state.package_path:
        st.markdown('<div class="status-success">✅ Package Created</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-warning">⏳ No Package Created</div>', unsafe_allow_html=True)
    
    # Deployment status
    status_map = {
        "idle": ("⏳ Not Deployed", "status-warning"),
        "extracting": ("📦 Extracting...", "status-warning"),
        "checking": ("🔍 Checking...", "status-warning"),
        "deploying": ("🚀 Deploying...", "status-warning"),
        "waiting": ("⏳ Starting...", "status-warning"),
        "ready": ("✅ Running", "status-success"),
        "error": ("❌ Failed", "status-error"),
        "stopped": ("⏹️ Stopped", "status-warning")
    }
    
    status_text, status_class = status_map.get(st.session_state.deployment_status, ("❓ Unknown", "status-warning"))
    st.markdown(f'<div class="{status_class}">{status_text}</div>', unsafe_allow_html=True)
    
    # Deployment logs
    if st.session_state.deployment_logs:
        with st.expander("📋 Deployment Logs"):
            for log in st.session_state.deployment_logs[-10:]:
                st.text(log)

def display_quick_actions():
    """Display quick action buttons."""
    
    if st.button("🔄 Reset All", use_container_width=True):
        # Reset session state
        for key in ['generated_pipeline', 'package_path', 'deployment_status', 'deployment_logs']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
    
    if st.button("🛑 Stop Deployment", use_container_width=True):
        if st.session_state.deployment_status not in ["idle", "stopped"]:
            if st.session_state.deployment_manager:
                result = st.session_state.deployment_manager.stop_deployment()
                if result["success"]:
                    st.success("Deployment stopped")
                    st.session_state.deployment_status = "stopped"
                else:
                    st.error(f"Failed to stop: {result['error']}")
            else:
                st.error("Deployment manager not available")
    
    if st.button("📊 View Metrics", use_container_width=True):
        if st.session_state.deployment_status == "ready":
            st.info("Metrics available at: http://localhost:8000/metrics")
        else:
            st.warning("Deploy pipeline first to view metrics")

if __name__ == "__main__":
    main()
