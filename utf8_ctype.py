#!/bin/env python3

import argparse
import re

import config

def update_ctype(file):
    for line in file.readlines():
        match = re.match(r'^SWIDTH([12])\s+(.*)', line)
        if match is None:
            print(line.rstrip())
            continue
        width = int(match.group(1), 10)
        components = parse_swidth(match.group(2))

        for entry in config.OVERRIDE_WIDTH:
            overrides, components = extract_components(
                components,
                entry['code_start'],
                entry['code_end'],
            )
            if len(overrides) > 0:
                print(make_swidth(entry['width'], overrides))
            if len(components) == 0:
                continue

        if len(components) > 0:
            print(make_swidth(width, components))

def extract_components(components, code_start, code_end):
    overrides = []
    remainings = []

    for component in components:
        component_start, component_end = component

        if code_start <= component_end and code_end >= component_start:
            overrides.append((
                max(code_start, component_start),
                min(code_end, component_end))
            )
        else:
            remainings.append(component)
            continue

        if component_start < code_start:
            remainings.append((component_start, code_start - 1))

        if code_end < component_end:
            remainings.append((code_end + 1, component_end))

    return overrides, remainings

def parse_swidth(input):
    components = []

    for match in re.finditer(r'0x([0-9a-z]+)(?:\s+-\s+0x([0-9a-z]+))?', input):
        [start_component, end_component] = match.groups()
        if end_component:
            code_start = int(start_component, 16)
            code_end = int(end_component, 16)
            components.append((code_start, code_end))
        else:
            code_point = int(start_component, 16)
            components.append((code_point, code_point))

    return components

def make_swidth(width, components):
    notation = f'SWIDTH{width:d} '
    for component in components:
        code_start, code_end = component
        if code_start == code_end:
            notation += f'  0x{code_start:04x}'
        else:
            notation += f'  0x{code_start:04x} - 0x{code_end:04x}'

    return notation

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description = '''
        Update to optimize UTF-8.src file for CJK users.
        ''')
    parser.add_argument(
        'ctype_file',
        nargs = '?',
        type = str,
        default = 'UTF-8.src',
        help = ('The UTF-8.src file to read, default: %(default)s')
    )
    args = parser.parse_args()

    with open(args.ctype_file, mode = 'r') as file:
        update_ctype(file)
