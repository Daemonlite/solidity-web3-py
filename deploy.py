from solcx import compile_standard, install_solc
import json
from web3 import Web3
from decouple import config

# Install solc 0.6.0 if not already installed
install_solc("0.6.0")

# Read Solidity file
with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()

# Compile Solidity
compiled_solidity = compile_standard(
    {
        "language": "Solidity",
        "sources": {
            "SimpleStorage.sol": {
                "content": simple_storage_file
            }
        },
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]
                }
            }
        }
    },
    solc_version="0.6.0"
)

with open("compiled_code.json", "w") as file:
    json.dump(compiled_solidity, file)

# get bytecode
bytecode = compiled_solidity["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"]["bytecode"]["object"]

# get abi
abi = compiled_solidity["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]


# connecting to ganache
w3 = Web3(Web3.HTTPProvider("https://sepolia.infura.io/v3/d58e86edcd6a489cb03bfac69ad01ef0"))
chain_id = 11155111
my_address = "0x348a2C58d500E4912d3D4fc414eCdfa045103f8d"
private_key = config("PRIVATE_KEY")

# create the contract in python
SimpleStrage = w3.eth.contract(abi=abi, bytecode=bytecode)

# get the latest transaction

nonce = w3.eth.get_transaction_count(my_address)
# print(nonce)

"""
1. Build a transaction
2. Sign a transaction
3. Send a transaction
"""
print("deploying contract...")

transaction = SimpleStrage.constructor().build_transaction({
    "chainId": chain_id,
    "from": my_address,
    "nonce": nonce,
})

# print(transaction)

signed_txn = w3.eth.account.sign_transaction(transaction,private_key=private_key)

# print(signed_txn)

# send the signed transaction

txn_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
txn_receipt = w3.eth.wait_for_transaction_receipt(txn_hash)

print("deployed!")

"""
when working with the contract you will need
1. contract address
2. contract abi (application binary interface)
"""

simple_storage = w3.eth.contract(address=txn_receipt.contractAddress, abi=abi)

"""
Calls -> simulate making a call and getting a return value
Transact -> actually make a state change
"""

print(simple_storage.functions.retrieve().call())

# creating an actual transaction
print("updating contract...")

store_transaction = simple_storage.functions.store(15).build_transaction({
    "chainId": chain_id,
    "from": my_address,
    "nonce": nonce + 1,
})

signed_store_transaction = w3.eth.account.sign_transaction(store_transaction, private_key=private_key)
send_store_tx = w3.eth.send_raw_transaction(signed_store_transaction.raw_transaction)

tx_receipt = w3.eth.wait_for_transaction_receipt(send_store_tx)
print("updated!")
print(simple_storage.functions.retrieve().call())