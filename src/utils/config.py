import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings

load_dotenv()

def get_llm():
    return AzureChatOpenAI(
        azure_deployment=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT"),
        azure_endpoint=os.getenv("AZURE_OPENAI_API_BASE"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        temperature=0
    )

def get_embeddings():
    return AzureOpenAIEmbeddings(
        azure_deployment=os.getenv("AZURE_OPENAI_EMBED_MODEL"),
        azure_endpoint=os.getenv("AZURE_OPENAI_EMBED_API_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_EMBED_API_KEY"),
        openai_api_version=os.getenv("AZURE_OPENAI_EMBED_VERSION"),
    )