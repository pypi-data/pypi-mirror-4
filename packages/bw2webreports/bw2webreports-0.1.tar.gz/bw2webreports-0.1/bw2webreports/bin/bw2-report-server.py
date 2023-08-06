#!/usr/bin/env python
# encoding: utf-8
"""Brightway2 web user interface.

Usage:
  bw2-report-server.py <data_dir> [--port=<port>]
  bw2-report-server.py -h | --help
  bw2-report-server.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.

"""
from bw2webreports import report_server
from docopt import docopt
from werkzeug.serving import run_simple


if __name__ == "__main__":
    args = docopt(__doc__, version='Brightway2 Reports Server 0.1')
    port = int(args.get("--port", False) or 8000)
    report_server.config['DATA_DIR'] = args["<data_dir>"]
    run_simple("0.0.0.0", port, report_server, use_evalex=True)
