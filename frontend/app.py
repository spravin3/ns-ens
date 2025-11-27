import os
import streamlit as st
from web3 import Web3
import requests

st.set_page_config(page_title="ENS Profile Lookup", page_icon="🔎", layout="centered")
st.title("ENS Profile Lookup")
st.write("Enter any ENS name (e.g. vitalik.eth) to view profile stats.")

ETHERSCAN_API_KEY = os.getenv('ETHERSCAN_API_KEY')
COINMARKETCAP_API_KEY = os.getenv('COINMARKETCAP_API_KEY')
ETH_RPC_URL = os.getenv('ETH_RPC_URL')

ens_name = st.text_input("ENS Name", "vitalik.eth")

if st.button("Lookup"):
    with st.spinner("Resolving ENS and fetching data..."):
        # Step 1: ENS to address
        w3 = Web3(Web3.HTTPProvider(ETH_RPC_URL))
        address = w3.ens.address(ens_name)
        if not address:
            st.error(f"ENS name not found: {ens_name}")
            st.stop()
        st.write(f"**Address:** {address}")

        # Step 2: ETH balance
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
        st.write(f"**ETH Balance:** {balance_eth:.6f} ETH")

        # Step 3: Nametag
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
            nametag_data = nametag_res.json()
            nametag = nametag_data.get('result', {}).get('nameTag')
        except Exception:
            nametag = None
        st.write(f"**Nametag:** {nametag if nametag else 'N/A'}")

        # Step 4: ETH price
        price = None
        try:
            price_url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?symbol=ETH"
            headers = {"X-CMC_PRO_API_KEY": COINMARKETCAP_API_KEY}
            price_res = requests.get(price_url, headers=headers)
            price_data = price_res.json()
            price = price_data['data']['ETH']['quote']['USD']['price']
        except Exception:
            price = None
        if price:
            st.write(f"**ETH Value:** ${balance_eth * price:,.2f} (@ ${price:,.2f}/ETH)")
        else:
            st.write("**ETH Value:** N/A (price fetch failed)")
