# -*- coding: utf-8 -*-
"""Test module for ecl2df.pillars"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import sys

import pandas as pd

from ecl2df import pillars
from ecl2df import ecl2csv
from ecl2df.eclfiles import EclFiles

TESTDIR = os.path.dirname(os.path.abspath(__file__))
DATAFILE = os.path.join(TESTDIR, "data/reek/eclipse/model/2_R001_REEK-0.DATA")


def test_pillars():
    """Test that we can build a dataframe of pillar statistics"""
    eclfiles = EclFiles(DATAFILE)
    pillars_df = pillars.df(eclfiles)
    assert "PILLAR" in pillars_df
    assert "VOLUME" in pillars_df
    assert "PORV" in pillars_df
    assert "PERMX" in pillars_df
    assert "X" in pillars_df
    assert "Y" in pillars_df
    assert "PORO" in pillars_df
    assert "OILVOL" not in pillars_df
    assert "FIPNUM" not in pillars_df
    assert "EQLNUM" not in pillars_df
    assert len(pillars_df) == 2560

    pillars_df = pillars.df(eclfiles, region="FIPNUM")
    assert "FIPNUM" in pillars_df
    assert len(pillars_df["FIPNUM"].unique()) == 6
    assert "OILVOL" not in pillars_df

    pillars_df = pillars.df(eclfiles, rstdate="first")
    assert "OILVOL" in pillars_df
    assert "GASVOL" in pillars_df
    assert "WATVOL" in pillars_df


def test_main(tmpdir):
    """Test command line interface"""
    tmpcsvfile = tmpdir.join(".TMP-pillars.csv")
    sys.argv = ["ecl2csv", "pillars", DATAFILE, "-o", str(tmpcsvfile)]
    ecl2csv.main()
    assert os.path.exists(str(tmpcsvfile))
    disk_df = pd.read_csv(str(tmpcsvfile))
    assert "PILLAR" in disk_df
    assert not disk_df.empty
