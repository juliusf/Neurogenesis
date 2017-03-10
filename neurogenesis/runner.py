from neurogenesis.util import Logger, PrintColors
from neurogenesis.cluster import Cluster, TaskQueue
import sys
from subprocess import call

import os

def run_simulation(path_to_execute_binary, path_to_hosts_file, nr_ranks, simulations):
    from mpi4py import MPI
    #file = "/tmp/distsim_sims.list"
    #write_list_of_sims(file, simulations)
    #command = "/usr/bin/mpirun -np " + str(nr_ranks) + " --hostfile " + path_to_hosts_file + " " + path_to_execute_binary + " " + file
    #call(command, shell=True)
    mpi_info = MPI.Info.Create()
    mpi_info.Set("hostfile", path_to_hosts_file)
    comm = MPI.COMM_WORLD.Spawn(sys.executable,
                               args=[path_to_execute_binary],
                               maxprocs=nr_ranks-1,
                               info=mpi_info).Merge()

    comm.Barrier()
    print(nr_ranks)
    print("Current master rank: " + str(comm.Get_rank()))
    print("number of ranks: " + str(comm.Get_size()))
    queue = TaskQueue(simulations)
    cluster = Cluster(comm)
    cluster.schedule(queue)
    cluster.wait_and_reschedule(queue)
    cluster.synchronize()
    cluster.kill_workers()
    Logger.printColor(PrintColors.OKGREEN, "simulation successful")
    #comm.Disconnect()


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
    
