
from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages 
import glob, os.path, sys

# Read long description
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


# Path check
def which(command):
    percorso = os.getenv("PATH")
    directories = percorso.split(os.pathsep)
    for path_dir in directories:
        real_dir = os.path.expanduser(path_dir)
        try:
            lista_dir = os.listdir(real_dir)
        except OSError:
            lista_dir = []
        if os.path.exists(real_dir) and command in lista_dir:
            return os.path.join(real_dir, command)
    return None


# Look for script files
lscr = glob.glob(os.path.join('Scripts', 'SRP*'))
lscrex = []
for i in lscr:
    if os.path.splitext(i)[1] == '':
        lscrex.append(i)


# python
print "Python version %s" % (sys.version)
pvl = sys.version.split()[0].split('.')
if int(pvl[0]) != 2 or int(pvl[1]) < 3:
    print "Python version should be 2.x with x at least 6."
# eclipse
if which('ccube') == None:
    print "eclipse library (http://www.eso.org/projects/aot/eclipse/) or the python wrapping needed."
# sextractor
if which('sex') == None:
    print "sextractor package (http://terapix.iap.fr/soft/sextractor/) needed."


import SRP
durl = 'http://www.me.oa-brera.inaf.it/utenti/covino/SRPAstro-%s.tar.gz' % SRP.__version__


setup(
    name='SRPAstro', 
    version=SRP.__version__, 
    description='Data Analysis Packages', 
    packages = find_packages('.'),
    include_package_data = True,
    long_description='Set of tools for carrying out simple tasks related to astronomical observations',
    author='Stefano Covino', 
    author_email='stefano.covino@brera.inaf.it', 
    url='http://www.me.oa-brera.inaf.it/utenti/covino/SRPAstro.pdf', 
    download_url=durl,    
    install_requires=['scipy', 'astlib>=0.4', 'pil', 'matplotlib', 'atpy',
        'asciitable','pyfits', 'pyephem', 'numpy>=1.1'],
    scripts=lscrex,
    zip_safe = False,
    classifiers=[ 
        'Development Status :: 5 - Production/Stable', 
        'Environment :: Console', 
        'Intended Audience :: Science/Research', 
        'License :: Freely Distributable', 
        'Operating System :: MacOS :: MacOS X', 
        'Operating System :: POSIX', 
        'Programming Language :: Python :: 2', 
        'Topic :: Scientific/Engineering :: Astronomy', 
        ], 
    ) 


# nose
