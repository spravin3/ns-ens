import os
import requests

SIM_API_KEY = os.getenv('SIM_API_KEY')
SIM_API_URL = 'https://api.sim.dune.com/v1/evm'
CLOUDFLARE_ENS_URL = 'https://cloudflare-eth.com'

ENS_NAME = 'vitalik.eth'

def resolve_ens_name(ens_name):
    ETHERSCAN_API_KEY = os.getenv('ETHERSCAN_API_KEY')
    url = f"https://api.etherscan.io/v2/resolve-ens?name={ens_name}&apikey={ETHERSCAN_API_KEY}"
    res = requests.get(url)
    res.raise_for_status()
    data = res.json()
    address = data.get('data', {}).get('address')
    if not address or address == "0x0000000000000000000000000000000000000000":
        raise Exception("ENS name not found")
    return address

def fetch_ens_records(ens_name):
    url = f"{CLOUDFLARE_ENS_URL}/resolve-text/{ens_name}"
    res = requests.get(url)
    if not res.ok:
        return {}
    data = res.json()
    return data.get('records', {})

def fetch_sim_data(address):
    headers = {'X-Sim-Api-Key': SIM_API_KEY} if SIM_API_KEY else {}
    sim_data = {}
    # ETH balance
    bal_url = f"{SIM_API_URL}/balances?chain_ids=1&addresses={address}"
    bal_res = requests.get(bal_url, headers=headers)
    if bal_res.ok:
        bal_json = bal_res.json()
        sim_data['balance'] = bal_json.get('balances', {}).get(address, {}).get('native', {}).get('balance')
    # Transaction count
    tx_url = f"{SIM_API_URL}/transactions?chain_ids=1&addresses={address}&limit=1"
    tx_res = requests.get(tx_url, headers=headers)
    if tx_res.ok:
        tx_json = tx_res.json()
        sim_data['txCount'] = tx_json.get('transactions', {}).get(address, {}).get('count')
    # Contract status
    info_url = f"{SIM_API_URL}/token-info?chain_ids=1&addresses={address}"
    info_res = requests.get(info_url, headers=headers)
    if info_res.ok:
        info_json = info_res.json()
        sim_data['isContract'] = info_json.get('token_info', {}).get(address, {}).get('is_contract')
    return sim_data

def main():
    try:
        address = resolve_ens_name(ENS_NAME)
        print(f"Address: {address}")
        records = fetch_ens_records(ENS_NAME)
        print(f"Records: {records}")
        sim_data = fetch_sim_data(address)
        print(f"Sim Data: {sim_data}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
