 # This Python file uses the following encoding: utf-8
from distutils.core import setup
setup(
    name = "cobilib",
    packages = ["cobilib"],
    version = "1.0.0",
    description = "Optimizing Codon Usage with a Quasispecies Model",
    author = "Jan-Hendrik Trösemeier, Christel Kamp, Susanne Lipp",
    author_email = u'jan-hendrik.troesemeier@pei.de',
    url = "TODO.orggithub?",
    download_url = "TODO.orggithub?.tar.gz",
    keywords = ["bioinformatics"],
    classifiers = [
                   "Programming Language :: Python",
                   "Environment :: Console",
                   "Development Status :: 3 - Alpha",
                   "Intended Audience :: Science/Research",
                   "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
                   "Topic :: Scientific/Engineering :: Bio-Informatics"
                   ],
    license='LICENSE',
    long_description = open('README').read(),
    requires=[
    "sklearn",
    "matplotlib",
    "inspyred"
    ]
)


