export const packageInfo = { name: '@polkadot/x-textdecoder', version: '13.4.4' };

const TD = (typeof TextDecoder !== 'undefined') ? TextDecoder : class TextDecoder {
  decode(input) { try { return new Uint8Array(input).toString(); } catch (e) { return '' } }
};

export { TD as TextDecoder };
export default null;
