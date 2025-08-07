from pymilvus import MilvusClient, DataType, FieldSchema, CollectionSchema, Collection
import os
from dotenv import load_dotenv

class MilvusProductDB:
    def __init__(self, db_path: str = None):
        load_dotenv() # Load environment variables from .env file
        self.db_path = db_path if db_path else os.getenv("MILVUS_DB_PATH", "./milvus_product_db")
        self.client = MilvusClient(uri=self.db_path)
        self.collection_name = "product_embeddings"
        self._create_collection_if_not_exists()

    def _create_collection_if_not_exists(self):
        if self.client.has_collection(collection_name=self.collection_name):
            print(f"Collection '{self.collection_name}' already exists.")
            return

        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=False),
            FieldSchema(name="product_name", dtype=DataType.VARCHAR, max_length=256),
            FieldSchema(name="description", dtype=DataType.VARCHAR, max_length=512),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=768) # Assuming a common embedding dimension
        ]
        schema = CollectionSchema(fields, description="Product embeddings for substitute product search")
        self.client.create_collection(collection_name=self.collection_name, schema=schema)

        index_params = self.client.prepare_index_params()
        index_params.add_index(
            field_name="embedding",
            index_type="FLAT", # For simplicity, using FLAT. For larger datasets, consider HNSW, IVF_FLAT, etc.
            metric_type="L2" # Euclidean distance for similarity
        )
        self.client.create_index(collection_name=self.collection_name, index_params=index_params)
        print(f"Collection '{self.collection_name}' created and indexed.")

    def insert_products(self, products_data):
        """
        Inserts product data into the Milvus collection.
        products_data: List of dictionaries, each with 'id', 'product_name', 'description', 'embedding'.
        """
        if not products_data:
            return
        
        # MilvusClient.insert expects a list of dictionaries where keys match field names
        # and values are lists of data for each field.
        # Example:
        # {
        #   "id": [1, 2, 3],
        #   "product_name": ["Product A", "Product B", "Product C"],
        #   "description": ["Desc A", "Desc B", "Desc C"],
        #   "embedding": [[0.1, ...], [0.2, ...], [0.3, ...]]
        # }
        
        insert_data = {
            "id": [p["id"] for p in products_data],
            "product_name": [p["product_name"] for p in products_data],
            "description": [p["description"] for p in products_data],
            "embedding": [p["embedding"] for p in products_data]
        }
        
        res = self.client.insert(collection_name=self.collection_name, data=insert_data)
        print(f"Inserted {len(products_data)} products. Insert count: {res.insert_count}")
        self.client.flush(collection_name=self.collection_name) # Ensure data is written to disk

    def search_substitute_products(self, query_embedding, top_k=5):
        """
        Searches for substitute products based on a query embedding.
        query_embedding: The embedding of the product for which to find substitutes.
        top_k: Number of top similar products to return.
        """
        search_params = {
            "data": [query_embedding],
            "anns_field": "embedding",
            "limit": top_k,
            "output_fields": ["product_name", "description"]
        }
        res = self.client.search(collection_name=self.collection_name, **search_params)
        
        substitutes = []
        if res and res[0].ids:
            for hit in res[0]:
                substitutes.append({
                    "id": hit.id,
                    "product_name": hit.entity.get("product_name"),
                    "description": hit.entity.get("description"),
                    "distance": hit.distance
                })
        return substitutes

    def close(self):
        self.client.close()

# Example Usage (for testing purposes, not part of the agent's runtime)
if __name__ == "__main__":
    # This part would typically be handled by a separate data ingestion script
    # or a more sophisticated embedding generation process.
    
    # Dummy embedding generation (replace with actual embedding model)
    def generate_dummy_embedding(text):
        import numpy as np
        return np.random.rand(768).tolist() # 768-dimensional random vector

    db = MilvusProductDB(db_path="./milvus_data") # Persistent DB for testing, or None to use env var

    # Sample product data
    products = [
        {"id": 1, "product_name": "Red T-Shirt", "description": "Comfortable cotton t-shirt in red.", "embedding": generate_dummy_embedding("Red T-Shirt")},
        {"id": 2, "product_name": "Blue T-Shirt", "description": "Soft blue t-shirt, 100% organic cotton.", "embedding": generate_dummy_embedding("Blue T-Shirt")},
        {"id": 3, "product_name": "Green Polo Shirt", "description": "Stylish green polo for casual wear.", "embedding": generate_dummy_embedding("Green Polo Shirt")},
        {"id": 4, "product_name": "Red Hoodie", "description": "Warm red hoodie with a front pocket.", "embedding": generate_dummy_embedding("Red Hoodie")},
        {"id": 5, "product_name": "Black Jeans", "description": "Slim fit black jeans, durable denim.", "embedding": generate_dummy_embedding("Black Jeans")},
    ]

    db.insert_products(products)

    # Simulate a query for a substitute for "Red T-Shirt"
    # In a real scenario, you'd get the embedding of "Red T-Shirt" from your embedding model
    # For this example, we'll just use its own embedding to find similar items.
    query_product_name = "Red T-Shirt"
    query_embedding = next((p["embedding"] for p in products if p["product_name"] == query_product_name), None)

    if query_embedding:
        print(f"\nSearching for substitutes for '{query_product_name}':")
        substitutes = db.search_substitute_products(query_embedding, top_k=3)
        for sub in substitutes:
            print(f"  - {sub['product_name']} (Distance: {sub['distance']:.4f})")
    else:
        print(f"Product '{query_product_name}' not found for query.")

    db.close()