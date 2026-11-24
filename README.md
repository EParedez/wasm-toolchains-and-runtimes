# Zig + Wasmtime: bounded memory with WASI

A reproducible example for a WebAssembly article. It reads up to 32 KiB from
standard input, converts ASCII letters to uppercase in the same buffer, and
writes the result. The processing code does not request dynamic memory; the
32 KiB buffer is part of the module's linear memory. This does **not** cap
Wasmtime's total memory use.

## Versions

- Zig 0.13.0
- Wasmtime 50.0.0
- WASI Preview 1 (`wasm32-wasi`)

These versions are pinned in the GitHub Actions workflow. Each CI run reports
the generated binary's actual size; this project does not assume a fixed size.

## Build and run

```sh
zig build-exe processor.zig -target wasm32-wasi -O ReleaseSmall
printf '%s' '{"event": "user_login", "status": "ok"}' | wasmtime run -C cache=n processor.wasm
python3 tests/integration.py
```

Expected output for the `printf` command above:

```text
Processed 39 bytes in fixed memory:
{"EVENT": "USER_LOGIN", "STATUS": "OK"}
```

The limit includes any newline read from `stdin`. An input of 32,768 bytes is
accepted; 32,769 bytes is rejected with `StreamTooLong`. The transformation
only affects ASCII letters and does not change non-ASCII Unicode characters.

## What CI checks

- Compilation with the pinned Zig version.
- Execution with the pinned Wasmtime version.
- Output for empty input and a JSON payload.
- Behavior at the limit and one byte beyond it.
- The generated `.wasm` file's actual size.

The workflow does not measure latency, resident memory, or instance density.
Those metrics require a separate benchmark with a documented environment and
workload.
