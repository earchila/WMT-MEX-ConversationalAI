import json
from pymilvus import MilvusClient, FieldSchema, CollectionSchema, DataType

def create_and_populate_milvus_db(db_path: str, schema_json_path: str, data_json_path: str):
    """
    Creates a Milvus Lite database, defines a collection based on a schema,
    and populates it with data from JSON files.

    Args:
        db_path (str): The path where the Milvus Lite database will be stored.
        schema_json_path (str): The path to the JSON file containing the collection schema.
        data_json_path (str): The path to the JSON file containing the data to populate.
    """
    # Read schema from JSON file
    with open(schema_json_path, 'r') as f:
        schema_data = json.load(f)

    collection_name = schema_data['schema']['name']
    fields_config = schema_data['schema']['fields']
    
    fields = []
    for field_prop in fields_config:
        field_name = field_prop['name']
        data_type_str = field_prop['data_type'].upper()
        if data_type_str == "FLOATVECTOR":
            data_type_str = "FLOAT_VECTOR"
        elif data_type_str == "SPARSEFLOATVECTOR":
            data_type_str = "SPARSE_FLOAT_VECTOR"
        data_type = getattr(DataType, data_type_str)
        is_primary = field_prop.get('is_primary_key', False)
        auto_id = field_prop.get('autoID', False)
        is_partition_key = field_prop.get('is_partition_key', False)

        field_params = {
            "name": field_name,
            "dtype": data_type,
            "is_primary": is_primary,
            "auto_id": auto_id,
            "is_partition_key": is_partition_key
        }

        # Extract dim from type_params for vector fields
        if 'type_params' in field_prop:
            for param in field_prop['type_params']:
                if param['key'] == 'dim':
                    field_params['dim'] = int(param['value'])
                    break
            
        fields.append(FieldSchema(**field_params))

    schema = CollectionSchema(
        fields,
        description=schema_data.get('description', ""),
        enable_dynamic_field=schema_data.get('enable_dynamic_field', True)
    )

    # Initialize Milvus Lite client
    client = MilvusClient(db_path)

    # Create collection
    if client.has_collection(collection_name=collection_name):
        client.drop_collection(collection_name=collection_name)
    
    client.create_collection(
        collection_name=collection_name,
        schema=schema,
        shards_num=schema_data.get('shards_num', 1),
        consistency_level=schema_data.get('consistency_level', "Bounded")
    )

    # Read data from JSON file
    with open(data_json_path, 'r') as f:
        data = json.load(f)

    # Insert data
    client.insert(collection_name=collection_name, data=data)

    print(f"Milvus database created and populated at {db_path}")
    print(f"Collection '{collection_name}' created with {len(data)} entities.")

    client.close()

if __name__ == "__main__":
    # Example Usage:
    # Create dummy schema.json and data.json for demonstration
    schema_example = {
        "collection_name": "my_documents",
        "description": "A collection for storing documents and their embeddings",
        "enable_dynamic_field": True,
        "shards_num": 1,
        "consistency_level": "Bounded",
        "fields": {
            "id": {"data_type": "INT64", "is_primary": True, "auto_id": True},
            "embedding": {"data_type": "FLOAT_VECTOR", "dim": 128},
            "text": {"data_type": "VARCHAR", "max_length": 512},
            "category": {"data_type": "VARCHAR", "max_length": 128}
        }
    }

    data_example = [
        {"embedding": [0.1]*128, "text": "This is the first document.", "category": "A"},
        {"embedding": [0.2]*128, "text": "This is the second document.", "category": "B"},
        {"embedding": [0.3]*128, "text": "Another document here.", "category": "A"}
    ]

    # Define paths
    db_path = "./milvus_db.db"
    schema_json_path = "milvus_schema.json"
    data_json_path = "milvus_data.json"

    # Call the function
    create_and_populate_milvus_db(db_path, schema_json_path, data_json_path)

    # You can now interact with the created Milvus Lite database
    # For example, to verify:
    # client = MilvusClient(db_path)
    # print(client.query(collection_name="my_documents", filter="", output_fields=["id", "text", "category"]))
    # client.close()