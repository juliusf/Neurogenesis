#!/bin/python

import argparse
import sys
from neurogenesis import demux


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("file", help=".ini file to be demuxed")
    arg_parser.add_argument("--outdir", help="specifies the location where files should be written to.")
    arg_parser.add_argument("--inetdir", help='location of the inet executable on NFS share')
    arg_parser.add_argument("--omnetdir", help="location of the omnet executable on NFS share")
    arg_parser.add_argument("--additionalFiles", nargs="+", help="additional Files which should be copied to the output dirs")
    args = arg_parser.parse_args()

    if args.outdir is None:
        folder_path = "/mnt/distsim/simulations/"
    else:
        folder_path = args.outdir

    if args.inetdir is None:
        inet_dir = "/mnt/distsim/inet/src/"
    else:
        inet_dir = args.inetdir

    additional_files = []

    if args.additionalFiles is not None:
        for file in args.additionalFiles:
            additional_files.append(file)

    if args.omnetdir is not None:
        omnet_exec = args.omnetdir
    else:
        omnet_exec = "/mnt/distsim/omnetpp-5.0/"
    omnet_exec += "bin/opp_run"

    simulations = demux.demux_and_write_simulation(args.file, folder_path, inet_dir, additional_files, omnet_exec)
    [sys.stdout.write(hash + " ") for hash in simulations.keys()]

if __name__ == '__main__':
    main()
