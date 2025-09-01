from fastapi import Request, HTTPException
from src.models.requests import QueryFileRequest, UserInfoFromJWT
from src.models.responses import QueryFileResponse, Source
from src.shared.utils import create_embedding_for_chunk,decrypt_encryption,build_prompt
from src.shared.constants import pinecone_index_name,completion_supported_model
from src.services.gateway_services import return_openai_client, pc_client

def process_file_query(request: Request, query_info: QueryFileRequest, user_info: UserInfoFromJWT) -> QueryFileResponse:
    try:
        index = pc_client.Index(pinecone_index_name)
        question = query_info.question

        question_embedding = create_embedding_for_chunk(
            content=question,
            user_info=user_info
        )

        search_results = index.query(
            vector=question_embedding,
            top_k=query_info.top_k or 5,
            namespace="__default__",
            include_metadata=True,
            filter={
                "user_id": {"$eq": user_info["user_id"]}
            }
        )

        if not search_results.matches:
            return QueryFileResponse(
                answer="I couldn’t find any relevant information in your documents.",
                sources=[]
            )

        retrieved_chunks = []
        context_texts = []
        for match in search_results.matches:
            metadata = match.metadata
            context_texts.append(metadata.get("original_text", ""))
            retrieved_chunks.append(Source(
                doc_id=metadata.get("doc_id"),
                page=metadata.get("page_num"),
            ))
            
        prompt = build_prompt(
            question=question,
            context_chunks=context_texts
        )

        decrypted_openai_key = decrypt_encryption(encryption=user_info["user_openai_key"])
        openai_client = return_openai_client(decrypted_openai_key)

        response = openai_client.chat.completions.create(
            model=completion_supported_model,
            messages=[
                {"role": "system", "content": prompt},
            ]
        )

        answer = response.choices[0].message.content.strip()

        return QueryFileResponse(
            answer=answer,
            sources=retrieved_chunks
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process query: {str(e)}")
