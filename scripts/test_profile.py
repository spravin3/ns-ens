import os
import requests
from web3 import Web3
from datetime import datetime, timedelta


ETHERSCAN_API_KEY = os.getenv('ETHERSCAN_API_KEY')
ETH_RPC_URL = os.getenv('ETH_RPC_URL')
SIM_API_KEY = os.getenv('SIM_API_KEY')

ENS_NAME = input('Enter ENS name (e.g. vitalik.eth): ').strip()

# Step 1: Resolve ENS name to address
w3 = Web3(Web3.HTTPProvider(ETH_RPC_URL))
address = w3.ens.address(ENS_NAME)
if not address:
    print(f"ENS name not found: {ENS_NAME}")
    exit(1)
print(f"ENS Name: {ENS_NAME}")
print(f"Address: {address}")

# Step 2: ENS text records (avatar, display name, bio, socials)
profile = {}
try:
    resolver = w3.ens.resolver(ENS_NAME)
    if resolver:
        for key in [
            'avatar', 'display', 'description', 'email', 'url', 'twitter', 'github', 'discord', 'telegram', 'reddit',
            'eth', 'btc', 'ltc', 'doge', 'contenthash'
        ]:
            value = resolver.get_text(key)
            if value:
                profile[key] = value
except Exception:
    pass

# Print core profile
for key, label in [
    ('avatar', 'Avatar'),
    ('display', 'Display Name'),
    ('description', 'Bio/Description'),
    ('url', 'Website'),
    ('email', 'Email'),
    ('twitter', 'Twitter'),
    ('github', 'GitHub'),
    ('discord', 'Discord'),
    ('telegram', 'Telegram'),
    ('reddit', 'Reddit')
]:
    if profile.get(key):
        print(f"{label}: {profile[key]}")

# Step 3: ETH Balance
bal_url = (
    f"https://api.etherscan.io/v2/api"
    f"?chainid=1"
    f"&module=account"
    f"&action=balance"
    f"&address={address}"
    f"&tag=latest"
    f"&apikey={ETHERSCAN_API_KEY}"
)
bal_res = requests.get(bal_url)
bal_data = bal_res.json()
balance_wei = int(bal_data.get('result', '0'))
balance_eth = balance_wei / 1e18
print(f"ETH Balance: {balance_eth:.6f} ETH")

# Step 4: Last 10 internal transactions (Etherscan V2)
tx_url = (
    f"https://api.etherscan.io/v2/api"
    f"?chainid=1"
    f"&module=account"
    f"&action=txlistinternal"
    f"&address={address}"
    f"&startblock=0"
    f"&endblock=99999999"
    f"&page=1"
    f"&offset=10"
    f"&sort=desc"
    f"&apikey={ETHERSCAN_API_KEY}"
)
tx_res = requests.get(tx_url)
tx_data = tx_res.json()
txs = tx_data.get('result', [])
if isinstance(txs, list) and txs:
    print(f"Last 10 Internal Transactions:")
    for tx in txs:
        print(f"  Hash: {tx.get('hash', '')} | From: {tx.get('from', '')} | To: {tx.get('to', '')} | Value: {int(tx.get('value', '0'))/1e18:.4f} ETH | Time: {tx.get('timeStamp', '')}")


# Step 5: Aggregate transaction count and token balances from SIM API
if SIM_API_KEY:
    # Removed aggregate transaction count and account age metrics from SIM API

    # All token balances (balances endpoint)
    sim_bal_url = f"https://api.sim.dev.dune.com/v1/evm/balances/{address}?chain_ids=1&exclude_spam_tokens=true"
    try:
        sim_bal_res = requests.get(sim_bal_url, headers=sim_headers)
        sim_bal_data = sim_bal_res.json()
        balances = sim_bal_data.get('balances', [])
        if balances:
            print("\nToken Holdings (SIM API):")
            for bal in balances:
                symbol = bal.get('symbol', '')
                name = bal.get('name', '')
                amount = int(bal.get('amount', '0')) / (10 ** int(bal.get('decimals', 0))) if bal.get('decimals') else float(bal.get('amount', '0'))
                usd = bal.get('value_usd', None)
                price = bal.get('price_usd', None)
                print(f"  {symbol} ({name}): {amount:.4f}", end='')
                if usd:
                    print(f" | USD Value: ${usd:,.2f}", end='')
                if price:
                    print(f" | Price: ${price:,.2f}", end='')
                print("")
    except Exception as e:
        print(f"SIM API balances error: {e}")
