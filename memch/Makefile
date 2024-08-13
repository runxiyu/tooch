.PHONY: clean

memch: memch.c
	$(CC) -D_DEFAULT_SOURCE -std=c99 -o memch memch.c `pkg-config --libs --cflags ncursesw`

clean:
	rm -f memch
