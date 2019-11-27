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

import ecl2df


def df(eclfiles, region=None, rstdate=None):
    """Produce a dataframe with pillar information

    This is the "main" function for Python API users
    Produces a dataframe with data for each I-J combination
    (in the column PILLAR), and if a region parameter is
    supplied, also pr. region.

    PORV is the summed porevolume of the pillar (in the region),
    VOLUME is bulk volume, and PORO is porevolume weighted porosity
    PERM columns contain unweighted value averages, use with caution.

    If a restart date is picked, then SWAT and SGAS will
    be used to compute volumes pr. phase, WATVOL, OILVOL and GASVOL.

    Args:
        region (str): A parameter the pillars will be split
            on. Typically EQLNUM or FIPNUM.
        rstdate (str): Date for which restart data
            is to be extracted. The string can
            be in ISO-format, or one of the mnenomics
            'first' or 'last'.
    """
    if isinstance(rstdate, list):
        raise ValueError("Lists of rstdates not supported for pillars")

    grid_df = ecl2df.grid.df(eclfiles, rstdates=rstdate)

    grid_df["PILLAR"] = grid_df["I"].astype(str) + "-" + grid_df["J"].astype(str)

    groupbies = ["PILLAR"]
    if region:
        if region not in grid_df:
            logging.warning("Region parameter %s not found, ignored", region)
        else:
            groupbies.append(region)
            grid_df[region] = grid_df[region].astype(int)

    if "SWAT" in grid_df and "SGAS" in grid_df:
        grid_df["SOIL"] = 1 - grid_df["SWAT"] - grid_df["SGAS"]
    if "SWAT" in grid_df and "SGAS" not in grid_df:
        # Two-phase oil-water
        grid_df["SOIL"] = 1 - grid_df["SWAT"]
        # (or it could be two-phase water-gas, but then the SOIL would mean the same)

    if "SWAT" in grid_df:
        grid_df["WATVOL"] = grid_df["SWAT"] * grid_df["PORV"]
    if "SGAS" in grid_df:
        grid_df["GASVOL"] = grid_df["SGAS"] * grid_df["PORV"]
    if "SOIL" in grid_df:
        grid_df["OILVOL"] = grid_df["SOIL"] * grid_df["PORV"]

    aggregators = {
        "VOLUME": "sum",
        "PORV": "sum",
        "PERMX": "mean",
        "PERMY": "mean",
        "PERMZ": "mean",
        "X": "mean",
        "Y": "mean",
        "Z": "mean",
        "WATVOL": "sum",
        "GASVOL": "sum",
        "OILVOL": "sum",
    }
    aggregators = {key: aggregators[key] for key in aggregators if key in grid_df}

    grouped = (
        grid_df[list(aggregators.keys()) + groupbies]
        .groupby(groupbies)
        .agg(aggregators)
    ).reset_index()
    if "PORV" and "VOLUME" in grouped:
        grouped["PORO"] = grouped["PORV"] / grouped["VOLUME"]

    return grouped


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
        "-o",
        "--output",
        type=str,
        help="Name of output csv file.",
        default="pillars.csv",
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
    pillarstats_main(parser.parse_args())


def pillarstats_main(args):
    """This is the command line API"""
    if args.verbose:
        logging.basicConfig(level=logging.INFO)
    eclfiles = ecl2df.EclFiles(args.DATAFILE)
    dframe = df(eclfiles, region=args.region, rstdate=args.rstdate)

    if args.output == "-":
        # Ignore pipe errors when writing to stdout.
        from signal import signal, SIGPIPE, SIG_DFL

        signal(SIGPIPE, SIG_DFL)
        dframe.to_csv(sys.stdout, index=False)
    else:
        dframe.to_csv(args.output, index=False)
        print("Wrote to " + args.output)
