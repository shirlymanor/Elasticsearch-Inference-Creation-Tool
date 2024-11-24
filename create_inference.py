from elasticsearch import Elasticsearch, ApiError, ConnectionTimeout, NotFoundError
import os
import time
from dotenv import load_dotenv
load_dotenv() 

def main():
    api_key = os.getenv("ELASTIC_API_KEY")
    if not api_key:
        print("Error: ELASTIC_API_KEY environment variable is not set.")
        return

    client = Elasticsearch(
        "https://my-elastic-project-a943bc.es.us-east-1.aws.elastic.cloud:443",
        api_key=api_key
    )

    # Check connection and print cluster info
    try:
        info = client.info()
        print(f"Connected to Elasticsearch cluster: {info['cluster_name']}")
        print(f"Elasticsearch version: {info['version']['number']}")
    except ApiError as e:
        print(f"Error connecting to Elasticsearch: {e}")
        return

    # Create or get existing inference
    inference_id = "elser_embeddings"
    create_or_get_inference(client, inference_id)

def create_or_get_inference(client, inference_id):
    max_retries = 3
    retry_delay = 5

    for attempt in range(max_retries):
        try:
            # Check if inference already exists
            try:
                existing_inference = client.inference.get(task_type="sparse_embedding", inference_id=inference_id)
                print(f"Inference '{inference_id}' already exists:")
                print(existing_inference)
                return
            except NotFoundError:
                # Inference doesn't exist, proceed with creation
                pass

            resp = client.inference.put(
                task_type="sparse_embedding",
                inference_id=inference_id,
                inference_config={
                    "service": "elser",
                    "service_settings": {
                        "num_allocations": 1,
                        "num_threads": 1
                    }
                }
            )
            print("Inference creation response:")
            print(resp)
            return
        except ConnectionTimeout:
            if attempt < max_retries - 1:
                print(f"Connection timed out. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("Max retries reached. Unable to create inference due to connection timeout.")
        except ApiError as e:
            print(f"Error creating inference: {e}")
            if "Model IDs must be unique" in str(e):
                new_id = f"{inference_id}_{int(time.time())}"
                print(f"Attempting to create inference with a new ID: {new_id}")
                create_or_get_inference(client, new_id)
            return

if __name__ == "__main__":
    main()