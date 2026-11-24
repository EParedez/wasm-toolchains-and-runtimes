# Practical WebAssembly examples

This repository contains examples for a two-part WebAssembly article:

1. [Part 1 — Emscripten](emscripten/): a C function called once per batch from
   JavaScript in Node.js or a browser.
2. [Part 2 — Zig WASI](zig-wasi/): a module with bounded input, run with
   **Wasmtime** and **WasmEdge**.

These examples demonstrate APIs and portability. They are not performance
benchmarks or proof that one runtime is faster than another.

## Versions

- Zig 0.13.0
- Wasmtime 50.0.0
- WasmEdge 0.18.1
- Emscripten 6.0.13
- WASI Preview 1 (`wasm32-wasi`)

The versions are pinned in GitHub Actions. Each CI run reports the generated
WASI binary's actual size; this project does not assume a fixed size.

## Zig WASI module: Wasmtime and WasmEdge

`zig-wasi/processor.zig` reads up to 32 KiB from standard input, converts ASCII letters
to uppercase in the same buffer, and writes the result. The processing code
does not request dynamic memory. The buffer is part of the module's linear
memory; it does **not** cap either runtime's total memory use.

Build the module with Zig 0.13.0:

```sh
zig build-exe zig-wasi/processor.zig -target wasm32-wasi -O ReleaseSmall -femit-bin=zig-wasi/processor.wasm
```

Run it with Wasmtime 50.0.0:

```sh
printf '%s' '{"event": "user_login", "status": "ok"}' | wasmtime run -C cache=n zig-wasi/processor.wasm
python3 zig-wasi/tests/integration.py
```

Run the same module with WasmEdge 0.18.1:

```sh
printf '%s' '{"event": "user_login", "status": "ok"}' | wasmedge zig-wasi/processor.wasm
python3 zig-wasi/tests/integration.py --runtime wasmedge
```

WasmEdge can also compile an AOT artifact for the current host architecture:

```sh
wasmedge compile zig-wasi/processor.wasm zig-wasi/processor-aot.wasm
python3 zig-wasi/tests/integration.py --runtime wasmedge --module zig-wasi/processor-aot.wasm --aot
```

Expected output for either runtime's `printf` command:

```text
Processed 39 bytes in fixed memory:
{"EVENT": "USER_LOGIN", "STATUS": "OK"}
```

The limit includes any newline read from `stdin`. An input of 32,768 bytes is
accepted; 32,769 bytes is rejected with `StreamTooLong`. The transformation
only affects ASCII letters and does not change non-ASCII Unicode characters.

## Emscripten: one JavaScript-to-Wasm call per batch

`emscripten/batch.c` exports a function that uppercases a byte buffer. The
JavaScript examples allocate one contiguous buffer in Wasm memory, copy the
data, call the C function once, read the result, and free the buffer. No claim
about speed follows from this pattern alone; compare it with a simple JS
implementation using your actual input sizes.

Build with Emscripten 6.0.13:

```sh
emcc emscripten/batch.c -O2 \
  -sMODULARIZE=1 \
  -sENVIRONMENT=web,node \
  -sEXPORT_NAME=createBatchModule \
  -sEXPORTED_FUNCTIONS=_uppercase_ascii,_malloc,_free \
  -sEXPORTED_RUNTIME_METHODS=HEAPU8 \
  -sALLOW_MEMORY_GROWTH=1 \
  -o emscripten/batch.js
node emscripten/test-batch.cjs
```

For the browser demo, serve the repository and open
`http://localhost:8000/emscripten/demo.html`:

```sh
python3 -m http.server 8000
```

Use a web server so the generated `.wasm` is fetched from the same origin.
If your server does not already do so, serve it with the `application/wasm`
content type.

## What CI checks

- Compilation with the pinned Zig version.
- Execution with pinned Wasmtime and WasmEdge versions, including WasmEdge AOT.
- WASI output for empty input and a JSON payload, plus behavior at the limit
  and one byte beyond it.
- Compilation with pinned Emscripten and JavaScript-to-Wasm batch calls in
  Node.js, including non-ASCII preservation and a 1 MiB input.
- The generated WASI `.wasm` file's actual size.

The workflow does not measure latency, resident memory, instance density, or
browser rendering. Those claims require separate measurements with a
documented environment and workload.
