//go:build exclude

/*
 * Copyright (c) 2024 Runxi Yu <https://runxiyu.org>
 * SPDX-License-Identifier: BSD-2-Clause
 *
 * Key inspiration was taken from mutt_oauth2.py written by Alexander Perlis,
 * licensed under the GNU General Public License, version 2 or later, as
 * published by the Free Software Foundation. I don't think that this program
 * is a derivative work of mutt_oauth2.py in terms of GPL interpretation, but I
 * might be wrong.  Consult your lawyer if you want to use this program in a
 * context incompatible with the GPL.
 * https://raw.githubusercontent.com/muttmua/mutt/master/contrib/mutt_oauth2.py
 *
 * This C implementation does not support authorizing a new token, but it does
 * support refreshing tokens.
 * It isn't compatible with the Go implementation because of awkward timezone
 * handling in both. This should be fixed later.
 */

#define _XOPEN_SOURCE 600

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <time.h>
#include <curl/curl.h>
#include <sys/stat.h>
#include <openssl/rand.h>
#include <openssl/sha.h>
#include <json-c/json.h>

#define TOKENENDPOINT "https://login.microsoftonline.com/ddd3d26c-b197-4d00-a32d-1ffd84c0c295/oauth2/v2.0/token"
#define TENANT "ddd3d26c-b197-4d00-a32d-1ffd84c0c295"
#define SCOPE "offline_access https://outlook.office.com/IMAP.AccessAsUser.All https://outlook.office.com/SMTP.Send"
#define CLIENTID "fea760d5-b496-4f63-be1e-93855c1c5f78"

struct token_t {
	char *access_token;
	char *access_token_expiration;
	char *refresh_token;
	char *email;
};

struct token_t token;
char *token_file;

int read_token_file(const char *filename)
{
	struct stat st;
	if (stat(filename, &st) != 0) {
		fprintf(stderr, "stat(): %s\n", strerror(errno));
		return -1;
	}

	off_t length = st.st_size;

	FILE *file = fopen(filename, "r");
	if (!file) {
		fprintf(stderr, "fopen(): %s\n", strerror(errno));
		return -1;
	}

	char *data = malloc(length);
	if (!data) {
		fprintf(stderr, "malloc(): %s\n", strerror(errno));
		fclose(file);
		return -1;
	}

	fread(data, 1, length, file);
	fclose(file);

	struct json_object *parsed_json;
	parsed_json = json_tokener_parse(data);
	free(data);
	if (!parsed_json) {
		fprintf(stderr, "json_tokener_parse() failed\n");
		return -1;
	}

	struct json_object *access_token_obj;
	struct json_object *access_token_expiration_obj;
	struct json_object *refresh_token_obj;
	struct json_object *email_obj;

	json_object_object_get_ex(parsed_json, "access_token",
				  &access_token_obj);
	json_object_object_get_ex(parsed_json, "access_token_expiration",
				  &access_token_expiration_obj);
	json_object_object_get_ex(parsed_json, "refresh_token",
				  &refresh_token_obj);
	json_object_object_get_ex(parsed_json, "email", &email_obj);

	token.access_token = strdup(json_object_get_string(access_token_obj));
	token.access_token_expiration =
	    strdup(json_object_get_string(access_token_expiration_obj));
	token.refresh_token = strdup(json_object_get_string(refresh_token_obj));
	token.email = strdup(json_object_get_string(email_obj));

	json_object_put(parsed_json);
	return 0;
}

int write_token_file(const char *filename)
{
	struct json_object *token_json = json_object_new_object();
	json_object_object_add(token_json, "access_token",
			       json_object_new_string(token.access_token));
	json_object_object_add(token_json, "access_token_expiration",
			       json_object_new_string
			       (token.access_token_expiration));
	json_object_object_add(token_json, "refresh_token",
			       json_object_new_string(token.refresh_token));
	json_object_object_add(token_json, "email",
			       json_object_new_string(token.email));

	const char *data = json_object_to_json_string(token_json);

	FILE *file = fopen(filename, "w");
	if (!file) {
		fprintf(stderr, "fopen(): %s\n", strerror(errno));
		json_object_put(token_json);
		return -1;
	}
	fputs(data, file);
	fclose(file);
	json_object_put(token_json);
	return 0;
}

int access_token_valid()
{
	if (!token.access_token_expiration) {
		fprintf(stderr, "token.access_token_expiration NULL???\n");
		return 0;
	}
	struct tm tm;
	memset(&tm, 0, sizeof(struct tm));
	if (!strptime
	    (token.access_token_expiration, "%Y-%m-%dT%H:%M:%S%z", &tm)) {
		fprintf(stderr, "strptime() failed\n");
		return 0;
	}
	time_t expiration_time = mktime(&tm) - timezone;
	time_t current_time = time(NULL);
	return difftime(expiration_time, current_time) > 0;
}

