"""Run the compiled WASI module with Wasmtime and check its boundaries."""

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "processor.wasm"
LIMIT = 32 * 1024


def run(payload: bytes) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["wasmtime", "run", "-C", "cache=n", str(MODULE)],
        input=payload,
        capture_output=True,
        check=False,
    )


def expect_success(payload: bytes, transformed: bytes) -> None:
    result = run(payload)
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
    assert MODULE.is_file(), "Compile processor.wasm before running the tests"

    expect_success(b"", b"")
    expect_success(
        b'{"event": "user_login", "status": "ok"}',
        b'{"EVENT": "USER_LOGIN", "STATUS": "OK"}',
    )
    expect_success(b"a" * LIMIT, b"A" * LIMIT)

    oversized = run(b"a" * (LIMIT + 1))
    assert oversized.returncode != 0, "Oversized input was silently accepted"
    assert b"StreamTooLong" in oversized.stderr, oversized.stderr[:500]

    print("OK: empty, JSON, exact limit, and oversized input")
    print(f"Wasm size: {MODULE.stat().st_size} bytes")


if __name__ == "__main__":
    main()
