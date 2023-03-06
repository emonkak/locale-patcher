CC ?= gcc
CFLAGS ?= -O2 -march=native -pipe -std=c99 -Wall

CFLAGS += -I/usr/include/freetype2
LDFLAGS += -lfreetype

UNICODE_VERSION=14.0.0

all: UTF-8-CJK UTF-8-CJK.src

clean:
	rm -f *.txt UTF-8 UTF-8-CJK

UTF-8: unicode_utils.py utf8_gen.py
	utf8_gen.py --unicode_version $(UNICODE_VERSION)

UTF-8-CJK: UTF-8 UnicodeWidth.txt
	awk '/^WIDTH$$/{f=1} !f; /^END WIDTH$$/{f=0}' < UTF-8 > $@
	echo 'WIDTH' >> $@
	cat UnicodeWidth.txt >> $@
	echo 'END WIDTH' >> $@

UTF-8.src:
	curl -o $@ https://raw.githubusercontent.com/openbsd/src/master/share/locale/ctype/en_US.UTF-8.src

UTF-8-CJK.src: UTF-8.src utf8_ctype.py config.py
	python3 utf8_ctype.py $< | sed -E 's|^(ENCODING\s+)"UTF8"|\1"UTF-8"|' > $@

UnicodeWidth.txt: Blocks.txt EastAsianWidth.txt PropList.txt UnicodeData.txt unicode_width.py config.py
	python3 unicode_width.py > $@

EastAsianWidth.txt:
	curl -o $@  https://www.unicode.org/Public/$(UNICODE_VERSION)/ucd/$@

PropList.txt:
	curl -o $@  https://www.unicode.org/Public/$(UNICODE_VERSION)/ucd/$@

UnicodeData.txt:
	curl -o $@  https://www.unicode.org/Public/$(UNICODE_VERSION)/ucd/$@

Blocks.txt:
	curl -o $@  https://www.unicode.org/Public/$(UNICODE_VERSION)/ucd/$@

.PHONY: all clean
