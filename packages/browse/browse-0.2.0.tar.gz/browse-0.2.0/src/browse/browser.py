# -*- python -*-
#
#  Copyright (c) 2011-2012  
#
#  File author(s): Thomas Cokelaer <cokelaer@gmail.com>
#
#  Distributed under the GPLv3 License.
#  See accompanying file LICENSE.txt or copy at
#      http://www.gnu.org/licenses/gpl-3.0.html
#
#
##############################################################################
import sys, webbrowser
import os
from optparse import  OptionParser, OptionGroup
import argparse


class Options(argparse.ArgumentParser):

    def  __init__(self, version="1.0", prog="browse"):
        usage = """usage: %s URL --verbose\nAuthor: Thomas Cokelaer, 2012""" % prog
        super(Options, self).__init__(usage=usage, version=version, prog=prog)
        self.add_input_options()

    def add_input_options(self):
        """The input oiptions.

        Default is None. Keep it that way because otherwise, the contents of
        the ini file is overwritten in :class:`apps.Apps`.
        """

        group = self.add_argument_group("Inputs", 
                    """This section allows to provide path and file names of the input data.
                    If path is provided, it will be used to prefix the midas and sif filenames.
                        --path /usr/share/data --sif test.sif --midas test.csv
                    means that the sif file is located in /usr/share/data.
                    """)

        group.add_argument("--verbose", dest='verbose', 
                         action="store_true", 
                         help="verbose option.")
        group.add_argument("--url", dest='url', default=None,
                         help="url to open")
        group.add_argument("--file", dest='file', default=None,
                         help="url to open")



def browse(url, verbose=True):
    if verbose:
        print "openning %s" % url
    webbrowser.open(url)


def main():
    import sys
    args = sys.argv[:]

    # check for verbosity
    if "--verbose" in args:
        verbose = True
        args.remove("--verbose")
        print args
    else:
        verbose = False

    if "--help" in args:
        print("Browse, a simple command line browser")
        print("Author: Thomas Cokelaer, (c) 2012.")
        print("USAGE\n\tbrowse http://docs.python.org ")
        print("\tbrowse http://docs.python.org --verbose")
        print("\tbrowse localfile.html")
        print("\tbrowse local_directory (Linux only ?)")
    url = args[1]

    import os
    if os.path.exists(url):
        if verbose:
            print("%s is local file. Trying to open it.\n" % url)
        browse(url, verbose)
    else:
        if verbose:
            print("%s seems to be a web address. Trying to open it.\n" %url)
        if url.startswith("http"):
            browse(url, verbose)
        else:
            if verbose:
                print("%s does not exists and does not starts with http, trying anyway." %url)
            browse("http://"+url, verbose)


def main_old():

    import sys
    args = sys.argv[:]
    user_options = Options()
    if len(args) == 1:
        user_options.parse_args(["browse", "--help"])
    else:
        a = user_options.parse_args(args[1:])
        if a.url:
            if a.url.startswith("http"):
                url = a.url
                webbrowser.open(url)
            else:
                url = a.url
                try:
                    browse(url, a.verbose)
                except:
                    try:
                        url = "http://" + a.url
                        browse(url, a.verbose)
                    except:
                        pass
        elif a.file:
            webbrowser.open(a.file)
        else:
            print("provide either --url or --file, none of them used !")

if __name__ == "__main__":
    main()
