"""
LLM service for managing language model interactions.
Supports Google Gemini (primary), OpenAI, and Azure OpenAI.
"""
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from app.config import settings
import os


def get_llm():
    """
    Get LLM instance based on configuration.
    Returns the same LLM type as used in the notebook (ChatGoogleGenerativeAI).
    """
    provider = settings.LLM_PROVIDER.lower()
    
    if provider == "google":
        # Set API key in environment (required by langchain-google-genai)
        os.environ["GOOGLE_API_KEY"] = settings.GOOGLE_API_KEY
        
        # Return exact same configuration as notebook
        return ChatGoogleGenerativeAI(
            model=settings.LLM_MODEL,
            temperature=settings.LLM_TEMPERATURE
        )
    
    elif provider == "openai":
        return ChatOpenAI(
            model=settings.LLM_MODEL,
            temperature=settings.LLM_TEMPERATURE,
            api_key=settings.OPENAI_API_KEY
        )
    
    elif provider == "azure":
        return AzureChatOpenAI(
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            api_key=settings.AZURE_OPENAI_KEY,
            api_version="2024-02-01",
            temperature=settings.LLM_TEMPERATURE
        )
    
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")


# Global LLM instance (same pattern as notebook)
llm = get_llm()
