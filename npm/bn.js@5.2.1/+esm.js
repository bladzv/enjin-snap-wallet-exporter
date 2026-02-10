// Minimal bn.js shim providing BN constructor with toArrayLike method used by some polkadot libs
export const packageInfo = { name: 'bn.js', version: '5.2.1' };

export class BN {
  constructor(input) { this._v = BigInt(input||0); }
  toArrayLike(ArrayType, endian, length) {
    let hex = this._v.toString(16);
    if (hex.length % 2) hex = '0' + hex;
    const bytes = hex.match(/.{1,2}/g).map(h => parseInt(h,16));
    if (length && bytes.length < length) {
      const pad = new Array(length - bytes.length).fill(0);
      return Uint8Array.from((endian === 'le') ? bytes.reverse().concat(pad) : pad.concat(bytes));
    }
    return Uint8Array.from((endian === 'le') ? bytes.reverse() : bytes);
  }
}

export default BN;
