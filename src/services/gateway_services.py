
from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec
from src.shared.utils import get_env_variable
from supabase import create_client, Client

pc_client = Pinecone(api_key=get_env_variable("PINECONE_API_KEY"))
openai_client = OpenAI(api_key=get_env_variable("OPEN_AI_API_KEY"))
supabase_client: Client = create_client(get_env_variable("SUPABASE_URL"), get_env_variable("SUPABASE_KEY"))