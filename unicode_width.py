#!/bin/env python3

import argparse
import re

import config

def generate_width_table(unicode_data_table, east_asian_width_table, prop_list_table):
    base_widths = {}

    for entry in east_asian_width_table:
        if re.match(r'.*<reserved-.+>\.\.<reserved-.+>.*', entry['comment']):
            continue
        if entry['category'] in ('W', 'F'):
            for code_point in range(entry['code_start'], entry['code_end'] + 1):
                base_widths[code_point] = 2

    for entry in unicode_data_table:
        if entry['bidirectional_category'] == 'NSM' or entry['general_category'] in ('Cf', 'Me', 'Mn'):
            base_widths[entry['code_value']] = 0

    for entry in prop_list_table:
        if entry['property'] == 'Prepended_Concatenation_Mark':
            for code_point in range(entry['code_start'], entry['code_end'] + 1):
                if code_point in base_widths:
                    base_widths[code_point] = 1

    for entry in config.OVERRIDE_WIDTH:
        for code_point in range(entry['code_start'], entry['code_end'] + 1):
            base_widths[code_point] = entry['width']

    results = []

    last_code_start = 0
    last_code_end = 0
    last_width = -1

    for code_point in sorted(base_widths):
        width = base_widths[code_point]

        if last_width == width and last_code_end + 1 == code_point:
            last_code_end = code_point
            continue

        if last_width >= 0:
            results.append({
                'code_start': last_code_start,
                'code_end': last_code_end,
                'width': last_width,
            })

        last_code_start = code_point
        last_code_end = code_point
        last_width = width

    if last_width >= 0:
        results.append({
            'code_start': last_code_start,
            'code_end': last_code_end,
            'width': last_width,
        })

    return results

def load_unicode_data(file):
    table = []
    for line in file.readlines():
        components = line.rstrip().split(';')
        table.append({
            'code_value': int(components[0], 16),
            'character_name': components[1],
            'general_category': components[2],
            'canonical_combining_classes': components[3],
            'bidirectional_category': components[4],
            'character_decomposition_mapping': components[5],
            'decimal_digit_value': int(components[6], 10) if components[6] else None,
            'digit_value': int(components[7], 10) if components[7] else None,
            'numeric_value': components[8],
            'mirrored': components[9],
            'unicode_1_0_name': components[10],
            'iso_10646_comment_field': components[11],
            'uppercase_mapping': int(components[12], 16) if components[12] else None,
            'lowercase_mapping': int(components[13], 16) if components[13] else None,
            'titlecase_mapping': int(components[14], 16) if components[14] else None,
        })
    return table

def load_east_asian_width(file):
    table = []
    for line in file.readlines():
        match = re.match(r'^([0-9A-Fa-f]{4,})(?:\.\.([0-9A-Fa-f]{4,}))?;(Na?|[WHFA])\s*#\s*(.*)', line)
        if match is None:
            continue
        start = match.group(1)
        end = match.group(2) or start
        category = match.group(3)
        comment = match.group(4)
        table.append({
            'code_start': int(start, 16),
            'code_end': int(end, 16),
            'category': category,
            'comment': comment,
        })
    return table

def load_prop_list(file):
    table = []
    for line in file.readlines():
        match = re.match(r'^([0-9A-Fa-f]{4,})(?:\.\.([0-9A-Fa-f]{4,}))?\s*?;\s*(\w+)', line)
        if match is None:
            continue
        start = match.group(1)
        end = match.group(2) or start
        property = match.group(3)
        table.append({
            'code_start': int(start, 16),
            'code_end': int(end, 16),
            'property': property,
        })
    table.sort(key = lambda element: element['code_start'])
    return table

def ucs_symbol(code_point):
    if code_point < 0x10000:
        return f'<U{code_point:04X}>'
    else:
        return f'<U{code_point:08X}>'

def search_entry_at_char_code(table, char_code):
    def f(entry, char_code):
        if entry['code_value'] > char_code:
            return -1
        if entry['code_value'] < char_code:
            return 1
        return 0

    return binary_search(table, char_code, f)

def binary_search(haystack, needle, f):
    left = 0;
    right = len(haystack) - 1;

    while left <= right:
        middle = left + ((right - left) >> 1);
        element = haystack[middle]
        ordering = f(element, needle)

        if ordering < 0:
            right = middle - 1
        elif ordering > 0:
            left = middle + 1
        else:
            return element

    return None;

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description = '''
        Generate a UTF-8 file from UnicodeData.txt, EastAsianWidth.txt, and PropList.txt.
        ''')
    parser.add_argument(
        '-u', '--unicode_data_file',
        nargs = '?',
        type = str,
        default = 'UnicodeData.txt',
        help = ('The UnicodeData.txt file to read, default: %(default)s')
    )
    parser.add_argument(
        '-e', '--east_asian_width_file',
        nargs = '?',
        type = str,
        default = 'EastAsianWidth.txt',
        help = ('The EastAsianWidth.txt file to read, default: %(default)s')
    )
    parser.add_argument(
        '-p', '--prop_list_file',
        nargs = '?',
        type = str,
        default = 'PropList.txt',
        help = ('The PropList.txt file to read, default: %(default)s')
    )
    args = parser.parse_args()

    with open(args.unicode_data_file, mode = 'r') as file:
        unicode_data_table = load_unicode_data(file)

    with open(args.east_asian_width_file, mode = 'r') as file:
        east_asian_width_table = load_east_asian_width(file)

    with open(args.prop_list_file, mode = 'r') as file:
        prop_list_table = load_prop_list(file)

    width_table = generate_width_table(
        unicode_data_table,
        east_asian_width_table,
        prop_list_table,
    )

    for entry in width_table:
        width = entry['width']

        if width == 1:
            continue

        start_symbol = ucs_symbol(entry['code_start'])
        end_symbol = ucs_symbol(entry['code_end'])

        if entry['code_start'] == entry['code_end']:
            print(f'{start_symbol}\t{width:d}')
        else:
            print(f'{start_symbol}...{end_symbol}\t{width:d}')
