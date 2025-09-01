
from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec
from cryptography.fernet import Fernet
from src.shared.env import get_env_variable
from supabase import create_client, Client

pc_client = Pinecone(api_key=get_env_variable("PINECONE_API_KEY"))
supabase_client: Client = create_client(get_env_variable("SUPABASE_URL"), get_env_variable("SUPABASE_KEY"))
fernet = Fernet(get_env_variable("FERNET_ENCRYPTION_KEY"))

def return_openai_client(api_key: str | None = None):
    if api_key is None:
        print("Using default OpenAI API key")
        openai_client = OpenAI(api_key=get_env_variable("OPEN_AI_API_KEY"))
        return openai_client
    else:
        print("Using provided OpenAI API key")
        openai_client = OpenAI(api_key=api_key)
        return openai_client
