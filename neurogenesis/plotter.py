from neurogenesis.util import Logger
import pickle
import imp

class SimulationConfig():
    def __init__(self):
        self.x_limits = (0,100,10)
        self.y_limits = (0, 100, 10)

        self.x_axis_parameter = ""
        self.y_axis_parameter = ""


def check_filter(sim, filter_list):
    for filter in filter_list:
        try:
            if not sim.parameters[filter[0]] == filter[1]:
               return False
        except KeyError:
            Logger.warning("The dataset does not contain filter value: %s" % (filter[0]))
            pass
    return True

def load_plot_config(path):
    for line in config_file:
        if line.lstrip()[0] is "#": #comment
            continue

        tokens = line.strip().split(" ")

def get_datapoints_in_buckets(simulations, x_axis_attr, y_axis_attr, filter=None):
    datapoints = []
    data_buckets = {}
    for sim in simulations.values():
        if type(filter) is tuple:
            if not filter or sim.results[filter[0]] == filter[1]:
                datapoints.append((sim.results[x_axis_attr], sim.results[y_axis_attr]))
        else:
            result = check_filter(sim, filter)
            if result:
                datapoints.append((sim.results[x_axis_attr], sim.results[y_axis_attr]))

    for point in datapoints:
        if point[0] not in data_buckets:
            data_buckets[point[0]] = []
        data_buckets[point[0]].append(point[1])
    tuples = []
    for (key, l) in data_buckets.items():
        tpl = (key, l)
        tuples.append(tpl)

    return sorted(tuples, key=lambda x: x[0])

def plot_simulations(simulations, plot_script_path):
    mod = imp.load_source("plot", plot_script_path)
    mod.plot(simulations)


