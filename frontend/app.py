import os
import streamlit as st
from web3 import Web3
import requests
import pandas as pd
import networkx as nx
import plotly.graph_objects as go

st.set_page_config(page_title="ENS Profile Lookup", page_icon="🔎", layout="wide")

ETHERSCAN_API_KEY = os.getenv('ETHERSCAN_API_KEY')
COINMARKETCAP_API_KEY = os.getenv('COINMARKETCAP_API_KEY')
ETH_RPC_URL = os.getenv('ETH_RPC_URL')
SIM_API_KEY = os.getenv('SIM_API_KEY')

# Initialize session state for selected ENS
if 'selected_ens_for_main' not in st.session_state:
    st.session_state['selected_ens_for_main'] = None
if 'current_page' not in st.session_state:
    st.session_state['current_page'] = "ENS Main Lookup"

# Check if we need to switch to main lookup from a node click
if st.session_state.get('selected_ens_for_main'):
    st.session_state['current_page'] = "ENS Main Lookup"

# Create tabs for navigation
tab1, tab2 = st.tabs(["🔎 ENS Main Lookup", "🕸️ ENS List Lookup"])

with tab1:
    st.write("Enter an ENS name to view the 4 key metrics.")
    
    # Use selected ENS from graph if available, otherwise use default
    default_ens = st.session_state.get('selected_ens_for_main', 'vitalik.eth')
    ens_name = st.text_input("ENS Name", default_ens)
    
    # Auto-lookup if ENS was selected from graph
    auto_lookup = False
    if st.session_state.get('selected_ens_for_main'):
        auto_lookup = True
        st.session_state['selected_ens_for_main'] = None
    
    if st.button("Lookup", type="primary") or auto_lookup:
        with st.spinner("Resolving ENS and fetching data..."):
            w3 = Web3(Web3.HTTPProvider(ETH_RPC_URL))
            address = w3.ens.address(ens_name)
            
            if not address:
                st.error(f"ENS name not found: {ens_name}")
                st.stop()
            
            st.success(f"**Address:** `{address}`")
            
            # Metric 1: ETH Balance
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
            
            # Metric 2: ETH USD Value
            price = None
            try:
                price_url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?symbol=ETH"
                headers = {"X-CMC_PRO_API_KEY": COINMARKETCAP_API_KEY}
                price_res = requests.get(price_url, headers=headers)
                price_data = price_res.json()
                price = price_data['data']['ETH']['quote']['USD']['price']
                eth_usd = balance_eth * price
            except Exception:
                eth_usd = 0
                price = 0
            
            # Display 4 Key Metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(label="📍 Address", value=f"{address[:6]}...{address[-4:]}")
            
            with col2:
                st.metric(label="💰 ETH Balance", value=f"{balance_eth:.4f} ETH")
            
            with col3:
                st.metric(label="💵 USD Value", value=f"${eth_usd:,.2f}")
            
            with col4:
                st.metric(label="📈 ETH Price", value=f"${price:,.2f}")
            
            # Last 10 Internal Transactions
            st.subheader("📜 Last 10 Internal Transactions")
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
                tx_table = []
                for tx in txs:
                    tx_table.append({
                        "Hash": tx.get('hash', '')[:16] + "...",
                        "From": tx.get('from', '')[:10] + "...",
                        "To": tx.get('to', '')[:10] + "...",
                        "Value (ETH)": f"{float(tx.get('value', '0')) / 1e18:.4f}",
                        "Timestamp": tx.get('timeStamp', '')
                    })
                df_tx = pd.DataFrame(tx_table)
                st.dataframe(df_tx, use_container_width=True)
            else:
                st.info("No internal transactions found.")

