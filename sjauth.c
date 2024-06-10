/*
 * Script to log in to YK Pao School Songjiang Campus student WiFi
 * Written by Runxi Yu <me@runxiyu.org>
 *
 * This program is public domain, or under the terms of Creative Commons
 * Zero 1.0 Universal, at your choice. In addition, a Waiver of Patent
 * Rights apply. See the LICENSE file for details.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <curl/curl.h>

// I just blindly translated this and it seems to work... didn't bother
// to really test it with all sorts of data
void rc4(const char *plain, const char *rc4key, char *output)
{
	int sbox[256];
	int key_length = strlen(rc4key);
	int i, j = 0, a = 0, b = 0, c;
	size_t plain_length = strlen(plain);
	for (i = 0; i < 256; i++)
		sbox[i] = i;
	for (i = 0; i < 256; i++) {
		j = (j + sbox[i] + rc4key[i % key_length]) % 256;
		int temp = sbox[i];
		sbox[i] = sbox[j];
		sbox[j] = temp;
	}
	for (i = 0; i < (int)plain_length; i++) {
		a = (a + 1) % 256;
		b = (b + sbox[a]) % 256;
		int temp = sbox[a];
		sbox[a] = sbox[b];
		sbox[b] = temp;
		c = (sbox[a] + sbox[b]) % 256;
		sprintf(output + i * 2, "%02x", plain[i] ^ sbox[c]);
	}
	output[plain_length * 2] = '\0';
}

size_t wc(void *ptr, size_t size, size_t nmemb, void *userdata)
{
	memcpy(userdata, ptr, size * nmemb);
	return size * nmemb;
}

void login(const char *username, const char *password, char *response)
{
	CURL *curl;
	CURLcode res;
	char ts[32];
	char rc4_output[256];
	long timestamp = (long)(time(NULL) * 100);
	snprintf(ts, sizeof(ts), "%ld", timestamp);

	rc4(password, ts, rc4_output);

	char postfields[512];
	snprintf(postfields, sizeof(postfields),
		 "opr=pwdLogin&userName=%s&pwd=%s&rc4Key=%s&auth_tag=%s&rememberPwd=1",
		 username, rc4_output, ts, ts);

	curl_global_init(CURL_GLOBAL_DEFAULT);
	curl = curl_easy_init();
	if (curl) {
		curl_easy_setopt(curl, CURLOPT_URL,
				 "http://sjauth.ykpaoschool.cn/ac_portal/login.php");
		curl_easy_setopt(curl, CURLOPT_POSTFIELDS, postfields);
		curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, wc);
		curl_easy_setopt(curl, CURLOPT_WRITEDATA, response);

		struct curl_slist *headers = NULL;
		headers =
		    curl_slist_append(headers,
				      "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:104.0) Gecko/20100101 Firefox/104.0");
		headers =
		    curl_slist_append(headers,
				      "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8");
		headers =
		    curl_slist_append(headers,
				      "Accept-Language: en-US.en;q=0.5");
		headers =
		    curl_slist_append(headers,
				      "Content-Type: application/x-www-form-urlencoded; charset=UTF-8");
		headers = curl_slist_append(headers, "Origin: null");
		headers = curl_slist_append(headers, "Connection: keep-alive");
		curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);

		res = curl_easy_perform(curl);
		if (res != CURLE_OK) {
			fprintf(stderr, "curl_easy_perform() failed: %s\n",
				curl_easy_strerror(res));
		}

		curl_slist_free_all(headers);
		curl_easy_cleanup(curl);
	}
	curl_global_cleanup();
}

int main(int argc, char *argv[])
{
	if (argc != 3) {
		fprintf(stderr,
			"%s: Invalid arguments. The first argument shall be your username, and the second shall be the name of the environment variable containing your password.\n",
			argv[0]);
		return 1;
	}

	const char *username = argv[1];
	const char *password = getenv(argv[2]);
	if (!password) {
		fprintf(stderr,
			"%s: Environment variable %s does not exist. You shall cause the variable identified by %s to contain your password.\n",
			argv[0], argv[2], argv[2]);
		return 2;
	}

	char response[2048];
	login(username, password, response);
	printf("%s\n", response);

	return 0;
}
