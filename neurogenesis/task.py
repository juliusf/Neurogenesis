import luigi
from neurogenesis.features import distsim_simulate

class RunSimulationTask(luigi.Task):
    args = luigi.DictParameter(significant=False)
    task_namespace = 'simulation_run'
    def run(self):
        distsim_simulate(self.args)
    def requires(self):
        return []

    def output(self):
        return []
