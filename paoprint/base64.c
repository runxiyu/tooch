/* TODO: This base64 implementation does not handle padding correctly */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <err.h>

#include "base64.h"

const char base64_sbox[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";

// Caller shall free
char *base64_encode(const unsigned char *data, size_t input_len, size_t *output_len)
{
	*output_len = 4 * ((input_len + 2) / 3);
	char *encoded = malloc(*output_len + 1);
	if (encoded == NULL)
		err(EXIT_FAILURE, "malloc");

	size_t i, j;
	for (i = 0, j = 0; i < input_len;) {
		uint32_t octet_first = i < input_len ? data[i++] : 0;
		uint32_t octet_second = i < input_len ? data[i++] : 0;
		uint32_t octet_third = i < input_len ? data[i++] : 0;

		uint32_t octets = (octet_first << 16) | (octet_second << 8) | octet_third;

		encoded[j++] = base64_sbox[0x3F & (octets >> 18)];
		encoded[j++] = base64_sbox[0x3F & (octets >> 12)];
		encoded[j++] = (i > (input_len + 1)) ? '=' : base64_sbox[0x3F & (octets >> 6)];
		encoded[j++] = (i > input_len) ? '=' : base64_sbox[0x3F & octets ];
	}

	encoded[j] = '\0';
	return encoded;
}
