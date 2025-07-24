from  langchain_openai import AzureChatOpenAI
from langchain_aws import ChatBedrockConverse

from langchain_aws import ChatBedrockConverse

aws_llm = ChatBedrockConverse(
    model="anthropic.claude-3-5-sonnet-20241022-v2:0",
    temperature=0,
    max_tokens=None,
    # other params...
)

azure_llm = AzureChatOpenAI(
    azure_deployment="gpt-4.1-mini",  # or your deployment
    api_version="2024-12-01-preview",  # or your api version
    temperature=0,
    max_tokens=None,
    azure_endpoint="openai",
    api_key="hello",
    timeout=None,
    max_retries=6,
    top_p=0.8
)