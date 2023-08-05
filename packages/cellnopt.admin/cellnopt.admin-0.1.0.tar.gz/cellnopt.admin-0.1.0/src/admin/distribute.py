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
#  CNO website: http://www.ebi.ac.uk/~cokelaer/easydev
#
##############################################################################
# $Id: distribute.py 2565 2012-10-17 13:29:07Z cokelaer $
"""This script checks out the latest revision of a SVN directory (in the current
directory) into a temporary directory. It then creates a tar ball out of that 
SVN copy and copy the final tar ball in the directory where this script is
called. Sub directories such as .svn are removed. The temporary directory is
also removed.


"""
import os
import subprocess
import tempfile
from os.path import join as pj
import glob
import time
import sys

from easydev.tools import shellcmd
include = ["*"]


class DistributeRPackage(object):
    """Script to ease distribution of R packages from SVN

        >>> d = DistributeRPackage("CNORdt")
        >>> d.distribute()

    Best is to call distribute from command line::

        python distribute.py --package CNORdt --revision HEAD
        python distribute.py --package CNORdt --revision 666

    .. note:: there is also a script called easydev_distribute that works as
        "python distribute.py"

    Valid packages are stored in DistributeRPackage._valid_packages

    """
    _valid_packages = {"CellNOptR":"CellNOptR",
                       "CNORdt":pj("CNOR_dt","CNORdt"),
                       "CNORode":pj("CNOR_ode","CNORode"),
                       "CNORfuzzy":"CNOR_fuzzy",
                       "CNORfeeder":"CNOR_add_links",
                       "MEIGOR": pj('essR','MEIGOR')}

    def __init__(self, package, url=None, revision="HEAD", build_options="--no-vignettes",
        verbose=False):
        """

        :param str package: name of a valid package (e.g., CellNOptR)
        :param revision: SVN revision (default is HEAD )
        :param str url:
        :param bool verbose: (default is False)

        """
        if url == None:
            self.url = "https://svn.ebi.ac.uk/sysbiomed/trunk"
        else:
            self.url = url
        self.revision_user = revision
        self.exclude = [".svn"]
        self.package = package
        self.dtemp = None
        self.cwd = os.getcwd()
        self.verbose = verbose
        self.build_options = build_options

    def _getversion(self):
        data = open(self.dtemp + os.sep + self.package + os.sep + "DESCRIPTION", "r").read()
        res = [x.split(':')[1].strip() for x in data.split("\n") if x.startswith('Version')]
        return res[0]
    version = property(_getversion, doc="return version of the R package")

    def _get_package_directory(self):
        return DistributeRPackage._valid_packages[self.package]

    def _create_temp_directory(self):
        self.dtemp = tempfile.mkdtemp()

    def _checkout_svn(self):
        if self.dtemp == None:
            self._create_temp_directory()
        target = pj(self.dtemp, self.package)
        path = self.url + '/' + self._get_package_directory()
        cmd = "svn co -r%s %s/%s %s" % (self.revision_user, self.url,
            DistributeRPackage._valid_packages[self.package], pj(self.dtemp, self.package))
        print cmd, 
        try:
            ret = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
            ret.wait()
            if ret.poll()!=0:
                raise Exception
            print '...done'
        except Exception:
            raise Exception

    @staticmethod
    def help():
        """Return usage help message"""
        print("\nPURPOSE:"+__doc__)
        print("USAGE: python distribute.py --package valid_package_name")
        print("USAGE: python distribute.py --package valid_package_name --revision 500")
        print("USAGE: python distribute.py --svn valid_SVN --package valid_package_name --revision 500")
        print("")
        print("Possible package names are %s ." % DistributeRPackage._valid_packages.keys())
        #sys.exit(1)

    def distribute(self):
        """Creates the distribution files

        1. creates temp directoy
        2. svn checkout clean revision
        3. calls R CMD build

        """
        if self.dtemp == None:
            self._create_temp_directory()
        try:
            self._checkout_svn()
        except Exception, e:
            self._stop()
            raise Exception(e)

        self._build_R_package()
        self._stop()
        

    def _stop(self):
        import shutil
        if self.dtemp:
            shutil.rmtree(self.dtemp)

    def _get_revision(self):
        print("Getting the current SVN revision")
        try:

            tag="Last Changed Rev"
            cmdsvn = """svn info %s | grep "%s" | awk '{print $4}' """ % (pj(self.dtemp, self.package), tag)
            #tag="Revision"
            #cmdsvn = """svn info %s | grep "%s" | awk '{print $2}' """ % (pj(self.dtemp, self.package), tag)
            print(cmdsvn)
            ret = subprocess.Popen(cmdsvn, stdout=subprocess.PIPE, shell=True)
            ret.wait()
            revision = ret.stdout.read().strip()
        except Exception, e:
            revision = self.revision_user
            raise Exception(e)
        print("This is revision %s. Making a tar ball." % revision)
        return revision
    revision = property(_get_revision, doc="return SVN revision")

    def _build_R_package(self):
        # first, build the R package
        print("2."),
        t0 = time.time()
        cmdR = "R CMD build %s %s" % (self.dtemp+os.sep+self.package, self.build_options)
        shellcmd(cmdR, verbose=True)

        import glob
        package_name = self.package + "_" + self.version + ".tar.gz"
        #rename the package name
        package_name_rev = self.package + "_"+self.version + "_svn" + self.revision + ".tar.gz"
        print("3. "),
        shellcmd("ls %s" % (self.dtemp), verbose=True)
        shellcmd("ls", verbose=True)
        shellcmd("mv %s %s" % (package_name, package_name_rev), verbose=True)

        t1 = time.time()
        print(str(t1-t0) + " seconds.")
        self.package_name_rev = package_name_rev


    def _get_tar_all(self):
        """not used anymore ?"""
        # buildig a proper name for the distribution
        print("Creating tar balls\n 1."),
        output_filename = "%s_%s.tar.gz" % (self.package, self.revision)
    
        # the tar command, 
        cmdtar = "cd %s;" % self.dtemp
        cmdtar += "tar cvfz %s %s" % (pj(self.cwd, output_filename), self.package)
        # including and excluding directories and files
        for this in self.exclude:
            cmdtar += " --exclude=%s " % this
        for this in include:
            cmdtar += " %s " % this
        shellcmd(cmdtar)


def main():
    """Main executable related to distribute

    type::

        python distribute.py --help

    or::

        cnolab_distribute --help

    """
    import sys
    print("RUNNING distribute.py")
    print("===========================================")
    print("Author: T. Cokelaer, $Rev: 2565 $")
    if len(sys.argv)!=3 and len(sys.argv)!=5:
        DistributeRPackage.help()
    else:
        import tempfile
        assert sys.argv[1] == "--package", DistributeRPackage.help()
        package = sys.argv[2]
        if len(sys.argv) == 5:
            assert sys.argv[3] == "--revision", DistributeRPackage.help()
            revision = sys.argv[4]
        else:
            revision = "HEAD"
        d = DistributeRPackage(package, revision=revision)
        d.distribute()

if __name__ == "__main__":
    main()
