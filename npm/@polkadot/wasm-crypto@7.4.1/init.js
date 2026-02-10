// init.js shim for @polkadot/wasm-crypto — no-op initializer
export async function init() {
  return true;
}

export const isReady = true;

export default { init, isReady };
