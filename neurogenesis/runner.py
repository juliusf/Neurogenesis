from neurogenesis.util import Logger
from subprocess import call
import os

def run_simulation(path_to_execute_binary, path_to_hosts_file, nr_ranks, simulations):
    file = "/tmp/distsim_sims.list"
    write_list_of_sims(file, simulations)
    command = "/usr/bin/mpirun -np " + str(nr_ranks) + " --hostfile " + path_to_hosts_file + " " + path_to_execute_binary + " " + file
    call(command, shell=True)


def write_list_of_sims(file, simulations):
    try:
        os.remove(file)
    except OSError:
        pass
    f = open(file, "w+")
    for hash in simulations.keys():
        f.write(hash + "\n")
    f.close()
    Logger.info("Passed %s simulations to MPI runner." % (len(simulations.keys())))
    
