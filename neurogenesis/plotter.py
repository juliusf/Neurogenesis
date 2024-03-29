import matplotlib as mpl
mpl.use('pdf')
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from neurogenesis.util import Logger
import pickle
import imp
import itertools
import datetime
from scipy import stats

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
            Logger.warning("Available are: %s" % (sim.parameters))
            pass
    return True

def load_plot_config(path):
    for line in config_file:
        if line.lstrip()[0] is "#": #comment
            continue

        tokens = line.strip().split(" ")

def get_datapoints_in_buckets(simulations, x_axis_attr, y_axis_attr, filter=None, y_scale=1):
    datapoints = []
    data_buckets = {}
    for sim in simulations.values():
        if type(filter) is tuple:
            if not filter or sim.results[filter[0]] == filter[1]:
                    datapoints.append((sim.results[x_axis_attr], sim.results[y_axis_attr] / y_scale))
        else:
            result = check_filter(sim, filter)
            if result:
                try:
                    datapoints.append((sim.results[x_axis_attr], sim.results[y_axis_attr] / y_scale))
                except KeyError, e:
                    Logger.error("Could not find desired axis %s in data set!" % (e))
                    Logger.error("Available are: %s" % (sim.results.keys()))
                    #exit(-1)

    for point in datapoints:
        if point[0] not in data_buckets:
            data_buckets[point[0]] = []
        data_buckets[point[0]].append(point[1])
    tuples = []
    for (key, l) in data_buckets.items():
        tpl = (key, l)
        tuples.append(tpl)

    return sorted(tuples, key=lambda x: x[0])

def get_time_series_in_buckets(simulations, y_axis_attrs, filter=None):
    results = []
    for sim in simulations.values():
        if type(filter) is tuple:
            if not filter or sim.parameters[filter[0]] == filter[1]:
                try:
                    res = {}
                    for attr in y_axis_attrs:
                        res[attr] = sim.result_vectors[attr]
                    results.append(res)
                except KeyError, e:
                    Logger.error("Could not find desired Y axis: %s in dataset" %(e))
        else:
            result = check_filter(sim, filter)
            if result:

                    res = {}
                    for attr in y_axis_attrs:
                        try:
                            res[attr] = sim.result_vectors[attr]
                        except KeyError, e:
                            Logger.error("Could not find desired axis %s in data set!" % (e))
                            Logger.error("Available are: %s" % (sim.result_vectors.keys()))
                    results.append(res)
    return results