int update_tokens(struct json_object *response)
{
	struct json_object *access_token_obj;
	struct json_object *expires_in_obj;
	struct json_object *refresh_token_obj;

	json_object_object_get_ex(response, "access_token", &access_token_obj);
	json_object_object_get_ex(response, "expires_in", &expires_in_obj);
	if (json_object_object_get_ex
	    (response, "refresh_token", &refresh_token_obj)) {
		free(token.refresh_token);
		token.refresh_token =
		    strdup(json_object_get_string(refresh_token_obj));
	}

	free(token.access_token);
	token.access_token = strdup(json_object_get_string(access_token_obj));
	int expires_in = json_object_get_int(expires_in_obj);
	time_t expiration_time = time(NULL) + expires_in;
	struct tm *tm = gmtime(&expiration_time);
	char expiration_str[30];
	strftime(expiration_str, sizeof(expiration_str), "%Y-%m-%dT%H:%M:%S%z",
		 tm);
	free(token.access_token_expiration);
	token.access_token_expiration = strdup(expiration_str);

	return write_token_file(token_file);
}

struct memory {
	char *response;
	size_t size;
};

size_t write_callback(void *contents, size_t size, size_t nmemb, void *userp)
{
	size_t realsize = size * nmemb;
	struct memory *mem = (struct memory *)userp;

	char *ptr = realloc(mem->response, mem->size + realsize + 1);
	if (ptr == NULL) {
		fprintf(stderr, "OOM\n");
		return 0;
	}

	mem->response = ptr;
	memcpy(&(mem->response[mem->size]), contents, realsize);
	mem->size += realsize;
	mem->response[mem->size] = 0;

	return realsize;
}

int refresh_token()
{
	if (!token.refresh_token) {
		fprintf(stderr, "token.refresh_token == NULL???\n");
		return -1;
	}

	CURL *curl;
	CURLcode res;
	struct json_object *response = NULL;
	struct memory chunk = { 0 };

	curl = curl_easy_init();
	if (!curl) {
		fprintf(stderr, "curl_easy_init() failed\n");
		return -1;
	}

	int post_fields_size;
	char *post_fields;
	if (!(post_fields = malloc(post_fields_size = snprintf(NULL, 0,
							       "client_id=%s&tenant=%s&refresh_token=%s&grant_type=refresh_token",
							       CLIENTID, TENANT,
							       token.refresh_token) + 1)))
	{
		fprintf(stderr, "malloc(): %s\n", strerror(errno));
		return -1;
	}

	// FIXME: URL escaping is probably warranted here.
	if (snprintf(post_fields, post_fields_size,
		     "client_id=%s&tenant=%s&refresh_token=%s&grant_type=refresh_token",
		     CLIENTID, TENANT,
		     token.refresh_token) >= post_fields_size) {
		fprintf(stderr,
			"post_fields overflow which should be impossible\n");
		return -1;
	}

	curl_easy_setopt(curl, CURLOPT_URL, TOKENENDPOINT);
	curl_easy_setopt(curl, CURLOPT_POSTFIELDS, post_fields);
	curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_callback);
	curl_easy_setopt(curl, CURLOPT_WRITEDATA, (void *)&chunk);

	res = curl_easy_perform(curl);
	if (res != CURLE_OK) {
		fprintf(stderr, "curl_easy_perform(): %s\n",
			curl_easy_strerror(res));
		curl_easy_cleanup(curl);
		if (chunk.response)
			free(chunk.response);
		return -1;
	}

	long http_code = 0;
	curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &http_code);
	if (http_code != 200) {
		fprintf(stderr, "HTTP %ld\n", http_code);
		fprintf(stderr, "REQUEST: %s\n", post_fields);
		curl_easy_cleanup(curl);
		if (chunk.response) {
			fprintf(stderr, "RESPONSE: %s\n", chunk.response);
			free(chunk.response);
		}
		return -1;
	}

	free(post_fields);

	response = json_tokener_parse(chunk.response);
	if (!response) {
		fprintf(stderr, "json_tokener_parse() failed\n");
		curl_easy_cleanup(curl);
		if (chunk.response)
			free(chunk.response);
		return -1;
	}

	if (json_object_object_get_ex(response, "error", NULL)) {
		fprintf(stderr,
			"Error in token refresh response (why is it returning 200 then?)\n");
		json_object_put(response);
		curl_easy_cleanup(curl);
		if (chunk.response)
			free(chunk.response);
		return -1;
	}

	int result = update_tokens(response);
	json_object_put(response);
	curl_easy_cleanup(curl);
	if (chunk.response)
		free(chunk.response);

	if (!access_token_valid()) {
		fprintf(stderr,
			"Access token is still invalid after refreshing, something has gone horribly wrong\n");
		return -1;
	}

	return result;
}

int main(int argc, char *argv[])
{
	if (argc != 2) {
		fprintf(stderr, "Token file path as first argument please\n");
		return 1;
	}

	token_file = argv[1];
	fprintf(stderr, "Token file: %s\n", token_file);

	if (read_token_file(token_file) != 0) {
		fprintf(stderr, "read_token_file(): %s\n", strerror(errno));
		return 1;
	}
	fprintf(stderr, "Read token file\n");

	if (!access_token_valid()) {
		fprintf(stderr, "Access token expired, refreshing token\n");
		if (refresh_token() != 0) {
			fprintf(stderr, "refresh_token() failed\n");
			return 1;
		}
	}

	printf("%s\n", token.access_token);
	return 0;
}
