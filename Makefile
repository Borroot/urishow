SRC       = src/main.py src/tui.py
BUILD     = dist
PREFIX    = /usr/local

PYFLAGS   = --noconfirm --onefile --paths src

all: urishow

urishow: $(SRC)
	pyinstaller $(PYFLAGS) --name $@ $^

clean:
	rm -rf $(BUILD) build urishow.spec __init__.spec

install: all
	mkdir -p $(PREFIX)/bin
	cp -f $(BUILD)/urishow $(PREFIX)/bin
	chmod 755 $(PREFIX)/bin/urishow

uninstall:
	rm -f $(PREFIX)/bin/urishow

.PHONY: all clean install uninstall
