
import pickle
import matplotlib.pyplot as plt

class SimulationConfig():
    def __init__(self):
        self.x_limits = (0,100,10)
        self.y_limits = (0, 100, 10)

        self.x_axis_parameter = ""
        self.y_axis_parameter = ""

def load_plot_config(path):


    for line in config_file:
        if line.lstrip()[0] is "#": #comment
            continue

        tokens = line.strip().split(" ")

def plot_simulations(simulations, plot_script_path):
    file = open(plot_script_path, "rb")
    plot_script = file.read()
    file.close()
    exec(plot_script)

