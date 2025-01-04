#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <err.h>

#include "base64.h"
#include "pwd.h"

// Caller shall free
char *pwd_encode(const unsigned char *plain, size_t plain_len)
{
	size_t truncated_len = plain_len < 12 ? plain_len : 12;
	unsigned char truncated[12];
	memcpy(truncated, plain, truncated_len);

	const unsigned char key[12] = "pfswpfswpfsw";

	unsigned char cipher[12];
	for (size_t i = 0; i < truncated_len; i++) {
		cipher[i] = truncated[i] ^ key[i];
	}

	size_t encoded_len;
	char *encoded = base64_encode(cipher, truncated_len, &encoded_len);

	return encoded;
}
