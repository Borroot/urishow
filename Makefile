SRC_DIR   = src/urishow
SRC_FILES = src/urishow/main.py

PREFIX    = /usr/local
BUILD     = dist

PYFLAGS   = --noconfirm --onefile --paths $(SRC_DIR)

all: urishow

urishow: $(SRC_FILES)
	pyinstaller $(PYFLAGS) --name $@ $^

clean:
	rm -rf build dist $(TARGET).spec __init__.spec

install: all
	mkdir -p $(PREFIX)/bin
	cp -f $(BUILD)/urishow $(PREFIX)/bin
	chmod 755 $(PREFIX)/bin/urishow

uninstall:
	rm -f $(PREFIX)/bin/urishow

.PHONY: all clean install uninstall
