# Elasticsearch Inference Creation Tool

This project provides a Python script for creating and managing sparse embedding inferences in Elasticsearch.

## Description

The `create_inference.py` script connects to an Elasticsearch cluster and creates or retrieves an existing inference for sparse embedding tasks. It's designed to work with the ELSER (Elasticsearch Learned Sparse EncodeR) service.

## Features

- Connects to Elasticsearch using an API key
- Creates a new inference or retrieves an existing one
- Handles connection timeouts with retries
- Manages unique inference IDs

## Prerequisites

- Python 3.x
- Elasticsearch Python client
- Access to an Elasticsearch cluster
- API key for authentication

## Installation

1. Clone this repository:
   ```
   git clone <repository-url>
   ```
2. Install the required packages:
3. Create a `.env` file in the project root and add your Elasticsearch API key:
ELASTIC_API_KEY=your_api_key_here
## Usage

Run the script using Python:

The script will attempt to create a new inference with the ID "elser_embeddings" or retrieve an existing one with the same ID.

## Configuration

- The Elasticsearch cluster URL is hardcoded in the script. Update it if necessary.
- The inference ID is set to "elser_embeddings" by default. You can modify this in the `main()` function.
- The script uses environment variables for the API key. Ensure your `.env` file is properly set up.

## Error Handling

The script includes error handling for:
- Connection timeouts (with retries)
- API errors
- Duplicate inference IDs

## Contributing

Contributions to improve the script or extend its functionality are welcome. Please feel free to submit pull requests or open issues for any bugs or feature requests.


## Contact

Shirly Manor - shirly.manor@gmail.com
