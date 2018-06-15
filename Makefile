.PHONY: all
all: bottisota/sprites.py

bottisota/sprites.py: sprites.qrc sprites/*.png
	pyrcc5 $< -o $@

.PHONY: clean
clean:
	rm -f bottisota/sprites.py
