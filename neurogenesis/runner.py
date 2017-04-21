from neurogenesis.util import Logger, PrintColors
import sys

import datetime
import os

def run_simulation(path_to_execute_binary, path_to_hosts_file, nr_ranks, simulations):
    from neurogenesis.cluster import Cluster, TaskQueue

    start_time = datetime.datetime.now()
    mpi_info = MPI.Info.Create()
    #mpi_info.Set("hostfile", path_to_hosts_file)
    mpi_info.Set("add-hostfile", path_to_hosts_file)
    comm = MPI.COMM_WORLD.Spawn(sys.executable,
                               args=[path_to_execute_binary],
                               maxprocs=nr_ranks-1,
                               info=mpi_info).Merge()

    comm.Barrier()
    queue = TaskQueue(simulations)
    cluster = Cluster(comm)
    cluster.schedule(queue)
    cluster.wait_and_reschedule(queue)
    cluster.synchronize(queue)
    cluster.kill_workers()
    duration = datetime.datetime.now() - start_time
    Logger.printColor(PrintColors.OKGREEN, "simulation successful. Duration: %s" % (duration))

    simulation_run = queue.get_completed_tasks()

    for sim in simulation_run.values():
        sim.last_run_at = start_time
    return simulation_run


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

