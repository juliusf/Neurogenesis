from neurogenesis.util import Logger
from mpi4py import MPI


class TaskQueue():
    def __init__(self, simulations):
        self.num_tasks = len(simulations.values())
        self.tasks = list(simulations.values())
        self.next_sim = 0
        self.completed_tasks = {}

    def has_next(self):
        return self.next_sim < self.num_tasks

    def get_next(self):
        ret = self.tasks[self.next_sim]
        self.next_sim += 1
        return ret

    def get_job_nr(self):
        return self.next_sim

    def set_task_complete(self, task):
        key = task.hash
        self.completed_tasks[key] = task

    def get_completed_tasks(self):
        return self.completed_tasks

class MPITags:
    DIE = 1
    WORK = 2
    FEEDBACK = 3

class Cluster():
    MASTER_CONTROLLER = 0

    def __init__(self, comm):
        self.master_controller = self.MASTER_CONTROLLER
        self.nr_ranks = comm.Get_size() -1
        self.active_ranks = []
        self.comm = comm

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
            completed_task = self.comm.recv(source=MPI.ANY_SOURCE, tag=MPITags.FEEDBACK, status=reception_status)
            self.check_exit_code(completed_task)
            queue.set_task_complete(completed_task)
            task = queue.get_next()
            Logger.info(" %s/%s: sent job %s to rank %s" % (
            queue.get_job_nr(), queue.num_tasks, task.hash, reception_status.source))
            self.comm.send(task, dest=reception_status.source, tag=MPITags.WORK)

    def synchronize(self, queue):
        while len(self.active_ranks) > 0:
            reception_status = MPI.Status()
            Logger.info("Waiting for active ranks to finish. Remaining active ranks: %s" % (len(self.active_ranks)))
            completed_task = self.comm.recv(source=MPI.ANY_SOURCE, tag=MPITags.FEEDBACK, status=reception_status)
            queue.set_task_complete(completed_task)
            self.active_ranks.remove(reception_status.source)
            self.check_exit_code(completed_task)

    def kill_workers(self):
        for i in range(1, self.nr_ranks):
            self.comm.send(0, dest=i, tag=MPITags.DIE)

    def check_exit_code(self, run):
        if run.last_exit_code != 0:
            Logger.warning("Task %s on node %s exited with non zero exit code!" % (run.hash, run.last_executed_on_rank))
        else:
            Logger.debug("Received exit code 0 from rank %s" % (run.last_executed_on_rank))
