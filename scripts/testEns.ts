import { resolveENS } from '../lib/ens';

async function main() {
  try {
    const result = await resolveENS('vitalik.eth');
    console.log('--- ENS Profile for vitalik.eth ---');
    console.log('Address:', result.address);
    console.log('Records:', result.records);
    console.log('Sim Data:', result.simData);
  } catch (err) {
    console.error('Error:', err);
  }
}

main();
