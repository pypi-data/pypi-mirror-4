# -*- python -*-
#
#  This file is part of the CNO software
#
#  Copyright (c) 2011-2012 - EBI
#
#  File author(s): Thomas Cokelaer <cokelaer@ebi.ac.uk>
#
#  Distributed under the GPLv2 License.
#  See accompanying file LICENSE.txt or copy at
#      http://www.gnu.org/licenses/gpl-2.0.html
#
#  CNO website: http://www.ebi.ac.uk/saezrodriguez/cno
#
##############################################################################
# $:Id $
"""This script checks out the latest revision of a SVN directory corresponding
to one of CellNOpt R package into a temporary directory. It then build the
pacakge and save a copy of the corresponding tar ball with the proper version
and SVN tag. Sub directories such as .svn are removed. The temporary directory is
also removed at the end.


"""
import os
import subprocess
import tempfile
from os.path import join as pj
import glob
import time
from easydev.tools import shellcmd
include = ["*"]
from distribute import DistributeRPackage


class MultiDistributeRPackage(object):
    """Script to ease distribution of R package from SVN

        >>> d = MultiDistributeRPackage()
        >>> d.distribute()

    Best is to call multidistribute from command line::

        python multidistribute.py --revision HEAD --packages CNORdt CNORfuzzy
        python multidistribute.py --revision 666

    """

    def __init__(self, packages=[], revision="HEAD", verbose=False):
        self.packages = packages
        if len(self.packages) == 0:
            self.packages = DistributeRPackage._valid_packages.keys()

        self.verbose = verbose
        self.revision = revision

    def run(self):
        """Build a package for each packages provided. 

        Default is a list containing CellNOptR, CNORdt, CNORode, CNORfuzzy"""
        for package in self.packages:
            print package
            d = DistributeRPackage(package ,
                    revision=self.revision,
                    verbose=self.verbose)
            d.distribute()

    def help():
        """Return usage help message"""
        print("\nPURPOSE:"+__doc__)
        print("USAGE: python multidistribute.py --revision 500")
        print("USAGE: python multidistribute.py --revision 500 --packages pkg1 pkg2")
        print("Possible package names are %s ." % MultiDistributeRPackage._valid_packages.keys())
        sys.exit(1)


if __name__ == "__main__":
    import sys
    print("RUNNING multidistribute.py")
    print("===========================================")
    print("Author: T. Cokelaer, $Rev: 2565 $")
    import tempfile
    if len(sys.argv) == 1:
        revision = "HEAD"
        packages = []
    elif len(sys.argv) == 3:
        assert sys.argv[1] == "--revision", MultiDistributeRPackage.help()
        revision = sys.argv[2]
        packages = []
    elif len(sys.argv) >= 5:
        revision = "HEAD"
        assert sys.argv[3] == "--packages", MultiDistributeRPackage.help()
        packages = sys.argv[4:]

    d = MultiDistributeRPackage(packages, revision=revision)
    d.run()