def generate_plot(simulation, plot_description, pdf):
    dimensions = plot_description['dimensions']
    config_map = {}
    all_filter_values = []


    for filter_values in dimensions:
        all_filter_values.append(filter_values[1])
        config_map[filter_values[0]] = filter_values[1]
    plot_configs = []
    for perm in itertools.product(*all_filter_values):
        filter = []
        for idx, dim in enumerate(perm):
            filter.append((dimensions[idx][0], dim))
        plot_configs.append(filter)

    plot_groups = plot_description['group-by'][:]
    plot_groups.insert(0, plot_description['line'])
    plot_groups.insert(0, plot_description['color'])

    for group in plot_groups:
        if isinstance(group, tuple): #tuple for named groups
            group = group[0]
        def getKey(plotConfig):
            for entry in plotConfig:
                if entry[0] == group:
                    return entry[1]
                Logger.warning("couldn't find group-key %s" % (group))
            Logger.warning("available:")
            Logger.warning(entry)
        plot_configs = sorted(plot_configs, key= getKey)

    line_parameter = plot_description['line']
    col_parameter = plot_description['color']


    nr_line_parameters = len(config_map[line_parameter]) if line_parameter is not '' else 1

    nr_col_parameters = len(config_map[col_parameter]) if col_parameter is not '' else 1

    line_mode = False
    ax = None
    box = None
    use_dotted = plot_description['line'] is not ''

    for idx, filter in enumerate(plot_configs):
        current_config = dict(filter)
        if plot_description.has_key('y-axis-scale'):
            datapoints = get_datapoints_in_buckets(simulation.simulation_runs, plot_description['x-axis'], plot_description['y-axis'], filter, plot_description['y-axis-scale'])
        else:
            datapoints = get_datapoints_in_buckets(simulation.simulation_runs, plot_description['x-axis'], plot_description['y-axis'], filter)

        if len(datapoints) == 0:
            Logger.error("Error in plot config! Simdata does not contain filter: %s" % (filter))
            exit(-1)

        if idx > 0 and idx % (nr_line_parameters * nr_col_parameters) == 0:
            # save old stuff
            generate_legend(ax, len(datapoints[0][1]), plot_description)
            plt.savefig(pdf, format='pdf')
            plt.close()


        if idx % (nr_line_parameters * nr_col_parameters) == 0:
            fig = plt.figure()
            title = generate_title(simulation, plot_description, current_config)
            fig.suptitle(title , fontsize=14, fontweight='bold')
            ax = plt.subplot(111)
            box = ax.get_position()
            ax.set_position([box.x0, box.y0 + box.height * 0.3 , box.width, box.height * 0.7])


        x_s = [dat[0] for dat in datapoints]
        y_s = [np.mean(dat[1]) for dat in datapoints]
        y_err = [stats.sem(dat[1]) for dat in datapoints]
        if idx % nr_col_parameters == 0:
            line_mode = not line_mode
            plt.gca().set_prop_cycle(None) #resets colorcycle

        line_part = "%s " %  (current_config[line_parameter]) if line_parameter is not '' else ''
        label_part = "%s " %  (current_config[col_parameter]) if col_parameter is not '' else ''
        try:
            label = label_part + "Mbps | active= " + current_config['**.rtcWebClient1.webRTCCB.enabled']
        except KeyError:
            label = label_part + "Mbps | active= " + current_config['**.rtcWebClient.webRTCCB.enabled']
        if use_dotted :
            if line_mode:
                ax.errorbar(x_s, y_s, yerr=y_err, label=label , marker="o", lw=3)
            else:
                ax.errorbar(x_s, y_s, yerr=y_err, label=label , fmt="-.", lw=3)
        else:
            ax.errorbar(x_s, y_s, yerr=y_err, label=label , marker="o", lw=3)

    generate_legend(ax, len(datapoints[0][1]), plot_description)
    plt.savefig(pdf, format='pdf')

def generate_legend(ax, n, plot_description):
    ax.set_xlabel(plot_description['x-axis-label'])
    ax.set_ylabel(plot_description['y-axis-label'])

    plt.figtext(0.02, 0.02, "n=%s" % (n))
    plt.legend(bbox_to_anchor=(0.0, -0.6, 1.0,  0), loc=3, ncol=2, mode="expand", borderaxespad=0.)

def generate_title(simulation, plot_description, current_config):
    title = plot_description['title']
    return title
    if simulation.name != "":
        title += " " + simulation.name + " "
    for entry in plot_description['group-by']:
        if isinstance(entry, tuple):
            value =  entry[1] + "=" + current_config[entry[0]]
            title += " | %s" % (value)
        else:
            value = current_config[entry]
            title += " | %s" % (value)
    return title

def plot_simulations(simulations, plot_script_path, plot_parameters=None, out_dir = '.'):
    mod = imp.load_source("plot", plot_script_path)
    if plot_parameters is None:
        mod.plot(simulations)
    else:
        mod.plot(simulations, plot_parameters)

def find_vector_XY(result_vectors, module, name, min_values):
    vec = find_vectors(result_vectors, module, name, min_values)

    if len(vec) > 0:
        vec = vec.popitem()[1]
        x_s = [x[1] for x in vec]
        y_s = [y[2] for y in vec]
        return x_s, y_s
    else:
        return [], []


def find_vectors(result_vectors, module, name, min_values):
    vec = {}
    for k, v in result_vectors.items():
        if module in k[0] and name in k[1] and len(v) > min_values:
            vec[k] = v
    return vec

