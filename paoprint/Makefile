.SUFFIXES: .o .c

CFLAGS += -Wall -Wextra -pedantic -g

paoprint: main.o utils.o pwd.o base64.o
	$(CC) $(CFLAGS) -o paoprint main.o utils.o pwd.o base64.o

.c.o:
	$(CC) $(CFLAGS) -c -o $@ $<

# BUG: Headers should be included in dependencies too
