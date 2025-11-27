import os
import requests
from web3 import Web3

# ENV VARS
ETHERSCAN_API_KEY = os.getenv('ETHERSCAN_API_KEY')
ETH_RPC_URL = os.getenv('ETH_RPC_URL')
COINMARKETCAP_API_KEY = os.getenv('COINMARKETCAP_API_KEY')

# INPUT: ENS name
ENS_NAME = input('Enter ENS name (e.g. vitalik.eth): ').strip()

# Step 1: Resolve ENS name to address using Web3
w3 = Web3(Web3.HTTPProvider(ETH_RPC_URL))
address = w3.ens.address(ENS_NAME)
if not address:
    print(f"ENS name not found: {ENS_NAME}")
    exit(1)
print(f"Resolved ENS: {ENS_NAME} -> {address}")

# Step 2: Use test_address.py logic to fetch profile
from test_address import fetch_etherscan_data, fetch_eth_price, fetch_sim_data

print(f"--- Etherscan Data for {address} ---")
ethscan = fetch_etherscan_data(address)
print(f"Nametag: {ethscan['nametag']}")
print(f"ETH Balance: {ethscan['balance_eth']} ETH")
eth_price = fetch_eth_price()
print(f"ETH Value: ${ethscan['balance_eth'] * eth_price:,.2f} (@ ${eth_price:,.2f}/ETH)")
print(f"--- Sim Data for {address} ---")
simdata = fetch_sim_data(address)
print(simdata)
