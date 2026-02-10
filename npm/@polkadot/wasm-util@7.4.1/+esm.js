export const packageInfo = { name: '@polkadot/wasm-util', version: '7.4.1' };

// Minimal utilities expected by some modules
export function u8aToHex(u8a) {
  return Array.from(u8a || []).map(b => b.toString(16).padStart(2,'0')).join('');
}

export default { u8aToHex };
