// asm.js shim fallback for @polkadot/wasm-crypto
export function asm() { return true; }
export const isReady = true;
export default { asm, isReady };
