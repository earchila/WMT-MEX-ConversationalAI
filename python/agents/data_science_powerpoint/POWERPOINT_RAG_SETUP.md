# PowerPoint RAG Agent Setup and Testing Instructions

This document provides comprehensive instructions for setting up the Google Cloud Platform (GCP) resources and testing the `Data_Science_PowerPoint` agent, which is integrated with a Vertex AI Vector Search-based Retrieval Augmented Generation (RAG) system for PowerPoint files.

## Summary of Implementation:

*   **New Agent Directory:** `adk-samples/python/agents/data_science_powerpoint` was created, based on `Data_Science_v2`.
*   **Main Agent Dependencies:** `pyproject.toml` was updated to include `httpx` for making HTTP requests to the RAG service.
*   **PowerPoint RAG Service (Isolated Environment):**
    *   A new Python project `adk-samples/python/powerpoint_rag_service` was created.
    *   Utility scripts (`pptx_reader.py`, `gcs_ingestion.py`, `vertex_vector_search.py`) were moved to this new service project.
    *   A dedicated `pyproject.toml` for this service was created with its own dependencies (`fastapi`, `uvicorn`, `google-cloud-aiplatform`, `google-cloud-storage`, `python-pptx`, `python-dotenv`), ensuring no dependency conflicts with `google-adk`.
    *   A FastAPI application (`main.py`) was implemented in this service with:
        *   A `/query` endpoint to receive queries and return relevant PowerPoint content from Vertex AI Vector Search.
        *   An `/ingest` endpoint to trigger PowerPoint file processing and indexing.
*   **Agent Tools:**
    *   The `read_powerpoint_file` tool in the main agent remains for reading specific PowerPoint files.
    *   The `query_powerpoint_rag` tool in the main agent was modified to make HTTP requests to the deployed PowerPoint RAG service.
*   **Agent Logic:**
    *   `data_science/agent.py` was updated to include the new tools.
    *   `data_science/prompts.py` was updated to instruct the agent on when to use `read_powerpoint_file` (for specific file queries) and `query_powerpoint_rag` (for general questions over indexed PowerPoint content).
*   **Environment Variables:**
    *   `data_science/envExample` in the main agent now includes `POWERPOINT_RAG_SERVICE_URL`.
    *   The `powerpoint_rag_service` will also need its own `.env` file with `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`, `GCS_POWERPOINT_BUCKET`, `VERTEX_AI_VECTOR_SEARCH_INDEX_ID`, and `VERTEX_AI_VECTOR_SEARCH_ENDPOINT_ID`.

---

## Setup and Testing Instructions:

### Step 1: Install Dependencies for Main Agent

Navigate to the main agent's directory and install the dependencies using Poetry:

```bash
cd adk-samples/python/agents/data_science_powerpoint
poetry install
```

### Step 2: Google Cloud Project Setup (Manual Steps)

You need to set up the following resources in your Google Cloud Project. Ensure you have the necessary IAM permissions.

1.  **Enable APIs:** Ensure the following APIs are enabled in your GCP project:
    *   Vertex AI API
    *   Cloud Storage API
    *   Cloud Build API (if you plan to use Cloud Build for deployment)

