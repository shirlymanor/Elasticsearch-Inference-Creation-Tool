import streamlit as st
from elasticsearch import Elasticsearch
import os
from dotenv import load_dotenv
from usage_examples import semantic_search
import json

# Load environment variables
load_dotenv()

# Initialize Elasticsearch client
client = Elasticsearch(
    "https://my-elastic-project-a943bc.es.us-east-1.aws.elastic.cloud:443",
    api_key=os.getenv('ELASTIC_API_KEY')
)

# Define the index name
index_name = "elser_test_index"

st.title("Semantic Search App")


# Create a text input for the search query
search_query = st.text_input("Enter your search query:")

if st.button("Search"):
    if search_query:
        try:
            results = semantic_search(client, index_name, search_query)
            
            st.subheader("Search Results:")
            if results['hits']['total']['value'] > 0:
                for hit in results['hits']['hits']:
                    st.write(f"Title: {hit['_source'].get('title', 'No title')}")
                    
                    # Safely get content
                    content = hit['_source'].get('content', 'No content available')
                    
                    # Highlight relevant terms if available
                    highlighted_content = hit.get('highlight', {}).get('content', [content])[0]
                    st.markdown(f"Content: {highlighted_content}", unsafe_allow_html=True)
                    
                    st.write(f"Score: {hit['_score']}")
                    
                    # Display relevance explanation if available
                    if 'explanation' in hit:
                        with st.expander("Why is this relevant?"):
                            st.json(hit['explanation'])
                    else:
                        st.write("(No relevance explanation available)")
                    
                    # Debug: Print all keys in the hit
                    #st.write("Debug - Hit keys:", list(hit.keys()))
                    
                    st.write("---")
            else:
                st.write("No results found.")
            
            # Print raw results for debugging
            st.subheader("Raw Results:")
            st.code(json.dumps(results, indent=2, default=str))
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.error("Full error details:")
            st.exception(e)
    else:
        st.warning("Please enter a search query.")