from elasticsearch import Elasticsearch, ApiError, NotFoundError, RequestError
import os

def main():
    # Connect to Elasticsearch
    es = Elasticsearch(
        hosts=["http://localhost:9200"],  # Update with your host if different
        basic_auth=(os.getenv('ES_USER') ,os.getenv('ES_PASSWORD')),  # Replace with your credentials
        verify_certs=False
    )

    # Check if the cluster is running and get version info
    try:
        info = es.info()
        print("Connected to Elasticsearch cluster:", info['cluster_name'])
        print("Elasticsearch version:", info['version']['number'])
    except ApiError as e:
        print(f"Error connecting to Elasticsearch: {e}")
        return

    # Check available features
    try:
        features = es.xpack.info()
        print("\nAvailable features:")
        for feature, details in features['features'].items():
            print(f"{feature}: {'enabled' if details['enabled'] else 'disabled'}")
    except ApiError as e:
        print(f"Error retrieving feature info: {e}")

    # List indices
    try:
        indices = es.cat.indices(format="json")
        print("\nAvailable indices:")
        for index in indices:
            print(f"Index: {index['index']}, Docs count: {index['docs.count']}")
    except ApiError as e:
        print(f"Error listing indices: {e}")

    # Input text for NLP tasks
    text = "Elasticsearch is a distributed, RESTful search and analytics engine capable of addressing a growing number of use cases."

    try:
        index_name = "test_index"
        es.indices.create(index=index_name, ignore=400)
        doc = {"title": "Test Document", "content": "This is a test document."}
        es.index(index=index_name, body=doc)
        print(f"\nCreated test index '{index_name}' and added a document.")
    except ApiError as e:
        print(f"Error creating test index: {e}")

    # Search the test index
    try:
        result = es.search(index=index_name, body={"query": {"match_all": {}}})
        print(f"\nSearch result from '{index_name}':")
        for hit in result['hits']['hits']:
            print(hit['_source'])
    except ApiError as e:
        print(f"Error searching test index: {e}")

if __name__ == "__main__":
    main()