from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup
from distutils.sysconfig import get_python_lib
from distutils.core import Extension
from distutils.util import get_platform
from distutils.dist import Distribution
import re


doc_files = ""

def get_pep386version():
    """This method examines the CMAKE set version variable and the most recent tags to make a pep 386 compliant version string."""
    mjsMAJOR = "1"
    mjsMINOR = "0"
    mjsPATCH = "0"

    # result of git describe
    mjsDESCRIBE = "-128-NOTFOUND"

    parts = mjsDESCRIBE.split('-')

    tag = parts[0]
    post = 0
    if (len(parts) >= 2):
        post = parts[1]
    hash = "unknown"
    if (len(parts) >= 3):
        gitHash = parts[2]


    # we expect the tags to conform to the following pattern "vN.N[.N]+(a|b|c|rc[N]"
    versionregex = re.compile( "v([0-9]+)\.([0-9]+)(\.([0-9]+))?(a|b|c|rc([0-9]+))?" )
    result = versionregex.search( tag )

    if ( not result ):
        version = str(mjsMAJOR)+"."+str(mjsMINOR)+"."+str(mjsPATCH)
        return version

    tagMAJOR = result.group(1)
    tagMINOR = result.group(2)
    # skip group with dot
    tagPATCH = "0"
    if (result.group(4)):
        tagPATCH = result.group(4)

    tagPRERELEASE = ''
    if (result.group(5)):
        tagPRERELEASE = result.group(5)



    version = str(mjsMAJOR)+"."+str(mjsMINOR)+"."+str(mjsPATCH)

    if (len(tagPRERELEASE)):
        version += tagPRERELEASE

    if((tagMAJOR==mjsMAJOR) and (tagMINOR==mjsMINOR) and (tagPATCH==mjsPATCH)):
        # tag and version match we should be release
        if (post!=0 ):
            version += ".post"+post
    else:
         if (post!=0 ):
             version += ".dev"+post

    return version


setup(
    name = 'gtm',
    version = get_pep386version(),
    author = 'OSEHRA',
    author_email = 'ibanezl@osehra.org',
    py_modules = ['gtm',],
    data_files = [(get_python_lib(), [r'/home/ibanez/bin/m.js/lib/_gtm.so']),
                  (get_python_lib(), [r'/home/ibanez/src/m.js/Source/gtm_access.ci',
                                      r'/home/ibanez/src/m.js/Source/_gtmaccess.m',
                                      r'/home/ibanez/src/m.js/Wrapping/PythonPackage/dist/README']),],
    download_url = r'https://github.com/OSEHR/m.js',
    platforms = [],
    description = r'Bindings to GT.M database.',
    long_description  = 'Binding to expost GT.M database functionalities through its C API.',
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering"
        ],
    license='Apache',
    keywords = 'GT.M database',
    url = r'https://github.com/OSEHRA-Sandbox/m.js',
    )
