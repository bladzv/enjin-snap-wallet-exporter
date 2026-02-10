export const packageInfo = { name: '@polkadot/x-global', version: '13.4.4' };

const globalObj = (typeof globalThis !== 'undefined') ? globalThis : (typeof window !== 'undefined' ? window : {});

function getRandomValues(buf) {
  if (globalObj.crypto && typeof globalObj.crypto.getRandomValues === 'function') return globalObj.crypto.getRandomValues(buf);
  if (typeof require === 'function') {
    try { const crypto = require('crypto'); const rv = crypto.randomBytes(buf.length); buf.set(rv); return buf; } catch(e) {}
  }
  for (let i=0;i<buf.length;i++) buf[i] = Math.floor(Math.random()*256);
  return buf;
}

export const xglobal = { getRandomValues };
export function exposeGlobal() { return globalObj; }
export function extractGlobal() { return globalObj; }

export default xglobal;
// Minimal shim for @polkadot/x-global for offline use
export const packageInfo = { name: '@polkadot/x-global', version: '13.4.4' };

const _global = (typeof globalThis !== 'undefined') ? globalThis : (typeof window !== 'undefined' ? window : {});

export const xglobal = {
  crypto: (_global && _global.crypto) ? _global.crypto : { getRandomValues: () => { throw new Error('crypto.getRandomValues unavailable') } }
};

export function exposeGlobal(name, value) {
  try { if (_global) _global[name] = value; } catch (e) { /* ignore */ }
}

export function extractGlobal(name, fallback) {
  try { return (_global && _global[name]) || fallback; } catch (e) { return fallback; }
}

export default null;
