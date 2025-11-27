import { ethers } from 'ethers';

// Use environment variable for RPC URL
const RPC_URL = process.env.NEXT_PUBLIC_ETH_RPC_URL || '';

if (!RPC_URL) {
	throw new Error('Missing NEXT_PUBLIC_ETH_RPC_URL in environment variables');
}

export const provider = new ethers.JsonRpcProvider(RPC_URL);
