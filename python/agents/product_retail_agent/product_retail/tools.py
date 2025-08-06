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
from typing import List, Dict


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
    product_name: str,
    tool_context: ToolContext,
) -> List[Dict]:
    """
    Tool to find substitute products using Milvus Lite.
    Args:
        product_name: The name of the product for which to find substitutes.
        tool_context: The tool context containing necessary state.
    Returns:
        A list of dictionaries, each representing a substitute product with its details.
    """
    # In a real scenario, you would generate an embedding for the product_name
    # using an embedding model (e.g., from Vertex AI, Sentence Transformers).
    # For this example, we'll use a dummy embedding.
    
    # Placeholder for embedding generation
    # You would replace this with actual model inference
    import numpy as np
    def generate_embedding_for_product(name: str) -> List[float]:
        # This is a dummy function. In a real application, you'd use an LLM
        # or a dedicated embedding model to generate a meaningful embedding.
        # For example:
        # from vertexai.language_models import TextEmbeddingModel
        # model = TextEmbeddingModel.from_pretrained("textembedding-gecko@001")
        # embeddings = model.get_embeddings([name])
        # return embeddings[0].values
        return np.random.rand(768).tolist() # Dummy 768-dim embedding

    query_embedding = generate_embedding_for_product(product_name)

    # Initialize MilvusProductDB (consider making this a singleton or passing it)
    # For simplicity, we'll initialize it here. In a production system,
    # you might manage the MilvusProductDB instance more carefully.
    milvus_db_path = tool_context.state.get("milvus_db_path")
    milvus_db = MilvusProductDB(db_path=milvus_db_path)

    substitutes = milvus_db.search_substitute_products(query_embedding, top_k=5)
    milvus_db.close() # Close the connection after use

    if substitutes:
        return substitutes
    else:
        return [{"message": f"No substitute products found for {product_name}."}]
