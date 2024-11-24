from elasticsearch import Elasticsearch
from elasticsearch import helpers, ApiError, NotFoundError, RequestError
from dotenv import load_dotenv
import os

  # Add this at the beginning of your script
def create_index(client):
    try:
        resp = client.indices.put_index_template(
            name="template_1",
            index_patterns=["template*"],
            priority=1,
            template={
                "settings": {
                    "number_of_shards": 2
                }
            },
        )
        print("Index template created:", resp)
    except ApiError as e:
        print(f"Error creating index template: {e}")
def main():
    load_dotenv()
    
    # Create Elasticsearch client
    client = Elasticsearch(
        "https://my-elastic-project-a943bc.es.us-east-1.aws.elastic.cloud:443",
        api_key=os.getenv('ELASTIC_API_KEY')
    )
    index_name = "search-rp3o"


    # Check connection and print cluster info
    try:
        info = client.info()
        print(f"Connected to Elasticsearch cluster: {info['cluster_name']}")
        print(f"Elasticsearch version: {info['version']['number']}")
    except ApiError as e:
        print(f"Error connecting to Elasticsearch: {e}")
        return

    # Create index
    create_index(client)

    # Add vector to index
    add_vector_to_index(client, index_name)

    # Use the ELSER model for text embedding
    text = "Elasticsearch is a powerful search and analytics engine."
    embedding_model_id = '.elser_model_2'
    try:
        embedding_result = client.ml.infer_trained_model(
            model_id=embedding_model_id,
            docs=[{'text_field': text}]
        )
        print("\nText Embedding Result:")
        print(embedding_result)
    except ApiError as e:
        print(f"Error during text embedding inference: {e}")


def add_vector_to_index(client, index_name):
    docs = [
        {
            "text": "Example text 1",
            "vector": [5.479, 9.789, 2.606]
        },
        {
            "text": "Example text 2",
            "vector": [7.475, 9.63, 8.804]
        },
        {
            "text": "Example text 3",
            "vector": [5.535, 6.532, 6.407]
        }
    ]

    try:
        bulk_response = helpers.bulk(client, docs, index=index_name)
        print("Bulk insert response:", bulk_response)
    except ApiError as e:
        print(f"Error adding vectors to index: {e}")
   
if __name__ == "__main__":
    main()
