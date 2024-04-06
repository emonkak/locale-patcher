# Locale Patchers

This repository contains some small scripts for updating the character width table for the locale.

- **Makefile** - Download lastest charmap and ctype from glibc and OpenBSD repositories, and apply the patch to them.

    Example:

    ```console
    # Generate UTF-8-PATCHED and UTF-8-PATCHED.src
    $ make
    ```

- **config.py** - The Configuration for `update_charmap.py` and `update_ctype.py`.

    You can add entries, to override the character width, in this file.

    Default:

    ```python
    OVERRIDE_WIDTHS = [
        # General Punctuation (U+2000..U+206f)
        #
        # But, excluding following the code ranges:
        # - EN QUAD (U+2000) .. RIGHT-TO-LEFT MARK(U+200F)
        # - LINE SEPARATOR (U+2028) .. NARROW NO-BREAK SPACE(U+202F)
        # - MEDIUM MATHEMATICAL SPACE (U+205F) .. NOMINAL DIGIT SHAPES(U+206F)
        { 'code_start': 0x2010, 'code_end': 0x2027, 'width': 2 },
        { 'code_start': 0x2030, 'code_end': 0x205E, 'width': 2 },

        # Letterlike Symbols (U+2100..U+214F)
        # Number Forms (U+2150..U+218F)
        # Arrows (U+2190..U+21FF)
        # Mathematical Operators (U+2200..U+22FF)
        # Miscellaneous Technical (U+2300..U+23FF)
        { 'code_start': 0x2100, 'code_end': 0x23ff, 'width': 2 },

        # Enclosed Alphanumerics (U+2460..U+24FF)
        { 'code_start': 0x2460, 'code_end': 0x24ff, 'width': 2 },

        # Geometric Shapes (U+25A0..U+25FF)
        # Miscellaneous Symbols (U+2600..U+26FF)
        # Dingbats (U+2700..U+27BF)
        { 'code_start': 0x25a0, 'code_end': 0x27bf, 'width': 2 },

        # Miscellaneous Symbols and Arrows (U+2B00..U+2BFF)
        { 'code_start': 0x2b00, 'code_end': 0x2bff, 'width': 2 },

        # Enclosed CJK Letters and Months (U+3200..U+32FF)
        { 'code_start': 0x3200, 'code_end': 0x32ff, 'width': 2 },

        # Yijing Hexagram Symbols (U+4DC0..U+4DFF)
        { 'code_start': 0x4dc0, 'code_end': 0x4dff, 'width': 2 },

        # Private Use Area (U+E000..U+F8FF)
        { 'code_start': 0xe000, 'code_end': 0xf8ff, 'width': 2 },

        # OBJECT REPLACEMENT CHARACTER (U+FFFC)
        # REPLACEMENT CHARACTER (U+FFFD)
        { 'code_start': 0xfffc, 'code_end': 0xfffd, 'width': 2 },

        # Mahjong Tiles (U+1F000..U+1F02F)
        # Domino Tiles (U+1F030..U+1F09F)
        # Playing Cards (U+1F0A0..U+1F0FF)
        # Enclosed Alphanumeric Supplement (U+1F100..U+1F1FF)
        # Enclosed Ideographic Supplement (U+1F200..U+1F2FF)
        # Miscellaneous Symbols and Pictographs (U+1F300..U+1F5FF)
        # Emoticons (U+1F600..U+1F64F)
        # Ornamental Dingbats (U+1F650..U+1F67F)
        # Transport and Map Symbols (U+1F680..U+1F6FF)
        # Alchemical Symbols (U+1F700..U+1F77F)
        # Geometric Shapes Extended (U+1F780..U+1F7FF)
        # Supplemental Arrows-C (U+1F800..U+1F8FF)
        # Supplemental Symbols and Pictographs (U+1F900..U+1F9FF)
        # Chess Symbols (U+1FA00..U+1FA6F)
        # Symbols and Pictographs Extended-A (U+1FA70..U+1FAFF)
        # Symbols for Legacy Computing (U+1FB00..U+1FBFF)
        { 'code_start': 0x1f000, 'code_end': 0x1fbf9, 'width': 2 },

        # Supplementary Private Use Area-A (U+F0000..U+FFFFF)
        # Supplementary Private Use Area-B (U+100000..U+10FFFF)
        { 'code_start': 0xf0000, 'code_end': 0x10FFFD, 'width': 2 },
    ]
    ```

- **update_charmap.py** - Update character widths in charmap for glib based on your own config.

    Example:

    ```console
    $ zcat /usr/share/i18n/charmaps/UTF-8.gz | update_charmap.py > UTF-8-PATCHED
    ```

- **update_ctype.py** - Update character widths in ctype for BSD based on your own config.

    Example:

    ```console
    $ update_ctype.py /usr/src/share/locale/ctype/en_US.UTF-8.src > en_US.UTF-8-PATCHED.src
    ```

## Using a custom locale

To use a custom locale in Linux, follow this step:

```shell
sudo localedef -i en_US -c -f UTF-8-PATCHED en_US.UTF-8
```

Or overwrite the existing locale:

```shell
gzip -c UTF-8-PATCHED | sudo dd of=/usr/share/i18n/charmaps/UTF-8.gz
sudo sh -c 'cd / && locale-gen'
```

If you are using MacOS, follow these steps:

```shell
mkdir -p ~/.locale/UTF-8
mklocale -o ~/.locale/UTF-8/LC_CTYPE en_US.UTF-8-PATCHED.src
cat > ~/Library/LaunchAgents/setup-locale.plist <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>setup-locale</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/launchctl</string>
    <string>setenv</string>
    <string>PATH_LOCALE</string>
    <string>/Users/YOUR_USER_NAME/.locale</string>
  </array>
  <key>RunAtLoad</key>
  <true/>
</dict>
</plist>
EOF
launchctl load -w ~/Library/LaunchAgents/setup-locale.plist
```
