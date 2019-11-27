#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Extract statistics pr cornerpoint pillar (i.j)-pair

"""
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import sys
import logging
import argparse
import fnmatch
import datetime
import dateutil.parser

import numpy as np
import pandas as pd

import ecl2df
from ecl.eclfile import EclFile
from .eclfiles import EclFiles


def df(eclfiles, rstdates=None):
    """Produce a dataframe with pillar information

    This is the "main" function for Python API users"""
    grid_df = ecl2df.grid.df(eclfiles, rstdates=rstdates)
    # todo: only select SGAS/SWAT from rst vectors

    gridgeom = gridgeometry2df(eclfiles)
    initdf = init2df(eclfiles, vectors=vectors)
    rst_df = None
    if rstdates:
        rst_df = rst2df(eclfiles, rstdates)
    grid_df = merge_gridframes(gridgeom, initdf, rst_df)
    if dropconstants:
        # Note: Ambigous object names, bool vs function
        grid_df = ecl2df.grid.dropconstants(grid_df)


    return grid_df


def fill_parser(parser):
    """Set up sys.argv parser.

    Arguments:
        parser: argparse.ArgumentParser or argparse.subparser
    """
    parser.add_argument(
        "DATAFILE",
        help=("Name of Eclipse DATA file. " "INIT and EGRID file must lie alongside."),
    )
    parser.add_argument(
        "--region",
        help="Name of Eclipse region parameter for which to separate the computations",
        type=str,
        default="EQLNUM",
    )
    parser.add_argument(
        "--initkeys",
        nargs="+",
        help="INIT vector wildcards for vectors to include",
        default="*",
    )
    parser.add_argument(
        "--rstdate",
        type=str,
        help=(
            "Point in time to grab restart data from, "
            "either 'first' or 'last', or a date in "
            "YYYY-MM-DD format"
        ),
        default="",
    )
    parser.add_argument(
        "--rststride",
        type=int,
        default=1,
        help=(
            "Number of RST reports to skip. "
            "Use a very large number "
            "to get first and last RST report."
        ),
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Name of output csv file.",
        default="eclgrid.csv",
    )
    parser.add_argument(
        "--dropconstants",
        action="store_true",
        help="Drop constant columns from the dataset",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Be verbose")
    return parser


def main():
    """Entry-point for module, for command line utility. Deprecated to use
    """
    logging.warning(
        "oilcol2csv is deprecated, use 'ecl2csv pillarstats <args>' instead"
    )
    parser = argparse.ArgumentParser()
    parser = fill_parser(parser)
    args = parser.parse_args()


def pillarstats_main(args):
    """This is the command line API"""
    if args.verbose:
        logging.basicConfig(level=logging.INFO)
    df = df(eclfiles, args)

    if args.output == "-":
        # Ignore pipe errors when writing to stdout.
        from signal import signal, SIGPIPE, SIG_DFL

        signal(SIGPIPE, SIG_DFL)
        df.to_csv(sys.stdout, index=False)
    else:
        df.to_csv(args.output, index=False)
        print("Wrote to " + args.output)
