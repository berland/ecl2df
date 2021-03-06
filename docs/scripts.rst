ecl2csv
=======

.. _ecl2csv:

Most of the functionality in ecl2df is exposed to the command line through
the script *ecl2csv*. The first argument to this script is always
the submodule (subcommand) from which you want functionality. Mandatory argument is
always an Eclipse deck or sometimes individual Eclipse include files, and
there is usually an ``--output`` option to specify which file to dump
the CSV to. If you want output to your terminal, use ``-`` as the output filename.

.. argparse::
   :ref: ecl2df.ecl2csv.get_parser
   :prog: ecl2csv

csv2ecl
=======

.. _csv2ecl:

Some of the modules inside ecl2df is able to write Eclipse include files
from dataframes (in the format dumped by ecl2df). This makes it possible
to produce Eclipse input data in any application that can write CSV files,
and use this tool to convert it into Eclipse include files, or it can
facilitate operations/manipulations of an existing deck using any tool
that can work on CSV files, by first running ecl2csv on an input file,
transforming it, and writing back using csv2ecl.

Mandatory argument for csv2ecl is
always the submodule responsible, a CSV file, and
an ``--output`` option to specify which include file to write to.
If you want output to your terminal, use ``-`` as the output filename. Unless
you also specify the ``--keywords`` argument with a list of wanted keywords, all
supported keywords for a submodule which is also found in the CSV file provided,
will be dumped to output file.

.. argparse::
   :ref: ecl2df.csv2ecl.get_parser
   :prog: csv2ecl
