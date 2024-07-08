.PHONY: all clean

all: sjauth

sjauth: sjauth.c
	$(CC) -Wall -Wextra -pedantic -O3 $(shell pkg-config --libs libcurl) -o sjauth sjauth.c

clean:
	rm sjauth
