// wasm.js shim for @polkadot/wasm-crypto — provides a no-op wasm initializer
export async function wasm() {
  return true;
}

export const isReady = true;

export default { wasm, isReady };
