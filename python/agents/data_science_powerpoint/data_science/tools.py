# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Top level agent for data agent multi-agents.

-- it get data from database (e.g., BQ) using NL2SQL
-- then, it use NL2Py to do further data analysis as needed
"""

import os
from google.adk.tools import ToolContext
from google.adk.tools.agent_tool import AgentTool

from .sub_agents import ds_agent, db_agent
import httpx # Import httpx for making HTTP requests
from .utils.pptx_reader import extract_text_from_pptx
# from .utils.vertex_vector_search import query_vector_search_index # No longer needed directly


async def call_db_agent(
    question: str,
    tool_context: ToolContext,
):
    """Tool to call database (nl2sql) agent."""
    print(
        "\n call_db_agent.use_database:"
        f' {tool_context.state["all_db_settings"]["use_database"]}'
    )

    agent_tool = AgentTool(agent=db_agent)

    db_agent_output = await agent_tool.run_async(
        args={
            "request": question,
            "all_bq_ddl_schemas": tool_context.state["database_settings"]["all_bq_ddl_schemas"],
            "bq_project_id": tool_context.state["database_settings"]["bq_project_id"],
        },
        tool_context=tool_context
    )
    tool_context.state["db_agent_output"] = db_agent_output
    return db_agent_output


async def call_ds_agent(
    question: str,
    tool_context: ToolContext,
):
    """Tool to call data science (nl2py) agent."""

    if question == "N/A":
        return tool_context.state["db_agent_output"]

    input_data = tool_context.state["query_result"]

    question_with_data = f"""
  Question to answer: {question}

  Actual data to analyze prevoius quesiton is already in the following:
  {input_data}

  """

    agent_tool = AgentTool(agent=ds_agent)

    ds_agent_output = await agent_tool.run_async(
        args={"request": question_with_data}, tool_context=tool_context
    )
    tool_context.state["ds_agent_output"] = ds_agent_output
    return ds_agent_output


async def read_powerpoint_file(
    file_path: str,
    tool_context: ToolContext,
):
    """Tool to read text content from a PowerPoint file."""
    extracted_text = extract_text_from_pptx(file_path)
    tool_context.state["powerpoint_text"] = extracted_text
    return extracted_text


async def query_powerpoint_rag(
    question: str,
    tool_context: ToolContext,
):
    """Tool to query the external PowerPoint RAG service for relevant information."""
    rag_service_url = os.getenv("POWERPOINT_RAG_SERVICE_URL")

    if not rag_service_url:
        return "Error: POWERPOINT_RAG_SERVICE_URL environment variable is not set. Please configure it in your .env file."

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{rag_service_url}/query",
                json={"query": question},
                timeout=30.0 # Add a timeout for the request
            )
            response.raise_for_status() # Raise an exception for 4xx or 5xx status codes
            
            response_data = response.json()
            relevant_content = response_data.get("relevant_content", "No relevant content found.")
            
            tool_context.state["powerpoint_rag_results"] = relevant_content
            return relevant_content
    except httpx.RequestError as e:
        return f"Error connecting to PowerPoint RAG service: {e}"
    except httpx.HTTPStatusError as e:
        return f"Error from PowerPoint RAG service: {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"An unexpected error occurred while querying RAG service: {e}"
