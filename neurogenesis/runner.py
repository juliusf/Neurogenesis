
from subprocess import call

def run_simulation(path_to_execute_binary, path_to_hosts_file, nr_ranks, simulations):
    command = "mpirun -np " + nr_ranks + "--hostfile " + path_to_hosts_file + " " + path_to_execute_binary + " "
    for hash in simulations.keys():
        command += hash + " "
    call(command)