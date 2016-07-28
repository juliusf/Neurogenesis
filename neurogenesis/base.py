import pickle

class SimulationRun():
    def __init__(self):
        self.hash = ""
        self.config = []
        self.last_executed = 0
        self.path = ""


def serialize_sim_data(simName, simulations):
    file = open(simName, "wb")
    pickle.dump(simulations, file)
    file.close()
