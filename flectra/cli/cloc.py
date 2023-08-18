# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.
import argparse
import os
import sys
import textwrap

from flectra.tools import cloc, config
from . import Command

class Cloc(Command):
    """\
    Flectra cloc is a tool to count the number of relevant lines written in
    Python, Javascript or XML. This can be used as rough metric for pricing
    maintenance of customizations.

    It has two modes of operation, either by providing a path:

        flectra-bin cloc -p module_path

    Or by providing the name of a database:

        flectra-bin cloc --addons-path=dirs -d database

    In the latter mode, only the custom code is accounted for.
    """
    def run(self, args):
        parser = argparse.ArgumentParser(
            prog="%s cloc" % sys.argv[0].split(os.path.sep)[-1],
            description=textwrap.dedent(self.__doc__),
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        parser.add_argument('--database', '-d', dest="database", help="Database name")
        parser.add_argument('--path', '-p', action='append', help="File or directory path")
        parser.add_argument('--verbose', '-v', action='count', default=0)
        opt, unknown = parser.parse_known_args(args)
        if not opt.database and not opt.path:
            parser.print_help()
            sys.exit()

        c = cloc.Cloc()
        if opt.database:
            config.parse_config(['-d', opt.database] + unknown)
            c.count_database(opt.database)
        if opt.path:
            for i in opt.path:
                c.count_path(i)
        c.report(opt.verbose)
