.PHONY: all install sjauth memch chphoto ykpsmuttauth clean uninstall pdfutils

all: sjauth memch chphoto ykpsmuttauth pdfutils

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

pdfutils:
	mkdir -p bin/
	install -c -m 755 pdfutils/* bin/

install: all
	mkdir -p $${HOME}/.local/bin/
	install -c -m 755 bin/* $${HOME}/.local/bin/

clean:
	$(MAKE) -C sjauth clean
	$(MAKE) -C memch clean
	$(MAKE) -C chphoto clean
	$(MAKE) -C ykpsmuttauth clean
	rm -f bin/*

uninstall:
	rm -f $${HOME}/.local/bin/sjauth $${HOME}/.local/bin/memch $${HOME}/.local/bin/chphoto $${HOME}/.local/bin/ykpsmuttauth $${HOME}/.local/bin/fixpdf $${HOME}/.local/bin/html2pdf $${HOME}/.local/bin/pdf2djvu $${HOME}/.local/bin/pdfclean

