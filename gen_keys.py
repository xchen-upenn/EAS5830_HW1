from web3 import Web3
from eth_account.messages import encode_defunct
import eth_account
import os

from eth_account import Account

# Create a new account - see student account request project

key = '0x0be68e35e911c47d0c43d96c49bb7a5a84a8ef114653f301d49748a59517de0e'
address = '0xE75Ea03674Fe735e8312fBA7849b61d3cF1D2Bf2'

# Save the private key in a file for your assignment
with open("secret_key.txt", "w") as f:
    f.write(acct.key.hex())



def sign_message(challenge, filename="secret_key.txt"):
    """
    challenge - byte string
    filename - filename of the file that contains your account secret key
    To pass the tests, your signature must verify, and the account you use
    must have testnet funds on both the bsc and avalanche test networks.
    """
    # This code will read your "sk.txt" file
    # If the file is empty, it will raise an exception
    with open(filename, "r") as f:
        key = f.readlines()
    assert(len(key) > 0), "Your account secret_key.txt is empty"

    w3 = Web3()
    message = encode_defunct(challenge)

    # TODO recover your account information for your private key and sign the given challenge
    # Use the code from the signatures assignment to sign the given challenge
    
    # Recover your account using the private key
    account = eth_account.Account.from_key(key)
    eth_addr = account.address

    # Sign the given challenge
    signed_message = account.sign_message(message)

    assert eth_account.Account.recover_message(message,signature=signed_message.signature.hex()) == eth_addr, f"Failed to sign message properly"

    #return signed_message, account associated with the private key
    return signed_message, eth_addr


if __name__ == "__main__":
    for i in range(4):
        challenge = os.urandom(64)
        sig, addr= sign_message(challenge=challenge)
        print( addr )