with tab2:
    st.write("Enter a comma-separated list of ENS names to visualize their social network.")
    
    ens_list = st.text_area("ENS Names (comma separated)", "vitalik.eth, balajis.eth, brantley.eth")
    ens_names = [e.strip() for e in ens_list.split(",") if e.strip()]
    
    if st.button("Build Social Graph", type="primary"):
        w3 = Web3(Web3.HTTPProvider(ETH_RPC_URL))
        
        with st.spinner("Resolving ENS names and building graph..."):
            # Resolve all ENS names
            addresses = {}
            balances = {}
            for ens in ens_names:
                try:
                    addr = w3.ens.address(ens)
                    if addr:
                        addresses[ens] = addr
                        # Get balance for each
                        bal_url = (
                            f"https://api.etherscan.io/v2/api"
                            f"?chainid=1"
                            f"&module=account"
                            f"&action=balance"
                            f"&address={addr}"
                            f"&tag=latest"
                            f"&apikey={ETHERSCAN_API_KEY}"
                        )
                        bal_res = requests.get(bal_url)
                        bal_data = bal_res.json()
                        balance_wei = int(bal_data.get('result', '0'))
                        balances[ens] = balance_wei / 1e18
                except Exception as e:
                    st.warning(f"Could not resolve {ens}: {e}")
                    continue
            
            if not addresses:
                st.error("No valid ENS names resolved.")
                st.stop()
            
            # Build NetworkX graph
            G = nx.Graph()
            for ens, addr in addresses.items():
                G.add_node(ens, address=addr, balance=balances.get(ens, 0))
            
            # Create edges (for demo: connecting all nodes in a network)
            resolved_names = list(addresses.keys())
            for i in range(len(resolved_names)):
                for j in range(i+1, len(resolved_names)):
                    G.add_edge(resolved_names[i], resolved_names[j])
            
            # Store in session state
            st.session_state['graph'] = G
            st.session_state['addresses'] = addresses
            st.session_state['balances'] = balances
            
            st.success(f"✅ Graph built with {len(G.nodes)} nodes and {len(G.edges)} edges")
    
    # Display graph and data if it exists
    if 'graph' in st.session_state:
        G = st.session_state['graph']
        addresses = st.session_state['addresses']
        balances = st.session_state['balances']
        
        # Display data table
        st.subheader("📊 ENS Profile Summary")
        table_data = []
        for ens, addr in addresses.items():
            table_data.append({
                "ENS Name": ens,
                "Address": f"{addr[:6]}...{addr[-4:]}",
                "Full Address": addr,
                "ETH Balance": f"{balances.get(ens, 0):.4f}"
            })
        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True)
        
        # Visualize graph with Plotly (interactive and clickable)
        st.subheader("🔗 Interactive Social Network Graph")
        
        # Get positions using NetworkX spring layout
        pos = nx.spring_layout(G, k=2, iterations=50)
        
        # Create edge traces
        edge_trace = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_trace.append(
                go.Scatter(
                    x=[x0, x1, None],
                    y=[y0, y1, None],
                    mode='lines',
                    line=dict(width=2, color='#888'),
                    hoverinfo='none',
                    showlegend=False
                )
            )
        
        # Create node trace
        node_x = []
        node_y = []
        node_text = []
        node_customdata = []
        
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            addr = G.nodes[node]['address']
            bal = G.nodes[node]['balance']
            node_text.append(f"{node}<br>Balance: {bal:.4f} ETH<br>{addr[:10]}...")
            node_customdata.append(node)
        
        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=[node for node in G.nodes()],
            textposition="top center",
            hovertext=node_text,
            customdata=node_customdata,
            marker=dict(
                size=30,
                color='lightblue',
                line=dict(width=2, color='darkblue')
            ),
            textfont=dict(size=12, color='black', family='Arial Black'),
            showlegend=False
        )
        
        # Create figure
        fig = go.Figure(data=edge_trace + [node_trace])
        
        fig.update_layout(
            title=dict(
                text="ENS Social Network - Click on a node to view profile",
                font=dict(size=20, color='darkblue')
            ),
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20, l=5, r=5, t=60),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='white',
            height=600
        )
        
        # Display the interactive graph
        selected_point = st.plotly_chart(fig, use_container_width=True, key="network_graph", on_select="rerun")
        
        # Handle node selection from graph click
        if selected_point and selected_point.get('selection') and selected_point['selection'].get('points'):
            points = selected_point['selection']['points']
            if points:
                clicked_ens = points[0].get('customdata')
                if clicked_ens:
                    st.session_state['selected_ens_for_main'] = clicked_ens
                    st.rerun()
        
        # Graph statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Nodes", len(G.nodes))
        with col2:
            st.metric("Total Edges", len(G.edges))
        with col3:
            st.metric("Network Density", f"{nx.density(G):.2f}")
        
        # Alternative: Clickable node buttons (in case graph click doesn't work in deployment)
        st.subheader("👤 Quick Node Access")
        st.write("Click on a node in the graph above, or use these buttons:")
        
        cols = st.columns(min(len(G.nodes), 4))
        for idx, node in enumerate(G.nodes):
            with cols[idx % 4]:
                if st.button(f"📍 {node}", key=f"btn_{node}", use_container_width=True):
                    st.session_state['selected_ens_for_main'] = node
                    st.rerun()
