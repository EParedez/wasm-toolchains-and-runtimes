const assert = require('node:assert/strict');
const createBatchModule = require('./batch.js');

async function main() {
  const module = await createBatchModule();
  const encoder = new TextEncoder();
  const decoder = new TextDecoder();

  function uppercase(text) {
    const bytes = encoder.encode(text);
    if (bytes.length === 0) return '';
    const pointer = module._malloc(bytes.length);
    if (pointer === 0) throw new Error('Wasm allocation failed');
    try {
      module.HEAPU8.set(bytes, pointer);
      module._uppercase_ascii(pointer, bytes.length);
      // Read the canonical view after calls that might grow Wasm memory.
      return decoder.decode(module.HEAPU8.subarray(pointer, pointer + bytes.length));
    } finally {
      module._free(pointer);
    }
  }

  assert.equal(uppercase(''), '');
  assert.equal(uppercase('hello from JS'), 'HELLO FROM JS');
  assert.equal(uppercase('café'), 'CAFé');
  assert.equal(uppercase('a'.repeat(1024 * 1024)), 'A'.repeat(1024 * 1024));
  console.log('OK (Emscripten): empty, ASCII, Unicode preservation, and 1 MiB batch');
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
