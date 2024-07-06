.PHONY: all install sjauth memch chphoto ykmuttauth

all: sjauth memch chphoto ykmuttauth

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

ykmuttauth:
	mkdir -p bin/
	$(MAKE) -C ykmuttauth
	install -c -m 755 ykmuttauth/ykmuttauth bin/

install: all
	mkdir -p $${HOME}/.local/bin/
	install -c -m 755 bin/sjauth bin/memch bin/chphoto bin/ykmuttauth $${HOME}/.local/bin/
