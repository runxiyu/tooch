.PHONY: all clean

all: sjauth

sjauth: sjauth.c
	$(CC) -Wall -Wextra -pedantic -O3 -o sjauth sjauth.c $(shell pkg-config --libs libcurl) 

clean:
	rm sjauth
