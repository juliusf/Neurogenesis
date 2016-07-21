#!/usr/bin/env python

import argparse
import itertools
import random
import string
import os.path
import hashlib
import os
import stat


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
    arg_parser.add_argument("--inetdir", help='location of the inet executable on NFS share'
                            )
    args = arg_parser.parse_args()
    if args.outdir is None:
        folder_path = "/tmp/distSim/simulations/"
    else:
        folder_path = args.outdir

    if args.inetdir is None:
        inet_dir = "/tmp/distSim/inet/src/"
    else:
        inet_dir = args.inetdir

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
        write_sim_data(inet_dir, folder_path, lines)

    print (all_dynamic_lines)

def write_sim_data(inet_dir, folder_path, lines):
    hash = hashlib.md5()
    [hash.update(str(line).encode('utf-8')) for line in lines]
    full_folder_path = check_and_create_folder(folder_path, hash.hexdigest())
    write_ini(full_folder_path, lines)
    create_bash_script(full_folder_path, inet_dir)

def write_ini(folder_path, file):
    full_path = folder_path + "/omnetpp.ini"
    if os.path.exists(full_path):
        os.remove(full_path)
    f = open (full_path, "a")
    for line in file:
        f.write(str(line))
    f.close()

def check_and_create_folder(base_path, folder_name):
    full_path = base_path + folder_name
    if not os.path.exists(full_path):
        os.makedirs(full_path)
    return full_path


def create_bash_script(target_folder, inet_dir):
    script = """
    #!/bin/bash
    cd %s
    .%srun_inet

    """ % (target_folder, inet_dir)
    full_path = target_folder + "/run.sh"
    if os.path.exists(full_path):
        os.remove(full_path)
    f = open (full_path, "a")
    f.write(script)
    f.close()
    file_handle = os.stat(full_path)
    os.chmod(full_path, file_handle.st_mode | stat.S_IEXEC)

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
