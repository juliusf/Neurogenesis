from neurogenesis.util import Logger
from mpi4py import MPI


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

class MPITags:
    DIE = 1
    WORK = 2
    FEEDBACK = 3

class Cluster():
    comm = MPI.COMM_WORLD
    MASTER_CONTROLLER = 0

    def __init__(self):
        self.master_controller = self.MASTER_CONTROLLER
        self.nr_ranks = self.comm.Get_size()
        self.active_ranks = []

    def schedule(self, queue):
        for i in range(self.master_controller + 1, self.nr_ranks):
            if queue.has_next():
                task = queue.get_next()
                Logger.info(" %s/%s: sent job %s to rank %s" % (queue.get_job_nr(), queue.num_tasks, task.hash, i))
                self.comm.send(task, dest=i, tag=MPITags.WORK)
                self.active_ranks.append(i)

    def wait_and_reschedule(self, queue):
        while (queue.has_next()):
            reception_status = MPI.Status()
            exit_code = self.comm.recv(source=MPI.ANY_SOURCE, tag=MPITags.FEEDBACK, status=reception_status)
            Logger.info("Received exit code %s from rank %s" % (exit_code, reception_status.source))

            task = queue.get_next()
            Logger.info(" %s/%s: sent job %s to rank %s" % (
            queue.get_job_nr(), queue.num_tasks, task.hash, reception_status.source))
            self.comm.send(task, dest=reception_status.source, tag=MPITags.WORK)

    def synchronize(self):
        while len(self.active_ranks) > 0:
            reception_status = MPI.Status()
            exit_code = self.comm.recv(source=MPI.ANY_SOURCE, tag=MPITags.FEEDBACK, status=reception_status)
            self.active_ranks.remove(reception_status.source)
            Logger.info("Received exit code %s from rank %s" % (exit_code, reception_status.source))

    def kill_workers(self):
        for i in range(1, self.nr_ranks):
            self.comm.send(0, dest=i, tag=MPITags.DIE)

