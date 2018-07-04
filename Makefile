.PHONY: all
all: bottisota/gui/sprites.py

bottisota/gui/sprites.py: sprites.qrc sprites/*.png
	pyrcc5 $< -o $@

.PHONY: clean
clean:
	rm -f bottisota/gui/sprites.py
