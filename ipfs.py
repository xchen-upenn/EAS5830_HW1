import requests
import json

PINATA_JWT = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySW5mb3JtYXRpb24iOnsiaWQiOiIzMWQyMzNiMi0wNmJlLTRiNmUtYjE3Mi0yZTg1N2Y5ZDA2OGMiLCJlbWFpbCI6InhjaGVuLnJ1Y0BnbWFpbC5jb20iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwicGluX3BvbGljeSI6eyJyZWdpb25zIjpbeyJkZXNpcmVkUmVwbGljYXRpb25Db3VudCI6MSwiaWQiOiJGUkExIn0seyJkZXNpcmVkUmVwbGljYXRpb25Db3VudCI6MSwiaWQiOiJOWUMxIn1dLCJ2ZXJzaW9uIjoxfSwibWZhX2VuYWJsZWQiOmZhbHNlLCJzdGF0dXMiOiJBQ1RJVkUifSwiYXV0aGVudGljYXRpb25UeXBlIjoic2NvcGVkS2V5Iiwic2NvcGVkS2V5S2V5IjoiNDcxZGFlNzRkYzM1YjkyNWFjYzUiLCJzY29wZWRLZXlTZWNyZXQiOiJiYmI1OTIyZTcwODk3M2NlNzkwMTY3MTYzY2U5ZWVmMGYxNTVlZTVmOTczNDU5MWZkYzA2NzYzZTI3ODk4ZmU3IiwiZXhwIjoxNzkyNzA3ODI4fQ.Y8dzaifOkrVlPZfDoyiAg2rmM5t_0z8Hw_3PApYBCB8"
# Pinata API base URL
PINATA_BASE_URL = "https://api.pinata.cloud"

def pin_to_ipfs(data):
    assert isinstance(data, dict), f"Error pin_to_ipfs expects a dictionary"

    # Convert dictionary to JSON string
    json_data = json.dumps(data)

    # Pinata JSON upload endpoint
    url = f"{PINATA_BASE_URL}/pinning/pinJSONToIPFS"

    headers = {
        "Authorization": f"Bearer {PINATA_JWT}",
        "Content-Type": "application/json"
    }

    # Send request
    response = requests.post(url, headers=headers, data=json_data)

    if response.status_code != 200:
        raise Exception(f"Error uploading to IPFS: {response.text}")

    # Extract the IPFS CID
    cid = response.json()["IpfsHash"]
    return cid




def get_from_ipfs(cid, content_type="json"):
    assert isinstance(cid, str), f"get_from_ipfs accepts a cid in the form of a string"

    # Retrieve from public gateway (works for any CID)
    response = requests.get(f"https://gateway.pinata.cloud/ipfs/{cid}")

    if response.status_code != 200:
        raise Exception(f"Error retrieving from IPFS: {response.text}")

    data = response.json()
    assert isinstance(data, dict), f"get_from_ipfs should return a dict"
    return data
