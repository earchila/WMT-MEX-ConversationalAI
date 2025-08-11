import os
from google.cloud import aiplatform
from google.cloud.aiplatform.matching_engine.matching_engine_index_endpoint import MatchingEngineIndexEndpoint
from gcs_ingestion import generate_embeddings # Re-use the embedding function

def query_vector_search_index(
    query_text: str,
    project_id: str,
    location: str,
    index_id: str,
    endpoint_id: str,
    num_neighbors: int = 5
) -> list[dict]:
    """
    Queries a Vertex AI Vector Search Index Endpoint for relevant documents.
    """
    aiplatform.init(project=project_id, location=location)

    # Generate embedding for the query
    query_embedding = generate_embeddings([query_text], project_id, location)[0]

    # Get the Index Endpoint
    index_endpoint = MatchingEngineIndexEndpoint(
        index_endpoint_name=f"projects/{project_id}/locations/{location}/indexEndpoints/{endpoint_id}"
    )

    # Query the index
    response = index_endpoint.find_neighbors(
        queries=[query_embedding],
        num_neighbors=num_neighbors
    )

    results = []
    for res in response[0]: # Assuming single query
        results.append({
            "id": res.id,
            "distance": res.distance,
            "metadata": res.metadata # This will contain the original text and source file
        })
    return results

if __name__ == "__main__":
    # Example Usage (replace with your actual values)
    # Ensure you have authenticated to GCP and set up your Index and Endpoint.

    GCP_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "your-gcp-project-id")
    GCP_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    VERTEX_AI_VECTOR_SEARCH_INDEX_ID = os.getenv("VERTEX_AI_VECTOR_SEARCH_INDEX_ID", "your-index-id")
    VERTEX_AI_VECTOR_SEARCH_ENDPOINT_ID = os.getenv("VERTEX_AI_VECTOR_SEARCH_ENDPOINT_ID", "your-endpoint-id")

    if (GCP_PROJECT == "your-gcp-project-id" or
        VERTEX_AI_VECTOR_SEARCH_INDEX_ID == "your-index-id" or
        VERTEX_AI_VECTOR_SEARCH_ENDPOINT_ID == "your-endpoint-id"):
        print("Please set your GCP project, index, and endpoint IDs in the .env file or directly in the script for testing.")
    else:
        sample_query = "What are the key findings?"
        print(f"Querying for: {sample_query}")
        
        search_results = query_vector_search_index(
            query_text=sample_query,
            project_id=GCP_PROJECT,
            location=GCP_LOCATION,
            index_id=VERTEX_AI_VECTOR_SEARCH_INDEX_ID,
            endpoint_id=VERTEX_AI_VECTOR_SEARCH_ENDPOINT_ID
        )
        
        if search_results:
            print("\nSearch Results:")
            for result in search_results:
                print(f"ID: {result['id']}, Distance: {result['distance']}")
                if 'metadata' in result and result['metadata']:
                    # Metadata is a list of dicts, each with 'key' and 'value'
                    metadata_dict = {item['key']: item['value'] for item in result['metadata']}
                    print(f"  Source File: {metadata_dict.get('source_file')}")
                    print(f"  Text Content: {metadata_dict.get('text_content')[:200]}...") # Print first 200 chars
        else:
            print("No results found.")