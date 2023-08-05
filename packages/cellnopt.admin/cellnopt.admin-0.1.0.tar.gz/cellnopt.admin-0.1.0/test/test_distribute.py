from rtools import distribute
import os

def test_dist():
    d = distribute.DistributeRPackage("CellNOptR", revision="HEAD", 
            url='https://svn.ebi.ac.uk/sysbiomed/trunk') 
    d.distribute()
    os.remove(d.package_name_rev)

def test_dist1():
    d = distribute.DistributeRPackage("CellNOptR", revision="HEAD")
    d.distribute()
    os.remove(d.package_name_rev)


def test_help():
    d = distribute.DistributeRPackage("CellNOptR", revision="HEAD")
    d.help()


def test_exec():
    import sys
    sys.argv=['dummy', '--help']
    distribute.main()

    
