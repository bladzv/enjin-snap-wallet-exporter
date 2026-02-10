export const packageInfo = { name: '@polkadot/x-textencoder', version: '13.4.4' };

const TE = (typeof TextEncoder !== 'undefined') ? TextEncoder : class TextEncoder {
  encode(str='') { const enc = []; for (let i=0;i<str.length;i++) enc.push(str.charCodeAt(i)); return new Uint8Array(enc); }
};

export { TE as TextEncoder };
export default null;
