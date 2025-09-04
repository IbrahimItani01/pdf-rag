# Server Data Related Constants
version = "0.0.1"
title = "PDF RAG API"
description = "API for PDF RAG"

# Upload API Related
allowed_file_extensions = {".pdf"}
allowed_file_size = 2 * 1024 * 1024 # 2MB
file_total_token_limit = 1000
overlap_tokens_count = 100
empty_page_threshold = 20

pinecone_index_name="pdf-rag-index"

embedding_supported_model= "text-embedding-3-small"
completion_supported_model= "gpt-5"

# TODO: change when ui login is done :)
email_confirm_redirect_url = "http://127.0.0.1:8080/login"

supabase_project_id = "meqqmoriaexmjnqchjmk"

base_prompt = """You are an assistant that answers based on the provided context.
If the answer isn’t in the context, just say something like:
"Sorry, I couldn’t find that in the provided information."

Question: {question}

Context:
{context}
"""

origins = [
    "http://localhost:8080",
    "http://127.0.0.1:8080"
]
