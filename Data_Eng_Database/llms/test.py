
import os
from openai import AzureOpenAI
# from prefect import task, flow
from typing import List, Dict, Optional, Union, Any

# @task(name="generate_azure_completions")
def generate_completions(
    messages: List[Dict[str, str]], 
    model_name: str,
    temperature: Optional[float] = None,
    top_p: Optional[float] = None,
    n: Optional[int] = None,
    stream: Optional[bool] = None,
    max_tokens: Optional[int] = None,
    echo: Optional[bool] = None,
    presence_penalty: Optional[float] = None,
    frequency_penalty: Optional[float] = None,
    logit_bias: Optional[Dict[str, float]] = None,
    logprobs: Optional[int] = None,
    user: Optional[str] = None,
    stop: Optional[Union[str, List[str]]] = None,
    seed: Optional[int] = None,
    suffix: Optional[str] = None,
    azure_endpoint: Optional[str] = None,
    api_key: Optional[str] = None,
    api_version: Optional[str] = None
):
    """
    Generate completions using Azure OpenAI API.
    
    Args:
        messages: List of message dictionaries with 'role' and 'content' (REQUIRED)
        model_name: Name of the deployment model to use (REQUIRED)
        temperature: Controls randomness (0-2)
        top_p: Controls diversity via nucleus sampling (0-1)
        n: Number of completions to generate
        stream: Whether to stream responses
        max_tokens: Maximum number of tokens to generate
        presence_penalty: Penalty for new tokens based on presence in text (0-2)
        frequency_penalty: Penalty for new tokens based on frequency in text (0-2)
        logit_bias: Bias for specific tokens
        user: Unique user identifier
        stop: Sequences where API will stop generating
        functions: Function definitions
        function_call: Function call behavior control
        response_format: Response format options
        seed: Random number generator seed
        azure_endpoint: Azure OpenAI endpoint URL
        api_key: Azure OpenAI API key
        api_version: API version to use
        
    Returns:
        The completion text
    """
    # Initialize the Azure OpenAI client
    client = AzureOpenAI(
        azure_endpoint=azure_endpoint,
        api_key=api_key,
        api_version=api_version
    )
    
    # Create a dictionary of all optional parameters
    optional_params = {
        "temperature": temperature,
        "top_p": top_p,
        "n": n,
        "stream": stream,
        "max_tokens": max_tokens,
        "echo": echo,
        "presence_penalty": presence_penalty,
        "frequency_penalty": frequency_penalty,
        "logit_bias": logit_bias,
        "logprobs": logprobs,
        "user": user,
        "stop": stop,
        "seed": seed,
        "suffix": suffix,
    }
    
    # Create base params with only the required ones
    completion_params = {
        "model": model_name,
        "messages": messages,
    }
    
    # Add only non-None optional parameters
    completion_params.update({k: v for k, v in optional_params.items() if v is not None})
    
    # Generate completions
    response = client.chat.completions.create(**completion_params)
    
    # if stream:
    #     for chunk in response:
    #         print(chunk.choices[0].delta.content, end='', flush=True)
    #     return 

    # Extract and return the completion
    completion = response.choices[0].message.content
    return completion

# @flow(name="azure_openai_flow")
def azure_openai_flow(model_name: str = "gpt-4o"):

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Does Azure OpenAI support customer managed keys? Do other Azure AI services support this too?"}
    ]

    
    # Run the task with only required parameters
    completion = generate_completions(messages=messages, model_name=model_name)
    
    
    return completion

# Run the flow if executed directly
if __name__ == "__main__":
    azure_openai_flow()

##################################################################################################################################################################################################################
# import os
# import json
# import boto3
# # from prefect import task, flow
# from typing import List, Dict, Optional, Union, Any


# # @task(name="generate_bedrock_completions")
# def generate_completions(
#     messages: List[Dict[str, str]], 
#     model_id: str,
#     region_name: str,
#     aws_access_key_id: str,
#     aws_secret_access_key: str,
#     temperature: Optional[float] = None,
#     top_p: Optional[float] = None,
#     top_k: Optional[int] = None,
#     max_tokens: Optional[int] = None,
#     stop_sequences: Optional[List[str]] = None,
#     anthropic_version: Optional[str] = None
# ):
#     """
#     Generate completions using Amazon Bedrock API with Anthropic Claude models.
    
