all: UTF-8-PATCHED en_US.UTF-8-PATCHED.src

clean:
	rm -f *.src UTF-8 UTF-8-PATCHED

UTF-8:
	curl -s -o $@ 'https://sourceware.org/git/?p=glibc.git;a=blob_plain;f=localedata/charmaps/UTF-8;hb=HEAD'

UTF-8-PATCHED: UTF-8 update_charmap.py config.py
	python3 update_charmap.py $< > $@

en_US.UTF-8.src:
	curl -s -o $@ https://raw.githubusercontent.com/openbsd/src/master/share/locale/ctype/$@

en_US.UTF-8-PATCHED.src: en_US.UTF-8.src update_ctype.py config.py
# In Mac, "UTF8" is an invalid encoding.
	python3 update_ctype.py $< | sed -E 's|^(ENCODING\s+)"UTF8"|\1"UTF-8"|' > $@

.PHONY: all clean
