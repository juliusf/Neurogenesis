import sys
from mpi4py import MPI
from neurogenesis.util import Logger, PrintColors
from neurogenesis.cluster import MPITags, Cluster, TaskQueue


def main():
    if Cluster.comm.Get_rank() == Cluster.MASTER_CONTROLLER:
        master()
    else:
        slave()


def master():
    import argparse
    from neurogenesis.base import deserialize_sim_data

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--metafile", help="metafile of current simulation")

    args= arg_parser.parse_args()
    if args.metafile == None:
        Logger.error("No simulation file specified!")
        sys.exit(-1)
    try:
        simulation = deserialize_sim_data(args.metafile)
    except IOError:
        Logger.error("could not open simulation file %s!" % (args.metafile))
        sys.exit(-1)

    queue = TaskQueue(simulation)
    cluster = Cluster()
    cluster.schedule(queue)
    cluster.wait_and_reschedule(queue)
    cluster.synchronize()
    cluster.kill_workers()


def slave():
    while True:
        reception_status = MPI.Status()
        task = Cluster.comm.recv(source=0, tag=MPI.ANY_TAG, status=reception_status)
        # execute task
        if reception_status.Get_tag() == MPITags.WORK:
            return_value = 0
            Cluster.comm.send(return_value, Cluster.MASTER_CONTROLLER, MPITags.FEEDBACK)
        elif reception_status.Get_tag() == MPITags.DIE:
            Logger.debug("rank %s exiting" %  (Cluster.comm.Get_rank()))
            sys.exit(0)
        else:
            Logger.error("Unknown TAG received!")

if __name__ == '__main__':
        main()
