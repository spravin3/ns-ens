st.set_page_config(page_title="ENS Profile Lookup", page_icon="🔎", layout="centered")
st.title("ENS Profile Lookup")
st.write("Enter any ENS name (e.g. vitalik.eth) to view profile stats.")
import os
import streamlit as st
from web3 import Web3
import requests

st.set_page_config(page_title="ENS Profile Lookup", page_icon="🔎", layout="centered")

ETHERSCAN_API_KEY = os.getenv('ETHERSCAN_API_KEY')
COINMARKETCAP_API_KEY = os.getenv('COINMARKETCAP_API_KEY')
ETH_RPC_URL = os.getenv('ETH_RPC_URL')
SIM_API_KEY = os.getenv('SIM_API_KEY')

pages = ["ENS Main Lookup", "ENS List Lookup"]
page = st.sidebar.selectbox("Select Page", pages)

if page == "ENS Main Lookup":
    st.title("ENS Main Lookup")
    st.write("Enter any ENS name (e.g. vitalik.eth) to view profile stats.")
    ens_name = st.text_input("ENS Name", "vitalik.eth")
    if st.button("Lookup"):
        with st.spinner("Resolving ENS and fetching data..."):
            w3 = Web3(Web3.HTTPProvider(ETH_RPC_URL))
            address = w3.ens.address(ens_name)
            if not address:
                st.error(f"ENS name not found: {ens_name}")
                st.stop()
            st.write(f"**Address:** {address}")

            # ETH balance and USD value
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

            # ETH price (CoinMarketCap)
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
                eth_usd = balance_eth * price
                st.write(f"**ETH Token Balance:** {balance_eth:.4f} ETH")
                st.write(f"**ETH USD Balance:** ${eth_usd:,.2f}")
                st.caption(f"(Price from CMC: ${eth_usd:,.2f} @ ${price:,.2f}/ETH)")
            else:
                st.write(f"**ETH Token Balance:** {balance_eth:.4f} ETH")
                st.write(f"**ETH USD Balance:** (USD price unavailable)")

            # Last 10 internal transactions (Etherscan V2)
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
                with st.expander("Last 10 Internal Transactions"):
                    import pandas as pd
                    tx_table = []
                    for tx in txs:
                        tx_table.append({
                            "Hash": tx.get('hash', ''),
                            "From": tx.get('from', ''),
                            "To": tx.get('to', ''),
                            "Value (ETH)": float(tx.get('value', '0')) / 1e18,
                            "Time": tx.get('timeStamp', '')
                        })
                    df = pd.DataFrame(tx_table)
                    st.dataframe(df)

            # Token Holdings (SIM API)
            if SIM_API_KEY:
                sim_bal_url = f"https://api.sim.dev.dune.com/v1/evm/balances/{address}?chain_ids=1&exclude_spam_tokens=true"
                sim_headers = {"X-Sim-Api-Key": SIM_API_KEY}
                try:
                    sim_bal_res = requests.get(sim_bal_url, headers=sim_headers)
                    sim_bal_data = sim_bal_res.json()
                    balances = sim_bal_data.get('balances', [])
                    if balances:
                        with st.expander("Token Holdings (SIM API)"):
                            token_table = []
                            for bal in balances:
                                symbol = bal.get('symbol', '')
                                name = bal.get('name', '')
                                amount = int(bal.get('amount', '0')) / (10 ** int(bal.get('decimals', 0))) if bal.get('decimals') else float(bal.get('amount', '0'))
                                usd = bal.get('value_usd', None)
                                price = bal.get('price_usd', None)
                                token_table.append({
                                    "Symbol": symbol,
                                    "Name": name,
                                    "Amount": amount,
                                    "USD Value": usd,
                                    "Price": price
                                })
                            df_tokens = pd.DataFrame(token_table)
                            st.dataframe(df_tokens)
                except Exception as e:
                    st.write(f"SIM API balances error: {e}")

elif page == "ENS List Lookup":
    st.title("ENS List Lookup & Social Graph")
    st.write("Enter a comma-separated list of ENS names to visualize their social network and click nodes for deep profile lookup.")
    import networkx as nx
    import pandas as pd
    ens_list = st.text_area("ENS Names (comma separated)", "vitalik.eth, balajis.eth")
    ens_names = [e.strip() for e in ens_list.split(",") if e.strip()]
    if st.button("Build Social Graph"):
        w3 = Web3(Web3.HTTPProvider(ETH_RPC_URL))
        addresses = {}
        for ens in ens_names:
            try:
                addr = w3.ens.address(ens)
                if addr:
                    addresses[ens] = addr
            except Exception:
                continue
        # Build a simple graph: each ENS is a node, edges if they follow/interact (mock: all connected)
        G = nx.Graph()
        for ens, addr in addresses.items():
            G.add_node(ens, address=addr)
        # For demo, connect all nodes to each other
        for i in range(len(ens_names)):
            for j in range(i+1, len(ens_names)):
                G.add_edge(ens_names[i], ens_names[j])
        st.write(f"Graph with {len(G.nodes)} nodes and {len(G.edges)} edges.")
        st.write(pd.DataFrame({"ENS": list(addresses.keys()), "Address": list(addresses.values())}))
        # Node profile lookup
        for node in G.nodes:
            if st.button(f"View {node} Profile"):
                st.session_state["selected_ens"] = node
                st.experimental_rerun()
    # Deep profile lookup
    if "selected_ens" in st.session_state:
        st.subheader(f"Profile for {st.session_state['selected_ens']}")
        w3 = Web3(Web3.HTTPProvider(ETH_RPC_URL))
        ens_name = st.session_state["selected_ens"]
        address = w3.ens.address(ens_name)
        st.write(f"**Address:** {address}")
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
        st.write(f"**ETH Token Balance:** {balance_eth:.4f} ETH")
        if SIM_API_KEY:
            sim_bal_url = f"https://api.sim.dev.dune.com/v1/evm/balances/{address}?chain_ids=1&exclude_spam_tokens=true"
            sim_headers = {"X-Sim-Api-Key": SIM_API_KEY}
            try:
                sim_bal_res = requests.get(sim_bal_url, headers=sim_headers)
                sim_bal_data = sim_bal_res.json()
                balances = sim_bal_data.get('balances', [])
                if balances:
                    st.write("Token Holdings (SIM API):")
                    token_table = []
                    for bal in balances:
                        symbol = bal.get('symbol', '')
                        name = bal.get('name', '')
                        amount = int(bal.get('amount', '0')) / (10 ** int(bal.get('decimals', 0))) if bal.get('decimals') else float(bal.get('amount', '0'))
                        usd = bal.get('value_usd', None)
                        price = bal.get('price_usd', None)
                        token_table.append({
                            "Symbol": symbol,
                            "Name": name,
                            "Amount": amount,
                            "USD Value": usd,
                            "Price": price
                        })
                    df_tokens = pd.DataFrame(token_table)
                    st.dataframe(df_tokens)
            except Exception as e:
                st.write(f"SIM API balances error: {e}")
