from elasticsearch import Elasticsearch, ApiError, ConnectionTimeout, NotFoundError
import os
import time
from dotenv import load_dotenv

load_dotenv()

def create_or_get_inference(client, inference_id):
    max_retries = 3
    retry_delay = 5

    for attempt in range(max_retries):
        try:
            # Check if inference already exists
            try:
                existing_inference = client.inference.get(task_type="completion", inference_id=inference_id)
                print(f"Inference '{inference_id}' already exists:")
                print(existing_inference)
                return True
            except NotFoundError:
                # Inference doesn't exist, proceed with creation
                pass

            resp = client.inference.put(
                task_type="completion",
                inference_id=inference_id,
                inference_config={
                    "service": "openai",
                    "service_settings": {
                        "api_key": os.getenv("OPENAI_API_KEY"),
                        "model_id": "gpt-3.5-turbo"  # Changed from 'model' to 'model_id'
                    }
                }
            )
            if resp:
                print("Inference creation response:")
                print(resp)
                return True
            else:
                print("No response received from the inference creation request.")
                return False
        except ConnectionTimeout:
            if attempt < max_retries - 1:
                print(f"Connection timed out. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("Max retries reached. Unable to create inference due to connection timeout.")
                return False
        except ApiError as e:
            print(f"Error creating inference: {e}")
            if "Model IDs must be unique" in str(e):
                new_id = f"{inference_id}_{int(time.time())}"
                print(f"Attempting to create inference with a new ID: {new_id}")
                return create_or_get_inference(client, new_id)
            return False

def main():
    api_key = os.getenv("ELASTIC_API_KEY")
    if not api_key:
        print("Error: ELASTIC_API_KEY environment variable is not set.")
        return

    client = Elasticsearch(
        "https://my-elastic-project-a943bc.es.us-east-1.aws.elastic.cloud:443",
        api_key=api_key
    )

    inference_id = "openai_chat_completions"
    if create_or_get_inference(client, inference_id):
        # Use the created inference
        try:
            resp = client.inference.inference(
                task_type="completion",
                inference_id=inference_id,
                input="What is Elastic?",
            )
            print("Inference response:")
            print(resp)
        except ApiError as e:
            print(f"Error during inference: {e}")
    else:
        print("Failed to create or get inference. Skipping inference request.")

if __name__ == "__main__":
    main()