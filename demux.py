#!/usr/bin/env python

import argparse
import itertools
import random
import string
import os.path
import hashlib

class DynamicLine(): # TODO better name?
    def __init__(self):
        self.head_part = ""
        self.dynamic_part = ""
        self.tail_part = ""
        self.current_print_representation = ""

    def __str__(self):
        return self.head_part + self.current_print_representation + self.tail_part
    def __repr__(self):
        return self.__str__()

def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("file", help=".ini file to be demuxed")
    arg_parser.add_argument("--outdir", help="specifies the location where files should be written to.")

    args = arg_parser.parse_args()
    if args.outdir is None:
        folder_path = "/tmp/"
    else:
        folder_path = args.outdir

    lines = []
    dynamic_lines = []
    with open(args.file) as input_file:
        for row in input_file:
            if '{' in row:
                line = create_dynamic_line(row)
                dynamic_lines.append(line)
                lines.append(line)
            else:
                lines.append(row)

    all_dynamic_lines = [line.dynamic_part for line in dynamic_lines]
    for perm in itertools.product(*all_dynamic_lines):
        for idx, val in enumerate(perm):
            dynamic_lines[idx].current_print_representation = val
        write_ini(folder_path, lines)

    print (all_dynamic_lines)

def write_ini(folderPath, file):
    hash = hashlib.sha1()
    
    filePath = id_generator() + '.ini'
   # while not os.path.isfile(folderPath + filePath):
   #     filePath = id_generator() + '.ini'
    f = open (folderPath + filePath, "a")
    for line in file:
        f.write(str(line))
    f.close()

def create_dynamic_line(line):
    dline = DynamicLine()
    head_tokens  = line.split('{')
    dline.head_part = head_tokens[0]
    tail_tokens = head_tokens[1].split('}')
    dline.dynamic_part = tail_tokens[0].split(',')
    dline.tail_part = tail_tokens[1]
    return dline

def id_generator():
    return ''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase) for _ in range(6))

if __name__ == '__main__':
    main()
