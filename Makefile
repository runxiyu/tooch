.PHONY: all

all: sjauth

sjauth: sjauth.c
	$(CC) $(shell pkg-config --libs libcurl) -o sjauth sjauth.c
