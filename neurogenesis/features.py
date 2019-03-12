#! /usr/bin/env python

import sys
import httplib, urllib
import shutil
import datetime
import os
import subprocess

from neurogenesis import demux
from neurogenesis import runner
from neurogenesis import extractor
from neurogenesis.util import Logger
from neurogenesis.base import serialize_sim_data, deserialize_sim_data, Simulation
from neurogenesis.plotter import plot_simulations


def distsim_simulate(args):
    Logger.info("trying to purge old simulation data...")
    clean_old_configs(args)
    Logger.info("Creating simulation configs...")
    sim = Simulation()
    sim.last_executed = datetime.datetime.now()
    inet_commit_shell_code = "cd %s && git describe" % (args['inetdir'])
    try:
        inet_commit = subprocess.check_output(inet_commit_shell_code, shell=True).strip()
    except subprocess.CalledProcessError:
        inet_commit = "UNKNOWN"

    if args['name'] is not None:
        sim.name = args['name']
    sim.inet_commit = inet_commit

    sim.simulation_runs = write_sim_config(args)
    sim = run_simulation(args, sim)
    Logger.info("Saving simulation Metadata")
    metafile = args['metaFile']
    serialize_sim_data(metafile, sim)

    notification_message = "simulation %s (%s) finished. \n duration: %s \n non-zero exits: %s \n ran on %s ranks" % (sim.name, args['inifile'], sim.total_duration, sim.total_non_zero_exit_codes, args['nrRanks'])
    send_notification(notification_message, args)
    output_folder = "results/%s_%s/" % (sim.last_executed, sim.name)
    if args['versionResults'] == True:
       if not os.path.exists(output_folder):
                os.makedirs(output_folder)
                sim.result_dir = output_folder
                serialize_sim_data(output_folder + metafile, sim)
    else:
        serialize_sim_data(metafile, sim)
    return sim

def distsim_extract(args, simulation = None):
        Logger.info("Extracting Scalars")
        updated_simulations = extract(args, simulation)
        Logger.info("done. Writing results back to metafile")
        Logger.warning(updated_simulations.result_dir)
        if updated_simulations.result_dir != '':
            serialize_sim_data(updated_simulations.result_dir + args['metaFile'], updated_simulations)

        serialize_sim_data(args['metaFile'], updated_simulations)

def distsim_plot(args):
        plot_simfile(args)

def distsim_clean(args):
        Logger.info("trying to purge old simulation data...")
        clean_old_configs(args)

def distsim_retry(args):
        Logger.info("Retrying failed simulation runs...")
        simulation = deserialize_sim_data(args['metaFile'])
        sim = runner.run_simulation(args['mpiWorker'], args['hostfile'], args['nrRanks'], simulation, retry_only = True)
        Logger.info("Saving simulation Metadata")
        serialize_sim_data(args['metaFile'], sim)

        notification_message = "simulation %s (%s) finished. \n duration: %s \n non-zero exits: %s \n ran on %s ranks" % (sim.name, args['inifile'], sim.total_duration, sim.total_non_zero_exit_codes, args['nrRanks'])
        send_notification(notification_message, args)

def distsim_dump(args):
        Logger.info("dumping the first 50 run hashes...")
        simulation = deserialize_sim_data(args['metaFile'])
        rns = simulation.simulation_runs.keys()[:50]
        [Logger.info(run) for run in runs]

def distsim_notify(args):
        send_notification(args['notifyMsg'], args)

def run_simulation(args, sim):
        Logger.info("Starting distributed Simulation with %i ranks" % args['nrRanks'])
        return runner.run_simulation(args['mpiWorker'], args['hostfile'], args['nrRanks'], sim)

def extract(args, simulation = None):
    if simulation == None:
        simulation = deserialize_sim_data(args['metaFile'])

    simulations = simulation.simulation_runs
    try:
        simulations = extractor.extract(args['extractScalarsFile'], simulations)
    except IOError as e:
        Logger.warning("Can't read scalars file: %s, exception: %s" % (args['extractScalarsFile'], e.strerror))
    try:
        simulations = extractor.extract_vectors(args['extractVectorsFile'], simulations)
    except IOError as e:
        Logger.warning("Can't read vectors file: %s, exception: %s" % (args['extractVectorsFile'], e.strerror))
    simulation.simulation_runs = simulations
    return simulation


def plot_simfile(args):
    simulations = deserialize_sim_data(args['metaFile'])
    plot_simulations(simulations, args['plotScript'])

def write_sim_config(args):
    if args['inifile'] is None:
        Logger.error("No ini File specified!")
        sys.exit(-127)
    simulations = demux.demux_and_write_simulation(args)
    return simulations

def clean_old_configs(args):
    try:
        simulations = deserialize_sim_data(args['metaFile'])
    except IOError as e:
        Logger.info("no previous simulations found")
        return

    Logger.info("purging old simulation data")
    for simulation in simulations.simulation_runs.values():
        shutil.rmtree(simulation.path, ignore_errors=True)

def send_notification(msg, args):
    try:
        pushover_secret_file = open(args['notificationKeyFile'], "r")
    except IOError:
        Logger.warning("pushover secret-file does not exist")
        return
    secret = pushover_secret_file.read().strip()
    conn = httplib.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
    urllib.urlencode({
    "token": "ae1u9qxnk2obfgiodr19rrbo2bsazs",
    "user": secret,
    "message": msg,
  }), { "Content-type": "application/x-www-form-urlencoded" })
    conn.getresponse()

    pushover_secret_file.close()


