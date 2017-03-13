import itertools
import hashlib
import os
import stat
from neurogenesis.base import SimulationRun
from neurogenesis.util import Logger

class DynamicLine(): # TODO better name?
    def __init__(self):
        self.head_part = ""
        self.dynamic_part = ""
        self.tail_part = ""
        self.current_print_representation = ""
        self.parameter_representation = {}

    def get_current_value_tuple(self):
        return (self.head_part, self.current_print_representation, self.tail_part)
    def __str__(self):
        return self.head_part + self.current_print_representation + self.tail_part
    def __repr__(self):
        return self.__str__()

def demux_and_write_simulation(ini_file, out_dir, inet_dir, additional_files, omnet_exec):
    lines = []
    dynamic_lines = []
    simulation_runs = {}
    with open(ini_file) as input_file:
        for row in input_file:
            if '{' in row.split('#')[0]: # ignore comments (T)
                line = create_dynamic_line(row)
                dynamic_lines.append(line)
                lines.append(line)
            else:
                lines.append(row)

    all_dynamic_lines = [line.dynamic_part for line in dynamic_lines]
    for perm in itertools.product(*all_dynamic_lines):
        run = SimulationRun()
        for idx, val in enumerate(perm):
            dynamic_lines[idx].current_print_representation = val
            run.parameters.append((dynamic_lines[idx].head_part.split()[0], val.strip()))
        hash = create_file_hash(lines)
        target_file = "run.sh"
        write_sim_data(omnet_exec, inet_dir, out_dir, lines, hash, additional_files, target_file)
        run.hash = hash
        [run.config.append(line.get_current_value_tuple()) for line in dynamic_lines]
        run.path = out_dir + hash + "/"
        run.executable_path = out_dir + hash + "/" + target_file
        simulation_runs[hash] = run
    Logger.info("Generated %s simulation configs." % (len(simulation_runs)))
    return simulation_runs

def write_sim_data(omnet_exec, inet_dir, folder_path, lines, hash, additional_files, target_file):

    full_folder_path = check_and_create_folder(folder_path, hash)
    write_ini(full_folder_path, lines)
    create_bash_script(full_folder_path, omnet_exec, inet_dir, target_file)
    write_additional_files(full_folder_path, additional_files)

def create_file_hash(lines):
    hash = hashlib.md5()
    [hash.update(str(line).encode('utf-8')) for line in lines]
    return hash.hexdigest()

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

def create_bash_script(target_folder, omnet_exec, inet_dir, target_file):
    script = """
    #!/bin/bash
    DIR=%s
    TARGET=%s
    cd $DIR
    %s -G -u Cmdenv -l $DIR/INET -n  $DIR/inet:$DIR/../tutorials:$DIR/../examples:$DIR/../examples:$TARGET/ $TARGET/omnetpp.ini > /dev/null
    rc=$?
    if [ $rc -gt 0 ]; then
        echo There is something wrong! omnet exited with non 0 exit code!
        exit $rc
    fi
    """ % (inet_dir[:-1], target_folder, omnet_exec)
    full_path = target_folder + target_file
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
