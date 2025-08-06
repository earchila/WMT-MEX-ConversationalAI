import json

def clean_milvus_data_json(file_path: str):
    """
    Reads a JSON file, removes the 'vector_sparse' field from each object,
    and writes the modified data back to the same file.

    Args:
        file_path (str): The path to the milvus_data.json file.
    """
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)

        if not isinstance(data, list):
            print(f"Warning: The JSON data in {file_path} is not a list of objects. Skipping cleaning.")
            return

        modified_data = []
        for entry in data:
            if isinstance(entry, dict):
                new_entry = entry.copy()
                if 'vector_sparse' in new_entry:
                    del new_entry['vector_sparse']
                modified_data.append(new_entry)
            else:
                modified_data.append(entry)

        with open(file_path, 'w') as f:
            json.dump(modified_data, f, indent=4) # Use indent for readability

        print(f"Successfully cleaned '{file_path}': 'vector_sparse' field removed from all entries.")

    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
    except json.JSONDecodeError as e:
        print(f"Error: Could not decode JSON from {file_path}. Please check for syntax errors. Details: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    # CORRECTED PATH: Since you are running this script from within the 'milvus-lite' directory,
    # 'milvus_data.json' is directly in that directory.
    data_json_path = "milvus_data.json"
    clean_milvus_data_json(data_json_path)