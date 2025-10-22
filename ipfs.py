import requests
import json

# Use local IPFS node (default port for Kubo)
IPFS_API_URL = "https://ip4/127.0.0.1/tcp/5001"

def pin_to_ipfs(data):
    assert isinstance(data, dict), f"Error pin_to_ipfs expects a dictionary"

    # Convert dictionary to JSON string
    json_data = json.dumps(data)

    # Send to IPFS local API
    files = {'file': ('data.json', json_data)}
    response = requests.post(f"{IPFS_API_URL}/api/v0/add", files=files)

    if response.status_code != 200:
        raise Exception(f"Error uploading to IPFS: {response.text}")

    cid = response.json()["Hash"]
    return cid



def get_from_ipfs(cid, content_type="json"):
    assert isinstance(cid, str), f"get_from_ipfs accepts a cid in the form of a string"

    # Retrieve from public gateway (works for any CID)
    response = requests.get(f"https://ipfs.io/ipfs/{cid}")

    if response.status_code != 200:
        raise Exception(f"Error retrieving from IPFS: {response.text}")

    data = response.json()
    assert isinstance(data, dict), f"get_from_ipfs should return a dict"
    return data
