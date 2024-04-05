#!/usr/bin/env python3

import argparse
import re
import sys

import config

def update_charmap(file):
    # skip lines until the start for WIDTH.
    for line in file:
        print(line, end = '')
        if line == 'WIDTH\n':
            break

    widths = {}

    for line in file:
        if line == 'END WIDTH\n':
            break

        components = re.split(r'\s+', line.rstrip())
        if len(components) != 2:
            continue

        code_points = list(map(
            lambda s: int(s.lstrip('<U0').rstrip('>'), 16),
            components[0].split('...')
        ))
        width = int(components[1], 10)

        if len(code_points) == 1:
            widths[code_points[0]] = width
        elif len(code_points) == 2:
            for code_point in range(code_points[0], code_points[1] + 1):
                widths[code_point] = width

    for entry in config.OVERRIDE_WIDTHS:
        for code_point in range(entry['code_start'], entry['code_end'] + 1):
            widths[code_point] = entry['width']

    last_code_start = 0
    last_code_end = 0
    last_width = -1

    for code_point in sorted(widths):
        width = widths[code_point]

        if last_width == width and last_code_end + 1 == code_point:
            last_code_end = code_point
            continue

        if last_width >= 0 and last_width != 1:
            print(make_width_entry(
                last_code_start,
                last_code_end,
                last_width,
            ))

        last_code_start = code_point
        last_code_end = code_point
        last_width = width

    if last_width >= 0 and last_width != 1:
        print(make_width_entry(
            last_code_start,
            last_code_end,
            last_width,
        ))

    print('END WIDTH')

def make_width_entry(code_start, code_end, width):
    if code_start == code_end:
        return ucs_symbol(code_start) + '\t' + str(width)
    else:
        return ucs_symbol(code_start) + '...' + ucs_symbol(code_end) + '\t' + str(width)

def ucs_symbol(code_point):
    if code_point < 0x10000:
        return f'<U{code_point:04X}>'
    else:
        return f'<U{code_point:08X}>'

parser = argparse.ArgumentParser(
    description = 'Update character widths in charmap for glib based on your own config.'
)
parser.add_argument(
    'charmap_file',
    nargs = '?',
    help = 'a path of the original charmap file to patch (default: stdin)',
    type = str,
)
args = parser.parse_args()

if args.charmap_file:
    with open(args.charmap_file, mode = 'r') as file:
        update_charmap(file)
else:
    update_charmap(sys.stdin)
