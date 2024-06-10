.PHONY: all

all: sjauth

sjauth: sjauth.c
	$(CC) -O3 $(shell pkg-config --libs libcurl) -o sjauth sjauth.c
