.PHONY: clean

ykpsmuttauth: ykpsmuttauth.go
	go build

ykpsmuttauth2: ykpsmuttauth2.c
	$(CC) -Wall -Wextra -pedantic -o ykpsmuttauth2 ykpsmuttauth2.c $(shell pkg-config --cflags --libs json-c) $(shell pkg-config --cflags --libs libcurl) $(shell pkg-config --cflags --libs openssl)

clean:
	rm -fv ykpsmuttauth ykpsmuttauth2
