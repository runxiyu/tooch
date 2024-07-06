.PHONY: all sjauth memch chphoto

all: sjauth memch chphoto

sjauth:
	$(MAKE) -C sjauth

memch:
	$(MAKE) -C memch

chphoto:
	$(MAKE) -C chphoto
