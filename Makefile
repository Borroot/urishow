SRC_DIR   = src/urishow
SRC_FILES = $(wildcard $(SRC_DIR)/*.py)

PYFLAGS   = --noconfirm --onefile --paths $(SRC_DIR)
TARGET    = urishow

all: $(TARGET)

urishow: $(SRC_FILES)
	@echo "Building binaries for $@."
	@pyinstaller $(PYFLAGS) --name $@ $^

clean:
	rm -rf build dist $(TARGET).spec __init__.spec
	@pyclean

re:
	@$(MAKE) clean
	@$(MAKE)

.PHONY: all clean re
