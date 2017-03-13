import cPickle as pickle

import gc


class SimulationRun():
    def __init__(self):
        self.hash = ""
        self.config = []
        self.last_executed = 0
        self.path = ""
        self.results = {}
        self.result_vectors = {}  # {('module', 'name'): [(event, simSec, value), ...], ...}
        self.parameters = []
        self.execute_binary = ""
        self.last_exit_code = -1
        self.last_executed_on_rank = -1
        self.last_run_at = 0


def serialize_sim_data(simName, simulations):
    file = open(simName, "wb+")
    gc.disable()
    pickle.dump(simulations, file, protocol=pickle.HIGHEST_PROTOCOL)
    gc.enable()
    file.close()


def deserialize_sim_data(path):
    file = open(path, "rb")
    gc.disable()
    sim_data = pickle.load(file)
    gc.enable()
    file.close()
    return sim_data
