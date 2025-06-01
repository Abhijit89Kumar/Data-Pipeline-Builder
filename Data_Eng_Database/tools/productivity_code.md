#SLACK TOOL

```python

from langchain_community.agent_toolkits import SlackToolkit
from langgraph.prebuilt import create_react_agent
import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

@task(name="initialize_slack_tools")
def initialize_slack_tools(slack_token:str):
    """
    Initialize the Slack toolkit and return the available tools.
    
    Returns:
        List of Slack tools (SlackGetChannel, SlackGetMessage, 
        SlackScheduleMessage, SlackSendMessage)
    """
    # Initialize the Slack toolkit
    os.environ["SLACK_USER_TOKEN"]=slack_token
    toolkit = SlackToolkit()
    
    # Get the available tools
    tools = toolkit.get_tools()
    
    # Print available tools for information
    print("Available Slack tools:")
    for i, tool in enumerate(tools):
        print(f"  {i+1}. {tool.__class__.__name__}")
    
    return tools

@flow(name="demonstrate_slack_capabilities")
def demonstrate_slack_capabilities(slack_token:str,
                                   user_question:str,
                                   llm_api_key:str,
                                   llm_model_name:str):
    """
    Demonstrates various capabilities of the Slack integration with LangChain.
    Initializes the Slack tools and performs operations such as listing channels,
    getting channel info, retrieving messages, and sending messages.
    """
    # Initialize the Slack tools directly inside this function
    tools = initialize_slack_tools(slack_token=slack_token)
    
    # Initialize the LLM
    llm = ChatGroq(temperature=0, 
                   groq_api_key=llm_api_key, 
                   model_name=llm_model_name)
    
    # Create a ReAct agent with the LLM and tools
    agent_executor = create_react_agent(llm, tools)

    channel_result = agent_executor.invoke({"messages": [("user", user_question)]})

    print(f"Result: {channel_result['messages'][-1].content}")
    return channel_result['messages'][-1].content
    

if __name__ == "__main__":
    demonstrate_slack_capabilities()

```
## Jira Toolkit (by LangChain)

```python

from langchain_community.agent_toolkits.jira.toolkit import JiraToolkit
from langchain_community.utilities.jira import JiraAPIWrapper
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import os

def initialize_jira_tools(jira_instance_url: str, 
                          jira_username: str = None, 
                          jira_api_token: str = None,
                          jira_oauth2: dict = None,
                          jira_cloud: bool = True):
    """
    Initialize the Jira toolkit and return the available tools.
    
    Args:
        jira_instance_url: URL of the Jira instance
        jira_username: Jira username (for API token authentication)
        jira_api_token: Jira API token (for API token authentication)
        jira_oauth2: OAuth2.0 credentials as dict (for OAuth2.0 authentication)
        jira_cloud: Whether using Jira Cloud instance (True) or Server instance (False)
    
    Returns:
        List of Jira tools
    """
    # Set environment variables for authentication
    os.environ["JIRA_INSTANCE_URL"] = jira_instance_url
    os.environ["JIRA_CLOUD"] = str(jira_cloud)
    
    # Choose authentication method based on provided credentials
    if jira_api_token and jira_username:
        os.environ["JIRA_API_TOKEN"] = jira_api_token
        os.environ["JIRA_USERNAME"] = jira_username
        print("Using API token authentication")
    elif jira_oauth2:
        import json
        os.environ["JIRA_OAUTH2"] = json.dumps(jira_oauth2)
        print("Using OAuth2.0 authentication")
    else:
        raise ValueError("Either API token or OAuth2.0 credentials must be provided")
    
    # Initialize Jira API wrapper and toolkit
    jira = JiraAPIWrapper()
    toolkit = JiraToolkit.from_jira_api_wrapper(jira)
    
    # Get the available tools
    tools = toolkit.get_tools()
    
    return tools

def jira_agent(jira_instance_url: str,
              llm_api_key: str,
              user_query: str = None,
              llm_model_name: str = "llama3-70b-8192",
              jira_username: str = None, 
              jira_api_token: str = None,
              jira_oauth2: dict = None,
              jira_cloud: bool = True):
    """
    Creates a LangChain agent to interact with Jira using natural language.
    Can handle a single query or run a list of example queries.
    
    Args:
        jira_instance_url: URL of the Jira instance
        llm_api_key: API key for the LLM
        user_query: Natural language query from user (optional)
        example_queries: List of example queries to run (optional)
        llm_model_name: Model name to use
        jira_username: Jira username (for API token authentication)
        jira_api_token: Jira API token (for API token authentication)
        jira_oauth2: OAuth2.0 credentials as dict (for OAuth2.0 authentication)
        jira_cloud: Whether using Jira Cloud instance (True) or Server instance (False)
        
    Returns:
        Response from the agent or dictionary of responses for multiple queries
    """
    # Initialize Jira tools
    tools = initialize_jira_tools(
        jira_instance_url=jira_instance_url,
        jira_username=jira_username,
        jira_api_token=jira_api_token,
        jira_oauth2=jira_oauth2,
        jira_cloud=jira_cloud
    )
    
    # Initialize the LLM
    llm = ChatGroq(
        temperature=0,
        groq_api_key=llm_api_key,
        model_name=llm_model_name
    )
    
    # Create a ReAct agent with the LLM and tools
    agent_executor = create_react_agent(llm, tools)
    
    result = agent_executor.invoke({"messages": [("user", user_query)]})
    response = result['messages'][-1].content

    return response
    

if __name__ == "__main__":
    # Example usage
    
    jira_agent()

```