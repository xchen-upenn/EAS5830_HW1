import eth_account
from eth_account import Account
from eth_account.messages import encode_defunct
import random
import string
import json
from pathlib import Path
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware  # Necessary for POA chains


def merkle_assignment():
    """
    The only modifications you need to make to this method are to assign
    your "random_leaf_index" and uncomment the last line when you are
    ready to attempt to claim a prime. You will need to complete the
    methods called by this method to generate the proof.
    """
    # Generate the list of primes as integers
    num_of_primes = 8192
    primes = generate_primes(num_of_primes)

    # Convert the list of primes to bytes32 format
    leaves = convert_leaves(primes)

    # Build a Merkle tree using the leaves
    tree = build_merkle(leaves)

    # Select a random leaf index (0 is already claimed)
    random_leaf_index = random.randint(1, num_of_primes - 1)
    proof = prove_merkle(tree, random_leaf_index)

    # Generate a challenge string for signing
    challenge = ''.join(random.choice(string.ascii_letters) for _ in range(32))
    addr, sig = sign_challenge(challenge)

    if sign_challenge_verify(challenge, addr, sig):
        # Send signed transaction to claim the prime
        tx_hash = send_signed_msg(proof, leaves[random_leaf_index])
        print("Transaction hash:", tx_hash)


def generate_primes(num_primes):
    """
    Generate the first 'num_primes' prime numbers.
    Returns a list of primes (ints) in ascending order.
    """
    primes_list = []
    num = 2

    while len(primes_list) < num_primes:
        is_prime = True
        for p in primes_list:
            if p * p > num:
                break
            if num % p == 0:
                is_prime = False
                break
        if is_prime:
            primes_list.append(num)
        num += 1

    return primes_list


def convert_leaves(primes_list):
    """
    Convert the list of primes to bytes32 format.
    Returns a list of bytes32-encoded primes.
    """
    leaves_bytes = []
    for p in primes_list:
        b = p.to_bytes(32, byteorder='big')
        leaves_bytes.append(b)
    return leaves_bytes


def build_merkle(leaves):
    """
    Build a Merkle Tree from the list of bytes32 leaves.
    Returns a list of levels, from leaves up to the root.
    """
    tree = [leaves]
    current = leaves

    while len(current) > 1:
        next_level = []
        for i in range(0, len(current), 2):
            left = current[i]
            right = current[i + 1] if i + 1 < len(current) else left
            parent = hash_pair(left, right)
            next_level.append(parent)
        tree.append(next_level)
        current = next_level

    return tree


def prove_merkle(merkle_tree, leaf_index):
    """
    Create a Merkle proof of inclusion for the leaf at 'leaf_index'.
    Returns a list of sibling hashes from leaf to root.
    """
    proof = []
    idx = leaf_index

    for level in range(len(merkle_tree) - 1):
        layer = merkle_tree[level]
        sibling_index = idx ^ 1  # flip last bit to get sibling
        if sibling_index < len(layer):
            proof.append(layer[sibling_index])
        else:
            proof.append(layer[idx])  # duplicate if no sibling
        idx //= 2

    return proof


def sign_challenge(challenge):
    """
    Sign a challenge string with the account's private key.
    Returns the address and the signature in hex.
    """
    acct = get_account()
    addr = acct.address
    eth_sk = acct.key

    msg = encode_defunct(text=challenge)
    eth_sig_obj = eth_account.Account.sign_message(msg, private_key=eth_sk)

    return addr, eth_sig_obj.signature.hex()


def send_signed_msg(proof, random_leaf):
    """
    Build, sign, and send a transaction claiming a leaf on the contract.
    """
    chain = 'bsc'
    acct = get_account()
    address, abi = get_contract_info(chain)
    w3 = connect_to(chain)

    contract = w3.eth.contract(address=w3.to_checksum_address(address), abi=abi)

    tx = contract.functions.submit(proof, random_leaf).build_transaction({
    'from': acct.address,
    'nonce': w3.eth.get_transaction_count(acct.address),
    'gas': 300000,
    'gasPrice': w3.to_wei('10', 'gwei'),
    'chainId': 97  # BSC testnet
    })

    signed_tx = w3.eth.account.sign_transaction(tx, private_key=acct.key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

    # Wait for the transaction to be mined
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    
    return w3.to_hex(tx_hash)    


# -------------------- Helper functions -------------------- #

def connect_to(chain):
    """
    Connect to a blockchain node ('avax' or 'bsc') and return a Web3 instance.
    """
    if chain not in ['avax', 'bsc']:
        print(f"{chain} is not a valid option for 'connect_to()'")
        return None

    api_url = (
        "https://api.avax-test.network/ext/bc/C/rpc"
        if chain == "avax"
        else "https://data-seed-prebsc-1-s1.binance.org:8545/"
    )

    w3 = Web3(Web3.HTTPProvider(api_url))
    w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
    return w3


def get_account():
    """
    Returns an account object recovered from the secret key in 'sk.txt'.
    """
    cur_dir = Path(__file__).parent.absolute()
    with open(cur_dir.joinpath("sk.txt"), "r") as f:
        sk = f.readline().strip()
    if sk.startswith("0x"):
        sk = sk[2:]
    return eth_account.Account.from_key(sk)


def get_contract_info(chain):
    """
    Return contract address and ABI from 'contract_info.json' for the given chain.
    """
    contract_file = Path(__file__).parent.absolute() / "contract_info.json"
    if not contract_file.is_file():
        contract_file = Path(__file__).parent.parent.parent / "tests" / "contract_info.json"

    with open(contract_file, "r") as f:
        d = json.load(f)[chain]

    return d["address"], d["abi"]


def sign_challenge_verify(challenge, addr, sig):
    """
    Verify a signature for a challenge string.
    """
    eth_encoded_msg = encode_defunct(text=challenge)
    recovered = eth_account.Account.recover_message(eth_encoded_msg, signature=sig)

    if recovered == addr:
        print(f"Success: signed the challenge {challenge} using address {addr}!")
        return True
    else:
        print(f"Failure: The signature does not verify!")
        print(f"signature = {sig}\naddress = {addr}\nchallenge = {challenge}")
        return False


def hash_pair(a, b):
    """
    Sorts two leaves and hashes them using solidity_keccak to match OpenZeppelin Merkle validation.
    """
    if a < b:
        return Web3.solidity_keccak(["bytes32", "bytes32"], [a, b])
    else:
        return Web3.solidity_keccak(["bytes32", "bytes32"], [b, a])


if __name__ == "__main__":
    merkle_assignment()
