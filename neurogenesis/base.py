import cPickle as pickle
import gc
import sys
from neurogenesis.util import Logger

class SimulationRun():
    def __init__(self):
        self.hash = ""
        self.config = []
        self.last_executed = 0
        self.path = ""
        self.executable_path = ""
        self.results = {}
        self.result_vectors = {}  # {('module', 'name'): [(event, simSec, value), ...], ...}
        self.parameters = {}
        self.execute_binary = ""
        self.last_exit_code = -1
        self.last_executed_on_rank = -1
        self.last_run_at = 0
        self.config_name = ""

class Simulation():
        def __init__(self):
            self.simulation_runs = {}
            self.name = ""
            self.last_executed = ""
            self.total_duration = -1
            self.total_non_zero_exit_codes = -1

def serialize_sim_data(simName, simulations):
    file = open(simName, "wb+")
    gc.disable()
    pickle.dump(simulations, file, protocol=pickle.HIGHEST_PROTOCOL)
    gc.enable()
    file.close()


def deserialize_sim_data(path):
    print(path)
    file = open(path, "rb")
    gc.disable()
    sim_data = pickle.load(file)
    gc.enable()
    file.close()
    if isinstance(sim_data, dict):
        Logger.error("It seems that your .meta.pickle file has been created with an old version of distsim. Please rerun your simulation!")
        sys.exit(-1)
    return sim_data
