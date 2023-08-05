import commands 
import os
import time
from distutils.core import setup

#Determine & save the revision number for the ETC
warning=""
vfname=os.path.join('.','VERSION')
try:
    # Always try to determine the version using svnversion
    warning=""
    stat,revset=commands.getstatusoutput('hg id -n')
    if stat != 0:
        raise ValueError("cannot extract version information from hg.")
    if revset.find("+") >= 0 :
        warning="this copy is modified"

    revset = revset.replace("M","")

    f=open(vfname,'w')
    f.write(revset)
    f.close()

except ValueError:
    print "couldn't run hg so will read version from VERSION file."
    #If we can't generate it, then see if the version file already
    #exists from when the source distribution was being assembled. 
    try :
        f=open(vfname,"r")
        revset=f.readline()
        f.close()
    except IOError:
        warning="cannot extract version information"
        revset='unavailable'

VERSION = "1.0."+revset

print warning
print "assuming that the version is " + VERSION

try: 
   import pyscons
   docs = pyscons.__doc__
   print >>open("README.txt", "w"), docs,
except:
   docs = file("README.txt").read()


setup(name="PyScons",
    version=VERSION,
    description="An extension to Scons which enables dependency tracking on python script imports.",
    long_description=docs,
    author="S. Joshua Swamidass",
    url="http://swami.wustl.edu/",
    author_email="swamidass@gmail.com",
    classifiers=["Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Science/Research",
        "License :: Free for non-commercial use",
        "Natural Language :: English",
        "Topic :: Software Development :: Build Tools",
        "Programming Language :: Python",
        "Topic :: System :: Installation/Setup",
        "Intended Audience :: Developers",
        ],
    py_modules=['pyscons']
)
