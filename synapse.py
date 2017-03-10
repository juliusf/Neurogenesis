import sys
from mpi4py import MPI
from neurogenesis.util import Logger, PrintColors

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
MASTER_CONTROLLER = 0
WORKTAG = 1
DIETAG = 2
FEEDBACKTAG = 3

class TaskQueue():
    def __init__(self, simulations):
        self.num_tasks = len(simulations.values())
        self.tasks = simulations.values()
        self.next_sim = 0

    def has_next(self):
        return self.next_sim < self.num_tasks

    def get_next(self):
        ret = self.tasks[self.next_sim]
        self.next_sim += 1
        return ret

    def get_job_nr(self):
        return self.next_sim

class Cluster():
    def __init__(self, nr_ranks):
        self.nr_ranks = nr_ranks
        self.active_ranks = []


def main():
    if rank == MASTER_CONTROLLER:
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

    executed = 0
    #initial distribution of work
    for i in range(MASTER_CONTROLLER + 1, size):
        if queue.has_next():
            task = queue.get_next()
            Logger.info(" %s/%s: sent job %s to rank %s" %(queue.get_job_nr(), queue.num_tasks, task.hash, i))
            comm.send(task, dest=i, tag=WORKTAG)

    #distribute all jobs to workers
    while(queue.has_next()):
        reception_status = MPI.Status()
        exit_code = comm.recv(source=MPI.ANY_TAG, tag=FEEDBACKTAG, status=reception_status)
        Logger.info("Recieved exit code %s from rank %s" % (exit_code, reception_status.source))

        task = queue.get_next()
        Logger.info(" %s/%s: sent job %s to rank %s" % (queue.get_job_nr(), queue.num_tasks, task.hash, reception_status.source))
        comm.send(task, dest=reception_status.source, tag=WORKTAG)

    #collect final results and shutdown
    for i in range(MASTER_CONTROLLER + 1, size):
        reception_status = MPI.Status()
        exit_code = comm.recv(source=MPI.ANY_TAG, tag=FEEDBACKTAG, status=reception_status)
        Logger.info("Recieved exit code %s from rank %s" % (exit_code, reception_status.source))
        comm.send(0, dest=reception_status.source, tag=DIETAG)

def slave():
    while True:
        reception_status = MPI.Status()
        task = comm.recv(source=MASTER_CONTROLLER, tag=MPI.ANY_TAG, status=reception_status)
        if reception_status.Get_tag() == WORKTAG:
            #print(task)
            return_value = 0
            comm.send(return_value, MASTER_CONTROLLER, FEEDBACKTAG)
        elif reception_status.Get_tag() == DIETAG:
            sys.exit(0)
        else:
            Logger.error("Unknown TAG received!")

if __name__ == '__main__':
        main()
