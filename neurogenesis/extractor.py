

def extract(scalars_file, simulations):
    scalars = []
    scalars_file = open(scalars_file, "rb")
    [scalars.append(scalar) for scalar in scalars_file]
    scalars_file.close()

    for simulation in simulations:
        result_file = open(simulation.path + "results/General-0.sca")
        for line in result_file:
            if line.startswith("scalar"):
                for scalar in scalars:
                    if scalar in line:
                        simulation.results[scalar] = extract_scalar_value(line)
                        break
        result_file.close()
    return simulations

def extract_scalar_value(line):
    end_of_scalar_name = line.rfind("\"")
    nr = line[end_of_scalar_name +1:].strip()
    return float(nr)