2.  **Create a Google Cloud Storage Bucket:**
    *   Create a GCS bucket where you will upload your PowerPoint files. Choose a unique name, e.g., `gs://your-powerpoint-bucket-unique-name`.
    *   **Create/Update `.env` for PowerPoint RAG Service:**
        *   Navigate to `adk-samples/python/powerpoint_rag_service`.
        *   Create a file named `.env` (if it doesn't exist).
        *   Add the following variables to this `.env` file, replacing placeholders with your actual values:
            ```
            GOOGLE_CLOUD_PROJECT='your-gcp-project-id'
            GOOGLE_CLOUD_LOCATION='us-central1' # Or your preferred region
            GCS_POWERPOINT_BUCKET='your-powerpoint-bucket-unique-name'
            VERTEX_AI_VECTOR_SEARCH_INDEX_ID='your-vector-search-index-id' # Will be populated in Step 2.3
            VERTEX_AI_VECTOR_SEARCH_ENDPOINT_ID='your-vector-search-endpoint-id' # Will be populated in Step 2.3
            ```

3.  **Set up Vertex AI Vector Search:**
    *   **Create an Index:** Follow the [Vertex AI documentation for creating a Vector Search Index](https://cloud.google.com/vertex-ai/docs/matching-engine/create-manage-index). You will need to specify:
        *   **Region:** (e.g., `us-central1`) - Must match `GOOGLE_CLOUD_LOCATION` in your `.env`.
        *   **Distance Measure:** (e.g., `DOT_PRODUCT`, `COSINE_DISTANCE`, `EUCLIDEAN_DISTANCE`) - Choose based on your embedding model.
        *   **Approximate Neighbors Count:** (e.g., `1000`)
        *   **Input Data Schema:** The `gcs_ingestion.py` script generates data in JSONL format with `id`, `embedding`, and `metadata`.
        *   **Input GCS Path:** This will be the GCS path where `gcs_ingestion.py` uploads the processed JSONL files (e.g., `gs://your-powerpoint-bucket-unique-name/vector_search_data/`).
    *   **Deploy the Index to an Endpoint:** After creating the Index, deploy it to an Index Endpoint.
    *   **Update `.env` for PowerPoint RAG Service:** Once the Index and Endpoint are created, update the `VERTEX_AI_VECTOR_SEARCH_INDEX_ID` and `VERTEX_AI_VECTOR_SEARCH_ENDPOINT_ID` in `adk-samples/python/powerpoint_rag_service/.env` with their respective IDs.

### Step 3: Deploy the PowerPoint RAG Service (Manual Step)

Deploy the `powerpoint_rag_service` as a web service. Cloud Run is recommended for ease of deployment and scalability.

*   **For Cloud Run:**
    1.  Navigate to the `adk-samples/python/powerpoint_rag_service` directory.
    2.  Build and deploy the service using `gcloud run deploy`. You'll need to specify the service name, region, and allow unauthenticated invocations if it's a public API.
        ```bash
        gcloud run deploy powerpoint-rag-service \
          --source . \
          --region your-gcp-location \
          --allow-unauthenticated \
          --set-env-vars GOOGLE_CLOUD_PROJECT=your-gcp-project-id,GOOGLE_CLOUD_LOCATION=your-gcp-location,GCS_POWERPOINT_BUCKET=your-powerpoint-bucket-unique-name,VERTEX_AI_VECTOR_SEARCH_INDEX_ID=your-vector-search-index-id,VERTEX_AI_VECTOR_SEARCH_ENDPOINT_ID=your-vector-search-endpoint-id
        ```
        *Replace placeholders with your actual values.*
    3.  Once deployed, note the service URL (e.g., `https://powerpoint-rag-service-xxxxxx-uc.a.run.app`).

*   **For Cloud Functions (2nd gen):**
    1.  You can deploy the `/query` and `/ingest` endpoints as separate HTTP-triggered Cloud Functions. Refer to Cloud Functions documentation for deployment details.
    2.  Note the URLs of the deployed functions.

**Update `.env` for Main Agent:**
*   Navigate to `adk-samples/python/agents/data_science_powerpoint/data_science`.
*   Create a file named `.env` (if it doesn't exist).
*   Set `POWERPOINT_RAG_SERVICE_URL` to the URL of your deployed RAG service (e.g., `https://your-rag-service-url.run.app`).

### Step 4: Ingest PowerPoint Files

1.  **Upload PowerPoint files to your GCS bucket:** Place your `.pptx` files into the GCS bucket you created (e.g., `gs://your-powerpoint-bucket-unique-name/my_presentation.pptx`).

2.  **Trigger Ingestion:**
    You can trigger the ingestion process by making an HTTP POST request to the `/ingest` endpoint of your deployed RAG service. For example, using `curl`:

    ```bash
    curl -X POST -H "Content-Type: application/json" \
         -d '{"bucket_name": "your-powerpoint-bucket-unique-name", "pptx_blob_name": "my_presentation.pptx"}' \
         https://your-rag-service-url.run.app/ingest
    ```
    Replace `your-powerpoint-bucket-unique-name`, `my_presentation.pptx`, and `https://your-rag-service-url.run.app` with your actual values.

### Step 5: Run the Agent and Test

1.  **Ensure your main agent's `.env` file is correctly configured** with the `POWERPOINT_RAG_SERVICE_URL`.

2.  **Integrate the agent into your application's agent orchestration system.**

3.  **Prompt the agent with questions:**

    *   **For specific PowerPoint file content (using `read_powerpoint_file`):**
        "Read the PowerPoint file located at `gs://your-powerpoint-bucket-unique-name/my_presentation.pptx` and tell me about the key findings."
        (Replace `gs://your-powerpoint-bucket-unique-name/my_presentation.pptx` with the actual GCS path to your file).

    *   **For general questions over indexed PowerPoint content (using `query_powerpoint_rag`):**
        "What are the main conclusions from the project overview presentations?"
        "Summarize the data analysis results from the PowerPoint documents."

The agent will use the `query_powerpoint_rag` tool to retrieve relevant information from your Vertex AI Vector Search Index via the deployed RAG service and then formulate a response based on that retrieved content.