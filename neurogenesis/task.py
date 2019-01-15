import luigi
from neurogenesis.features import distsim_simulate

class RunSimulationTask(luigi.Task):
    args = luigi.DictParameter(significant=False)
    task_namespace = 'simulation_run'
    completed = False
    result = None
    def run(self):
        self.result = distsim_simulate(self.args)
        self.completed = True
    def requires(self):
        return []

    def output(self):
        return []

    def complete(self):
        return self.completed
