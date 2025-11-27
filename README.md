# ENS Name Lookup & Network Graph

A minimalist web app for Ethereum Name Service (ENS) profile lookup, network graph, and simple balances/metrics for the ETH chain.

## Features
- Input any ENS name (e.g., `vitalik.eth`) and view:
  - Ethereum address
  - Nametag (Etherscan PRO)
  - ETH balance
  - ETH value (live price)
  - Network metrics (coming soon)
- Powered by Streamlit (Python)
- Uses Etherscan, CoinMarketCap, and Alchemy/Infura APIs

## Usage
1. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
2. **Set environment variables:**
   ```sh
   export ETHERSCAN_API_KEY=your_etherscan_api_key
   export COINMARKETCAP_API_KEY=your_coinmarketcap_api_key
   export ETH_RPC_URL=https://eth-mainnet.g.alchemy.com/v2/YOUR_ALCHEMY_KEY
   ```
3. **Run locally:**
   ```sh
   streamlit run frontend/app.py
   ```
4. **Deploy on Streamlit Cloud:**
   - Push repo to GitHub
   - Connect to Streamlit Cloud
   - Set environment variables in app settings
   - Deploy and get public URL

## File Structure
```
ns-ens/
  scripts/
    test_address.py
    test_nametag.py
  frontend/
    app.py
  requirements.txt
  README.md
```

## .env Example
```
ETHERSCAN_API_KEY=your_etherscan_api_key
COINMARKETCAP_API_KEY=your_coinmarketcap_api_key
ETH_RPC_URL=https://eth-mainnet.g.alchemy.com/v2/YOUR_ALCHEMY_KEY
```

## .gitignore Example
See below for recommended .gitignore.

---

## License
MIT
