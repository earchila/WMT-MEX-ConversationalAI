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

from google.adk.tools import ToolContext
from google.adk.tools.agent_tool import AgentTool

from .sub_agents import ds_agent, db_agent
from .milvus_utils import MilvusProductDB
from typing import List, Dict, Optional


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


async def find_substitute_product(
    tool_context: ToolContext,
    product_name: Optional[str] = None,
    product_id: Optional[int] = None,
):
    """
    Tool to find substitute products using Milvus Lite.
    Args:
        tool_context: The tool context containing necessary state.
        product_name: The name of the product for which to find substitutes (optional).
        product_id: The ID of the product for which to find substitutes (optional).
    Returns:
        A list of dictionaries, each representing a substitute product with its details.
    """
    import numpy as np
    
    milvus_db_path = tool_context.state.get("milvus_db_path")
    milvus_db = MilvusProductDB(db_path=milvus_db_path)
    
    query_embedding = None
    product_identifier = None

    if product_id is not None:
        # Retrieve product by ID from Milvus to get its embedding
        # MilvusClient.query can be used to retrieve entities by ID
        # Note: This assumes 'id' is indexed and searchable.
        try:
            # Fetch the product by ID
            res = milvus_db.client.query(
                collection_name=milvus_db.collection_name,
                filter=f"id == {product_id}", # Use 'filter' instead of 'expr' for newer PyMilvus versions
                output_fields=["product_name", "embedding"]
            )
            if res:
                # Assuming ID is unique, take the first result
                product_data = res[0]
                query_embedding = product_data.get("embedding")
                product_identifier = product_data.get("product_name", f"ID: {product_id}")
            else:
                milvus_db.close()
                return [{"message": f"Product with ID {product_id} not found."}]
        except Exception as e:
            milvus_db.close()
            return [{"error": f"Error retrieving product by ID: {e}"}]

    elif product_name is not None:
        # Placeholder for embedding generation
        # In a real application, you'd use an LLM or a dedicated embedding model
        # to generate a meaningful embedding for the product name.
        def generate_embedding_for_product(name: str) -> list[float]:
            return np.random.rand(768).tolist() # Dummy 768-dim embedding
        
        query_embedding = generate_embedding_for_product(product_name)
        product_identifier = product_name
    else:
        milvus_db.close()
        return [{"message": "Please provide either a product name or a product ID."}]

    if query_embedding is None:
        milvus_db.close()
        return [{"message": f"Could not generate or retrieve embedding for {product_identifier}."}]

    substitutes = milvus_db.search_substitute_products(query_embedding, top_k=5)
    milvus_db.close() # Close the connection after use

    if substitutes:
        return substitutes
    else:
        return [{"message": f"No substitute products found for {product_identifier}."}]
