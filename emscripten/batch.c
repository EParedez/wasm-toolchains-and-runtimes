#include <stddef.h>
#include <stdint.h>

// The caller owns the buffer and invokes this function once per batch.
void uppercase_ascii(uint8_t *data, size_t len) {
  for (size_t i = 0; i < len; ++i) {
    if (data[i] >= 'a' && data[i] <= 'z') {
      data[i] = (uint8_t)(data[i] - ('a' - 'A'));
    }
  }
}
