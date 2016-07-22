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
    arg_parser.add_argument("--inetdir", help='location of the inet executable on NFS share')
    arg_parser.add_argument("--additionalFiles", nargs="+", help="additional Files which should be copied to the output dirs")
    args = arg_parser.parse_args()

    if args.outdir is None:
        folder_path = "/tmp/distSim/simulations/"
    else:
        folder_path = args.outdir

    if args.inetdir is None:
        inet_dir = "/tmp/distSim/inet/src/"
    else:
        inet_dir = args.inetdir

    additional_files = []

    if args.additionalFiles is not None:
        for file in args.additionalFiles:
            additional_files.append(file)

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
        write_sim_data(inet_dir, folder_path, lines, additional_files)

    print ("file creation successfull")

def write_sim_data(inet_dir, folder_path, lines, additional_files):
    hash = hashlib.md5()
    [hash.update(str(line).encode('utf-8')) for line in lines]
    full_folder_path = check_and_create_folder(folder_path, hash.hexdigest())
    write_ini(full_folder_path, lines)
    create_bash_script(full_folder_path, inet_dir)
    write_additional_files(full_folder_path, additional_files)

def write_additional_files(folder_path, files):
    for file in files:
        base_name = os.path.basename(file)
        new_file_path = folder_path + '/'+ base_name
        f = check_and_create_file(new_file_path)
        with open(file) as input_file:
            for row in input_file:
                f.write(row)
            f.close()
        input_file.close()



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

def check_and_create_file(full_path):
    if os.path.exists(full_path):
        os.remove(full_path)
    f = open (full_path, "a")
    return f

def create_bash_script(target_folder, inet_dir):
    script = """
    #!/bin/bash
    DIR=%s
    TARGET=%s
    /home/jules/dev/omnetpp-5.0/bin/opp_run -u Cmdenv -l $DIR/INET -n  $DIR/../tutorials:$DIR/../examples:$DIR/:$DIR/../examples/ $TARGET/omnetpp.ini
    """ % (inet_dir[:-1], target_folder)
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
