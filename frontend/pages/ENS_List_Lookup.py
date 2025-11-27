import os
import streamlit as st
import networkx as nx
import pandas as pd
from web3 import Web3
import requests

st.set_page_config(page_title="ENS List Lookup", page_icon="🔗", layout="wide")
st.title("ENS List Lookup & Social Graph")
st.write("Enter a comma-separated list of ENS names to visualize their social network and click nodes for deep profile lookup.")

ETHERSCAN_API_KEY = os.getenv('ETHERSCAN_API_KEY')
ETH_RPC_URL = os.getenv('ETH_RPC_URL')
SIM_API_KEY = os.getenv('SIM_API_KEY')

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
    # Draw graph with clickable nodes
    import streamlit.components.v1 as components
    import networkx.readwrite
    import json
    # Use networkx to_json_graph for D3.js
    data = networkx.readwrite.json_graph.node_link_data(G)
    graph_json = json.dumps(data)
    # Use streamlit-agraph or custom D3 (for demo, show table)
    st.write("Nodes:")
    for node in G.nodes:
        if st.button(f"View {node} Profile"):
            st.session_state["selected_ens"] = node
            st.experimental_rerun()
    st.write(pd.DataFrame({"ENS": list(addresses.keys()), "Address": list(addresses.values())}))

# Deep profile lookup (reuse main page logic)
if "selected_ens" in st.session_state:
    st.subheader(f"Profile for {st.session_state['selected_ens']}")
    # ...existing logic from main page (copy from app.py)...
    w3 = Web3(Web3.HTTPProvider(ETH_RPC_URL))
    ens_name = st.session_state["selected_ens"]
    address = w3.ens.address(ens_name)
    st.write(f"**Address:** {address}")
    # ETH balance
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
    # Token Holdings (SIM API)
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
