.PHONY: all install sjauth memch chphoto

all: sjauth memch chphoto

sjauth:
	$(MAKE) -C sjauth
	mkdir -p bin/
	install -c -m 755 sjauth/sjauth bin/

memch:
	mkdir -p bin/
	$(MAKE) -C memch
	install -c -m 755 memch/memch bin/

chphoto:
	mkdir -p bin/
	$(MAKE) -C chphoto
	install -c -m 755 chphoto/chphoto bin/

install: all
	mkdir -p $${HOME}/.local/bin/
	install -c -m 755 bin/sjauth bin/memch bin/chphoto $${HOME}/.local/bin/
