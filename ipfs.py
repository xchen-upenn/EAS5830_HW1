import requests
import json

# Base URL of the IPFS API (change if you're using your own IPFS node)
IPFS_API_URL = "http://127.0.0.1:5001"  # or e.g. "https://ipfs.infura.io:5001"

def pin_to_ipfs(data):
    assert isinstance(data, dict), f"Error pin_to_ipfs expects a dictionary"

    # Convert dict to JSON string
    json_data = json.dumps(data)

    # Upload (add) the JSON to IPFS
    files = {
        'file': ('data.json', json_data)
    }
    response = requests.post(f"{IPFS_API_URL}/api/v0/add", files=files)

    if response.status_code != 200:
        raise Exception(f"Error uploading to IPFS: {response.text}")

    # Parse CID from response
    cid = response.json()["Hash"]

    return cid


def get_from_ipfs(cid, content_type="json"):
    assert isinstance(cid, str), f"get_from_ipfs accepts a cid in the form of a string"

    # Retrieve the content from IPFS
    response = requests.get(f"{IPFS_API_URL}/ipfs/{cid}")

    if response.status_code != 200:
        raise Exception(f"Error retrieving from IPFS: {response.text}")

    # Parse JSON content
    data = response.json()

    assert isinstance(data, dict), f"get_from_ipfs should return a dict"

    return data
