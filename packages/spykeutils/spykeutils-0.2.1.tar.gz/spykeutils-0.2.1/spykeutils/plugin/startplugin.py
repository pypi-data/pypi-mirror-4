#! /usr/bin/env python

import sys
import os
import argparse
import inspect
import json
import pickle

from spykeutils.plugin.analysis_plugin import AnalysisPlugin
from spykeutils.plugin.data_provider import DataProvider

# Data provider implementations need to be imported so they can be loaded
import spykeutils.plugin.data_provider_stored


def main():
    parser = argparse.ArgumentParser(description='Start an analysis plugin')
    parser.add_argument('Name', type=str, help='Name of analysis class')
    parser.add_argument('Code', type=str, help='Code of the analysis')
    parser.add_argument('Selection', type=str, help='Serialized selection')
    parser.add_argument('-c', '--config', dest='config', type=str,
        help='Pickled configuration of analysis')
    parser.add_argument('-cf', '--codefile', dest='codefile',
        action='store_const', const=True, default=False,
        help='Code represents a filename containing code (default: Code is a string containing code')
    parser.add_argument('-sf', '--selectionfile', dest='selectionfile',
        action='store_const', const=True, default=False,
        help='Selection represents a filename containing the serialized selection (default: Selection is a string')
    parser.add_argument('-dd', '--datadir', type=str, help='The data directory')

    args = parser.parse_args()

    exc_globals = {}

    if args.codefile:
        execfile(args.Code, exc_globals)
    else:
        exec(args.Code, exc_globals)

    # Load plugin
    plugin = None
    for cl in exc_globals.values():
        if not inspect.isclass(cl):
            continue

        if not issubclass(cl, AnalysisPlugin):
            continue

        if not cl.__name__ == args.Name:
            continue

        plugin = cl()
        break

    if not plugin:
        sys.stderr.write('Could not find plugin class, aborting...\n')
        sys.exit(1)

    # Load configuration
    if args.config:
        plugin.set_parameters(pickle.loads(args.config))

    # Load selection
    sels = []
    try:
        if args.selectionfile:
            f = open(args.Selection, 'r')
            sel_string = '\n'.join(f.readlines())
        else:
            sel_string = args.Selection

        sels = json.loads(sel_string)
    except Exception, e:
        sys.stderr.write('Could not load selection, aborting...\n')
        sys.exit(1)

    selections = []
    for s in sels:
        selections.append(DataProvider.from_data(s))

    if args.datadir and os.path.isdir(args.datadir):
        AnalysisPlugin.data_dir = args.datadir
    plugin.start(selections[0], selections[1:])

if __name__ == '__main__':
    main()