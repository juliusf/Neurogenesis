from neurogenesis.util import Logger, PrintColors
import sys

import datetime
import os

def run_simulation(path_to_execute_binary, path_to_hosts_file, nr_ranks, sim):
    from mpi4py import MPI
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
    queue = TaskQueue(sim.simulation_runs)
    cluster = Cluster(comm)
    cluster.schedule(queue)
    cluster.wait_and_reschedule(queue)
    cluster.synchronize(queue)
    cluster.kill_workers()
    duration = datetime.datetime.now() - start_time
    Logger.printColor(PrintColors.OKGREEN, "simulation successful. Duration: %s" % (duration))

    sim.simulation_run = queue.get_completed_tasks()

    non_zero_exit_codes = 0
    for sim_run in sim.simulation_run.values():
        sim_run.last_run_at = start_time
        if sim_run.last_exit_code != 0:
            non_zero_exit_codes += 1

    sim.total_duration = duration
    sim.total_non_zero_exit_codes = non_zero_exit_codes

    return sim


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

