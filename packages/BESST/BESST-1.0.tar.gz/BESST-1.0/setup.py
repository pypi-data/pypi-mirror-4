import os
from setuptools import setup, find_packages

setup(
    name='BESST',
    version='1.0',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        #"License :: GNU General Public License v3 or later (GPLv3+)",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Topic :: Scientific/Engineering :: Bio-Informatics"
      ],
    #py_modules=['BESST.py'],
    #packages=['BESST',],
    scripts=['runBESST', 'docs/INSTALL.txt', 'docs/MANUAL.txt'],
    description='Scaffolder for genomic assemblies.',
    author='Kristoffer Sahlin',
    author_email='kristoffer.sahlin@scilifelab.se',
    url='https://github.com/ksahlin/BESST',
    license='GPLv3',
    long_description=open(os.path.join(os.getcwdu(), 'README.md')).read(),
    #requires=['pysam (>=0.6)','networkx (>=1.4)'],
    install_requires=['pysam==0.6',
                      'networkx>=1.4',
                      'mathstats'],
    #platforms=['Unix', 'Linux', 'Mac OS']
)
