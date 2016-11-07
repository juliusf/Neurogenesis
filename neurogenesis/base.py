import pickle


class SimulationRun():
    def __init__(self):
        self.hash = ""
        self.config = []
        self.last_executed = 0
        self.path = ""
        self.results = {}
        self.result_vectors = {}


def serialize_sim_data(simName, simulations):
    file = open(simName, "wb+")
    pickle.dump(simulations, file)
    file.close()


def deserialize_sim_data(path):
    file = open(path, "rb")
    sim_data = pickle.load(file)
    file.close()
    return sim_data
