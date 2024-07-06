.PHONY: all install sjauth memch chphoto ykpsmuttauth

all: sjauth memch chphoto ykpsmuttauth

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

ykpsmuttauth:
	mkdir -p bin/
	$(MAKE) -C ykpsmuttauth
	install -c -m 755 ykpsmuttauth/ykpsmuttauth bin/

install: all
	mkdir -p $${HOME}/.local/bin/
	install -c -m 755 bin/sjauth bin/memch bin/chphoto bin/ykpsmuttauth $${HOME}/.local/bin/
