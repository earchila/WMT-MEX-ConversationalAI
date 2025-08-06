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
    # OPTIONAL DEBUG LINE: Uncomment the line below to see the path it's trying to open
    # print(f"Attempting to open schema file at: {schema_json_path}") 
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
            "is_partition_key": is_partition_key,
            "is_function_output": field_prop.get('is_function_output', False)
        }

        if 'type_params' in field_prop:
            for param in field_prop['type_params']:
                if param['key'] == 'dim':
                    field_params['dim'] = int(param['value'])
                elif param['key'] == 'max_length':
                    field_params['max_length'] = int(param['value'])
            
        fields.append(FieldSchema(**field_params))

    schema = CollectionSchema(
        fields,
        description=schema_data.get('description', ""),
        enable_dynamic_field=schema_data.get('enable_dynamic_field', True)
    )

    client = MilvusClient(db_path)

    if client.has_collection(collection_name=collection_name):
        client.drop_collection(collection_name=collection_name)
    
    client.create_collection(
        collection_name=collection_name,
        schema=schema,
        shards_num=schema_data.get('shards_num', 1),
        consistency_level=schema_data.get('consistency_level', "Bounded")
    )

    with open(data_json_path, 'r') as f:
        data = json.load(f)

    processed_data = []
    for entity in data:
        new_entity = entity.copy()

        if 'product_number' in new_entity:
            new_entity['product_number'] = int(new_entity['product_number'])
        
        # Remove vector_sparse if it exists in the data, as it's no longer in the schema
        if 'vector_sparse' in new_entity:
            del new_entity['vector_sparse']

        processed_data.append(new_entity)

    client.insert(collection_name=collection_name, data=processed_data)

    print(f"Milvus database created and populated at {db_path}")
    print(f"Collection '{collection_name}' created with {len(processed_data)} entities.")

    client.close()

if __name__ == "__main__":
    db_path = "./milvus_db.db"
    # IMPORTANT: These paths are relative to the directory from which you run the script.
    # Since you are in 'milvus-lite' directory, these should be just the filenames.
    schema_json_path = "milvus_schema.json"
    data_json_path = "milvus_data.json"

    create_and_populate_milvus_db(db_path, schema_json_path, data_json_path)