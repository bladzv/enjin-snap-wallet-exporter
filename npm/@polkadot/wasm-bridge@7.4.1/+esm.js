export const packageInfo = { name: '@polkadot/wasm-bridge', version: '7.4.1' };

// Minimal bridge shim: provide a no-op init and a flag indicating readiness.
export async function init() {
  return true;
}

export const isReady = true;

export default { init, isReady };