#     Args:
#         messages: List of message dictionaries with 'role' and 'content' (REQUIRED)
#             System message (role="system") is optional
#         model_id: The Bedrock model ID to use (e.g., 'anthropic.claude-3-sonnet-20240229-v1:0') (REQUIRED)
#         region_name: AWS region name (REQUIRED)
#         aws_access_key_id: AWS access key ID (REQUIRED)
#         aws_secret_access_key: AWS secret access key (REQUIRED)
#         temperature: Controls randomness (0-1)
#         top_p: Controls diversity via nucleus sampling (0-1)
#         top_k: Number of highest probability tokens to consider
#         max_tokens: Maximum number of tokens to generate
#         stop_sequences: List of sequences where the model will stop generating
#         anthropic_version: Version of the Anthropic API to use
        
#     Returns:
#         The completion text
#     """
    
#     # Initialize the Bedrock Runtime client
#     bedrock_runtime = boto3.client(
#         service_name='bedrock-runtime',
#         region_name=region_name,
#         aws_access_key_id=aws_access_key_id,
#         aws_secret_access_key=aws_secret_access_key
#     )
    
#     # Extract system message and build Claude messages format 
#     system_message = None
#     claude_messages = []
    
#     for msg in messages:
#         if msg["role"] == "system":
#             system_message = msg["content"]
#         else:
#             claude_messages.append({"role": msg["role"], "content": msg["content"]})
    

#     request_body = {
#         "anthropic_version": anthropic_version or "bedrock-2023-05-31",
#         "messages": claude_messages,
#     }
    
    
#     if system_message:
#         request_body["system"] = system_message
    
#     # Add optional parameters if they are provided
#     if temperature is not None:
#         request_body["temperature"] = temperature
#     if top_p is not None:
#         request_body["top_p"] = top_p
#     if top_k is not None:
#         request_body["top_k"] = top_k
#     if max_tokens is not None:
#         request_body["max_tokens"] = max_tokens
#     if stop_sequences is not None:
#         request_body["stop_sequences"] = stop_sequences
    

#     body = json.dumps(request_body)
    
#     response = bedrock_runtime.invoke_model(
#         modelId=model_id,
#         body=body
#     )
    
#     response_body = json.loads(response.get("body").read())

#     completion = response_body["content"][0]["text"]
#     return completion


# # @flow(name="bedrock_anthropic_flow")
# def bedrock_anthropic_flow(
#     user_message: str,
#     region_name: str,
#     aws_access_key_id: str,
#     aws_secret_access_key: str,
#     system_message: Optional[str] = None,
#     model_id: str = "anthropic.claude-3-haiku-20240307-v1:0",
#     **kwargs
# ):
#     """
#     Prefect flow for generating text completions using Amazon Bedrock with Anthropic Claude models.
    
#     Args:
#         user_message: The user message to complete (REQUIRED)
#         region_name: AWS region name (REQUIRED)
#         aws_access_key_id: AWS access key ID (REQUIRED)
#         aws_secret_access_key: AWS secret access key (REQUIRED)
#         system_message: The system message for Claude (OPTIONAL)
#         model_id: The Bedrock model ID to use (default is Claude 3 Haiku)
#         **kwargs: Additional parameters to pass to the completion function
        
#     Returns:
#         The completion text
#     """
#     if not user_message:
#         raise ValueError("User message is required")
    
#     if not region_name:
#         raise ValueError("AWS region name is required")
    
#     if not aws_access_key_id:
#         raise ValueError("AWS access key ID is required")
    
#     if not aws_secret_access_key:
#         raise ValueError("AWS secret access key is required")

#     # Create the messages list
#     messages = [{"role": "user", "content": user_message}]
    
#     # Add system message if provided
#     if system_message:
#         messages.insert(0, {"role": "system", "content": system_message})
    
#     # Run the task with required and optional parameters
#     completion = generate_completions(
#         messages=messages, 
#         model_id=model_id,
#         region_name=region_name,
#         aws_access_key_id=aws_access_key_id,
#         aws_secret_access_key=aws_secret_access_key,
#         **kwargs
#     )
    
#     print(completion)

#     return completion


# ###########################################################################################################################################################


# # Run the flow if executed directly
# if __name__ == "__main__":
#     bedrock_anthropic_flow(
#         system_message="You are a helpful assistant.",
#         user_message="Does Azure OpenAI support customer managed keys? Do other Azure AI services support this too?",
#         region_name=" ",
#         aws_access_key_id="",
#         aws_secret_access_key="",
#         temperature=0.5,
#         top_p=0.5,
#         top_k=5,
#         max_tokens=100

#     )