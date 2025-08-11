import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import the functions from the moved files
from pptx_reader import extract_text_from_pptx
from gcs_ingestion import download_pptx_from_gcs, upload_to_gcs, generate_embeddings, process_pptx_for_vector_search
from vertex_vector_search import query_vector_search_index

app = FastAPI()

class QueryRequest(BaseModel):
    query: str

class IngestRequest(BaseModel):
    bucket_name: str
    pptx_blob_name: str

@app.post("/query")
async def query_rag(request: QueryRequest):
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION")
    index_id = os.getenv("VERTEX_AI_VECTOR_SEARCH_INDEX_ID")
    endpoint_id = os.getenv("VERTEX_AI_VECTOR_SEARCH_ENDPOINT_ID")

    if not all([project_id, location, index_id, endpoint_id]):
        raise HTTPException(status_code=500, detail="Vertex AI Vector Search environment variables are not set.")

    try:
        results = query_vector_search_index(
            query_text=request.query,
            project_id=project_id,
            location=location,
            index_id=index_id,
            endpoint_id=endpoint_id
        )
        # Extract relevant text content from the results
        relevant_content = "\n\n".join([
            item['metadata'][0]['value'] for item in results if item.get('metadata') and item['metadata'][0].get('value')
        ])
        return {"relevant_content": relevant_content, "raw_results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying RAG: {e}")

@app.post("/ingest")
async def ingest_pptx(request: IngestRequest):
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION")
    gcs_bucket = os.getenv("GCS_POWERPOINT_BUCKET")

    if not all([project_id, location, gcs_bucket]):
        raise HTTPException(status_code=500, detail="GCP environment variables are not set for ingestion.")

    try:
        process_pptx_for_vector_search(
            bucket_name=gcs_bucket,
            pptx_blob_name=request.pptx_blob_name,
            project_id=project_id,
            location=location,
            output_gcs_path=f"gs://{gcs_bucket}/vector_search_data/"
        )
        return {"message": f"Successfully initiated ingestion for {request.pptx_blob_name}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during ingestion: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)