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
SIM_API_KEY = os.getenv('SIM_API_KEY')

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

        # Step 3: ENS text records (avatar, display name, bio, socials)
        profile = {}
        try:
            resolver = w3.ens.resolver(ens_name)
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
                st.write(f"**{label}:** {profile[key]}")


        # Step 4: Token Holdings (SIM API)
        if SIM_API_KEY:
            sim_bal_url = f"https://api.sim.dev.dune.com/v1/evm/balances/{address}?chain_ids=1&exclude_spam_tokens=true"
            sim_headers = {"X-Sim-Api-Key": SIM_API_KEY}
            try:
                sim_bal_res = requests.get(sim_bal_url, headers=sim_headers)
                sim_bal_data = sim_bal_res.json()
                balances = sim_bal_data.get('balances', [])
                if balances:
                    st.write("\n**Token Holdings (SIM API):**")
                    for bal in balances:
                        symbol = bal.get('symbol', '')
                        name = bal.get('name', '')
                        amount = int(bal.get('amount', '0')) / (10 ** int(bal.get('decimals', 0))) if bal.get('decimals') else float(bal.get('amount', '0'))
                        usd = bal.get('value_usd', None)
                        price = bal.get('price_usd', None)
                        line = f"- {symbol} ({name}): {amount:.4f}"
                        if usd:
                            line += f" | USD Value: ${usd:,.2f}"
                        if price:
                            line += f" | Price: ${price:,.2f}"
                        st.write(line)
            except Exception as e:
                st.write(f"SIM API balances error: {e}")
