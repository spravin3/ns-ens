const SIM_API_URL = 'https://api.sim.dune.com/v1/evm';
const CLOUDFLARE_ENS_URL = 'https://cloudflare-eth.com';

export async function resolveENS(ensName: string, simApiKey: string) {
	// Validate ENS name format
	if (!/^([a-z0-9-]+\.)*eth$/i.test(ensName.trim())) {
		throw new Error('Invalid ENS name format');
	}

	// Resolve ENS name to address
	const addressRes = await fetch(`${CLOUDFLARE_ENS_URL}/resolve-name/${ensName}`);
	if (!addressRes.ok) throw new Error('ENS name not found');
	const addressData = await addressRes.json();
	const address = addressData?.address;
	if (!address) throw new Error('ENS name not found');

	// Fetch ENS text records
	let records: Record<string, string> = {};
	try {
		const recordsRes = await fetch(`${CLOUDFLARE_ENS_URL}/resolve-text/${ensName}`);
		if (recordsRes.ok) {
			const recordsData = await recordsRes.json();
			records = recordsData?.records || {};
		}
	} catch {}

	// Fetch Sim API data
	let simData: any = {};
	if (simApiKey) {
		try {
			// ETH balance
			const balRes = await fetch(`${SIM_API_URL}/balances?chain_ids=1&addresses=${address}`, {
				headers: { 'X-Sim-Api-Key': simApiKey }
			});
			simData.balance = (await balRes.json()).balances?.[address]?.native?.balance || null;

			// Transaction count
			const txRes = await fetch(`${SIM_API_URL}/transactions?chain_ids=1&addresses=${address}&limit=1`, {
				headers: { 'X-Sim-Api-Key': simApiKey }
			});
			simData.txCount = (await txRes.json()).transactions?.[address]?.count || null;

			// Contract status
			const infoRes = await fetch(`${SIM_API_URL}/token-info?chain_ids=1&addresses=${address}`, {
				headers: { 'X-Sim-Api-Key': simApiKey }
			});
			simData.isContract = (await infoRes.json()).token_info?.[address]?.is_contract || false;
		} catch {}
	}

	return {
		ensName,
		address,
		records,
		simData
	};
}
