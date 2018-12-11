.PHONY: all
all: bottisota/gui/sprites.py
	python3 setup.py build

bottisota/gui/sprites.py: sprites.qrc sprites/*.png
	pyrcc5 $< -o $@

.PHONY: installuser
installuser: all
	python3 setup.py install --user

.PHONY: install
install: all
	python3 setup.py install

.PHONY: clean
clean:
	rm -rf build
	rm -f bottisota/gui/sprites.py
