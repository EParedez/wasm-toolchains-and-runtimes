"""Run the compiled WASI module and check its input boundaries."""

import argparse
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LIMIT = 32 * 1024


def run(payload: bytes, runtime: str, module: Path, aot: bool) -> subprocess.CompletedProcess[bytes]:
    if runtime == "wasmtime":
        command = ["wasmtime", "run", "-C", "cache=n", str(module)]
    else:
        command = ["wasmedge"]
        if aot:
            command.append("--run-mode=aot")
        command.append(str(module))
    return subprocess.run(
        command,
        input=payload,
        capture_output=True,
        check=False,
    )


def expect_success(payload: bytes, transformed: bytes, runtime: str, module: Path, aot: bool) -> None:
    result = run(payload, runtime, module, aot)
    expected = (
        f"Processed {len(payload)} bytes in fixed memory:\n".encode()
        + transformed
        + b"\n"
    )
    assert result.returncode == 0, result.stderr.decode(errors="replace")
    assert result.stdout == expected, (
        f"Unexpected output for {len(payload)} bytes: {result.stdout[:120]!r}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime", choices=("wasmtime", "wasmedge"), default="wasmtime")
    parser.add_argument("--module", type=Path, default=ROOT / "processor.wasm")
    parser.add_argument("--aot", action="store_true", help="Run a WasmEdge AOT artifact")
    args = parser.parse_args()
    if args.aot and args.runtime != "wasmedge":
        parser.error("--aot requires --runtime wasmedge")
    module = args.module.resolve()
    assert module.is_file(), f"Compile {module.name} before running the tests"

    expect_success(b"", b"", args.runtime, module, args.aot)
    expect_success(
        b'{"event": "user_login", "status": "ok"}',
        b'{"EVENT": "USER_LOGIN", "STATUS": "OK"}',
        args.runtime,
        module,
        args.aot,
    )
    expect_success(b"a" * LIMIT, b"A" * LIMIT, args.runtime, module, args.aot)

    oversized = run(b"a" * (LIMIT + 1), args.runtime, module, args.aot)
    assert oversized.returncode != 0, "Oversized input was silently accepted"
    assert b"StreamTooLong" in oversized.stderr, oversized.stderr[:500]

    print(f"OK ({args.runtime}{' AOT' if args.aot else ''}): empty, JSON, exact limit, and oversized input")
    print(f"Artifact size: {module.stat().st_size} bytes")


if __name__ == "__main__":
    main()
