from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec
from src.shared.utils import get_env_variable

pc_client = Pinecone(api_key=get_env_variable("PINECONE_API_KEY"))
openai_client = OpenAI(api_key=get_env_variable("OPEN_AI_API_KEY"))