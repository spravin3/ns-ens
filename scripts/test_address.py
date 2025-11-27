import os
import requests

SIM_API_KEY = os.getenv('SIM_API_KEY')
SIM_API_URL = 'https://api.sim.dune.com/v1/evm'

ETHERSCAN_API_KEY = os.getenv('ETHERSCAN_API_KEY')
COINMARKETCAP_API_KEY = os.getenv('COINMARKETCAP_API_KEY')
ADDRESS = '0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045'

def fetch_etherscan_data(address):
    # Get ETH balance (V2)
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
    bal_res.raise_for_status()
    bal_data = bal_res.json()
    balance_wei = int(bal_data.get('result', '0'))
    balance_eth = balance_wei / 1e18

    # Get Nametag (PRO endpoint)
    nametag_url = (
        f"https://api.etherscan.io/v2/api"
        f"?chainid=1"
        f"&module=nametag"
        f"&action=getaddresstag"
        f"&address={address}"
        f"&apikey={ETHERSCAN_API_KEY}"
    )
    nametag = None
    try:
        nametag_res = requests.get(nametag_url)
        nametag_res.raise_for_status()
        nametag_data = nametag_res.json()
        nametag = nametag_data.get('result', {}).get('nameTag')
    except Exception:
        nametag = None

    return {
        'balance_wei': balance_wei,
        'balance_eth': balance_eth,
        'nametag': nametag
    }
def fetch_eth_price():
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?symbol=ETH"
    headers = {"X-CMC_PRO_API_KEY": COINMARKETCAP_API_KEY}
    res = requests.get(url, headers=headers)
    res.raise_for_status()
    data = res.json()
    price = data['data']['ETH']['quote']['USD']['price']
    return price

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
        print(f"--- Etherscan Data for {ADDRESS} ---")
        ethscan = fetch_etherscan_data(ADDRESS)
        print(f"Nametag: {ethscan['nametag']}")
        print(f"ETH Balance: {ethscan['balance_eth']} ETH")
        eth_price = fetch_eth_price()
        print(f"ETH Value: ${ethscan['balance_eth'] * eth_price:,.2f} (@ ${eth_price:,.2f}/ETH)")
        print(f"--- Sim Data for {ADDRESS} ---")
        simdata = fetch_sim_data(ADDRESS)
        print(simdata)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
