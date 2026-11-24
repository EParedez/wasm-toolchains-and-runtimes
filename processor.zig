const std = @import("std");

// This buffer is part of the module's linear memory. The processing path
// performs no dynamic allocations.
var input: [32 * 1024]u8 = undefined;

pub fn main() !void {
    const stdin = std.io.getStdIn().reader();
    const stdout = std.io.getStdOut().writer();

    const len = try stdin.readAll(&input);

    // readAll may fill the buffer before reaching EOF. Check one more byte so
    // an oversized payload is rejected instead of silently truncated.
    if (len == input.len) {
        var extra: [1]u8 = undefined;
        if (try stdin.read(&extra) != 0) return error.StreamTooLong;
    }

    for (input[0..len]) |*byte| {
        byte.* = std.ascii.toUpper(byte.*);
    }

    try stdout.print("Procesados {d} bytes en memoria fija:\n{s}\n", .{
        len,
        input[0..len],
    });
}
