from elasticsearch import Elasticsearch
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    # Initialize Elasticsearch client
    client = Elasticsearch(
        "https://my-elastic-project-a943bc.es.us-east-1.aws.elastic.cloud:443",
        api_key=os.getenv('ELASTIC_API_KEY')
    )

    # Define the index name
    index_name = "elser_test_index"

    # Create the index with appropriate mappings
    create_index(client, index_name)

    # Index some sample documents
    index_documents(client, index_name)

    # Print all documents in the index
    print("\nAll documents in the index:")
    all_docs = client.search(index=index_name, body={"query": {"match_all": {}}})
    for hit in all_docs['hits']['hits']:
        print(f"ID: {hit['_id']}")
        print(f"Title: {hit['_source']['title']}")
        print(f"Content: {hit['_source']['content']}")
        print("---")

    # Perform a semantic search
    search_query = "What are the benefits of exercise?"
    search_results = semantic_search(client, index_name, search_query)

    # Print the search results
    print(f"\nSearch Query: {search_query}")
    print("Search Results:")
    print(f"Total hits: {search_results['hits']['total']['value']}")
    if search_results['hits']['total']['value'] > 0:
        for hit in search_results['hits']['hits']:
            print(f"Score: {hit['_score']}")
            print(f"Title: {hit['_source']['title']}")
            print(f"Content: {hit['_source']['content']}")
            print("---")
    else:
        print("No results found.")

    # Print the full response for debugging
    print("\nFull response:")
    print(search_results)

    # Print index mapping
    print("\nIndex mapping:")
    mapping = client.indices.get_mapping(index=index_name)
    print(mapping)

    # Print a sample document
    print("\nSample document:")
    sample_doc = client.get(index=index_name, id=1)
    print(sample_doc)

def create_index(client, index_name):
    index_body = {
        "mappings": {
            "properties": {
                "title": {"type": "text"},
                "content": {"type": "text"},
                "content_vector": {"type": "sparse_vector"}
            }
        }
    }
    client.options(ignore_status=[400, 404]).indices.delete(index=index_name)
    client.indices.create(index=index_name, body=index_body)
    print(f"Index '{index_name}' created.")

def index_documents(client, index_name):
    documents = [
        {
            "title": "Benefits of Exercise",
            "content": "Regular exercise improves cardiovascular health, strengthens muscles, and boosts mental well-beingHelp you get to and stay at a healthy weight. Along with diet, exercise plays an important role in maintaining a healthy weight and preventing obesity. If you are at a healthy weight, you can maintain it if the calories you eat and drink are equal to the amount of energy you burn. To lose weight, you need to use more calories than you eat and drink Help your body manage blood glucose (blood sugar) and insulin levels. Exercise can lower your blood glucose levels and help your insulin work better. This can reduce your risk of metabolic syndrome and type 2 diabetes. And if you already have one of these diseases, exercise can help you to manage it"
        },
        {
            "title": "Healthy Eating Habits",
            "content": "A balanced diet rich in fruits, vegetables, and whole grains provides essential nutrients for optimal health."
        },
        {
            "title": "Importance of Sleep",
            "content": "Adequate sleep is crucial for physical recovery, cognitive function, and overall health maintenance."
        }
    ]

    for i, doc in enumerate(documents, start=1):
        # Generate ELSER embedding for the content
        embedding = client.ml.infer_trained_model(
            model_id=".elser_model_2",
            docs=[{"text_field": doc["content"]}]
        )
        
        # Add the embedding to the document
        doc["content_vector"] = embedding["inference_results"][0]["predicted_value"]

        # Index the document with a unique ID
        response = client.index(index=index_name, id=str(i), document=doc)
        print(f"Document {i} indexed: {response['result']}")
    
    # Refresh the index to make the documents searchable immediately
    client.indices.refresh(index=index_name)
    print(f"{len(documents)} documents indexed and refreshed.")

def semantic_search(client, index_name, query):
    search_body = {
        "query": {
            "text_expansion": {
                "content_vector": {
                    "model_id": ".elser_model_2",
                    "model_text": query
                }
            }
        },
        "highlight": {
            "fields": {
                "content": {}
            }
        },
        "explain": True
    }
    
    return client.search(index=index_name, body=search_body)

if __name__ == "__main__":
    main()