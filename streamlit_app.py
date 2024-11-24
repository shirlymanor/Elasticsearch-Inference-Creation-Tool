import streamlit as st
from elasticsearch import Elasticsearch, ApiError, ConnectionTimeout, NotFoundError
import os
import time
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
                        "model_id": "gpt-3.5-turbo"
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

def use_openai_inference(client, inference_id, input_text):
    try:
        resp = client.inference.inference(
            task_type="completion",
            inference_id=inference_id,
            input=input_text,
        )
        # Print the full response for debugging
        print("Full response:", resp)
        
        # Check if 'completion' is directly in the response
        if 'completion' in resp:
            return resp['completion']
        # Check if 'inference_results' is in the response
        elif 'inference_results' in resp and len(resp['inference_results']) > 0:
            return resp['inference_results'][0].get('completion', 'No completion found')
        else:
            return "Unable to extract completion from response"
    except ApiError as e:
        st.error(f"Error during inference: {e}")
        return None

st.set_page_config(layout="wide")

st.title("Semantic Search and OpenAI Inference App")

# Create two columns
col1, col2 = st.columns(2)

with col1:
    st.header("Semantic Search")
    search_query = st.text_input("Enter your search query:")
    if st.button("Run Semantic Search", key="semantic_search_button"):
        if search_query:
            try:
                results = semantic_search(client, index_name, search_query)
                st.subheader("Search Results:")
                if results['hits']['total']['value'] > 0:
                    for hit in results['hits']['hits']:
                        with st.expander(f"Title: {hit['_source'].get('title', 'No title')}"):
                            content = hit['_source'].get('content', 'No content available')
                            highlighted_content = hit.get('highlight', {}).get('content', [content])[0]
                            st.markdown(f"Content: {highlighted_content}", unsafe_allow_html=True)
                            st.write(f"Score: {hit['_score']}")
                            if 'explanation' in hit:
                                with st.expander("Why is this relevant?"):
                                    st.json(hit['explanation'])
                            else:
                                st.write("(No relevance explanation available)")
                else:
                    st.write("No results found.")
                
                with st.expander("Raw Results"):
                    st.code(json.dumps(results, indent=2, default=str))
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.exception(e)
        else:
            st.warning("Please enter a search query.")

with col2:
    st.header("OpenAI Inference")
    inference_id = "openai_chat_completions"
    if create_or_get_inference(client, inference_id):
        input_text = st.text_area("Enter text for OpenAI inference:", height=150)
        if st.button("Run OpenAI Inference", key="openai_inference_button"):
            with st.spinner("Running inference..."):
                result = use_openai_inference(client, inference_id, input_text)
                if result:
                    st.success("Inference Result:")
                    st.markdown(f"""
                    <div style="border:1px solid #28a745; border-radius:5px; padding:10px; background-color:#f8f9fa;">
                        {result[0].get('result', 'No content available')}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error("Failed to get inference result")
    else:
        st.error("Failed to create or get inference.")

# Add some custom CSS to make it look nicer
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
    }
    .stTextInput>div>div>input {
        background-color: #f0f2f6;
    }
</style>
""", unsafe_allow_html=True)