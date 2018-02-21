import re
import sys

import os
from neurogenesis.util import Logger


def extract(scalars_file, simulations):
    scalars = []
    scalars_file = open(scalars_file, "rb")
    [scalars.append(scalar.rstrip()) for scalar in scalars_file]
    scalars_file.close()
    for simulation in simulations.values():
        scalar_encountered = dict( zip( scalars, [False] * len(scalars)))

        try:
            path = None
            resultdir = os.path.join(simulation.path, "results")
            for file in os.listdir(resultdir):
                if file.endswith('.sca'):
                    path = os.path.join(resultdir, file)
                    break
            if path is None:
                raise IOError('could not find result file!')
            with open(path) as result_file:
                for line in result_file:
                    if line.startswith("scalar"):
                        for scalar in scalars:
                            if scalar in line:
                                simulation.results[scalar] = extract_scalar_value(line)
                                scalar_encountered[scalar] = True
                    elif line.startswith("param"):
                        for scalar in scalars:
                            if scalar in line:
                                simulation.results[scalar] = extract_parameter_value(line)
                                scalar_encountered[scalar] = True
            for k,v in scalar_encountered.items():
                if not v:
                    Logger.warning("Couldn't find scalar %s in result file %s!" % (k, path) )
        except IOError as e:
            Logger.error("Results file for simulation: %s not found! error: %s" % (simulation.path, e.strerror))
            sys.exit(-1)
    Logger.info("Extracted scalars of %s simulations." % (len(simulations.values())))
    return simulations


def extract_scalar_value(line):
    # end_of_scalar_name = line.rfind("\"")
    # nr = line[end_of_scalar_name + 1:].strip()
    nr = line.strip().split()[-1]
    return float(nr)


def extract_parameter_value(line):
    if line.strip().endswith('"'):
        segments = line.split('"')
        value = segments[-2]
    else:
        segments = line.strip().split(" ")
        value = segments[-1]
    value = re.sub("[^0-9e\-\.]", "", value)  # replaces all non numeric values
    try:
        return float(value)
    except ValueError:
        return value


def extract_vectors(vector_file, simulations):
    with open(vector_file, "rb") as vector_file:
        vectors = [vector.rstrip() for vector in vector_file]
    encountered_filters = {}
    for simulation in simulations.values():
        try:
            path = None
            resultdir = os.path.join(simulation.path, "results")
            for file in os.listdir(resultdir):
                if file.endswith('.vec'):
                    path = os.path.join(resultdir, file)
                    break
            if path is None:
                raise IOError('could not find result file!')
            with open(path) as result_vector: # valid till omnet5.0
                values = {}
                values_names = {}
                for line in result_vector:
                    if line.startswith("vector"):
                        nr, module = line.split(" ")[1:3]
                        name = " ".join(line.split(" ")[3:]) #ugly hack to allow for Vector names with spaces
                        name = name.split(":vector")[0]
                        name = name.rstrip("ETV\n")
                        name = name.strip()
                        if check_match(vectors, module, name, encountered_filters):
                            values[nr] = []
                            values_names[nr] = (module, name)
                    elif len(line.strip()) > 0 and line.split()[0] in values:
                        v = [float(x) for x in line.split()[1:4]]
                        values[line.split()[0]].append(v)

            for k in values_names:
                simulation.result_vectors[values_names[k]] = values[k]
        except IOError as e:
            Logger.error("Results file for simulation: %s not found! error: %s" % (simulation.path, e.strerror))
            sys.exit(-1)
    for k, v in encountered_filters.iteritems():
        if not v:
            Logger.warning("Exctractor couldn't find match for filter: %s" % (k))
        else:
            Logger.info("Extractor found match for filter %s" % (k))
    return simulations


def check_match(patterns, module, name, encountered_filters):
    for pattern in patterns:
        if pattern not in encountered_filters:
            encountered_filters[pattern] = False
        if module in pattern and name in pattern:
            encountered_filters[pattern] = True
            return True
