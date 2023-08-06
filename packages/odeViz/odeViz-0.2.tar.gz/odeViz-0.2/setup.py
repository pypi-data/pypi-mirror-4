import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "odeViz",
    version = "0.2",
    author = "Andr"+unichr(233)+" Dietrich",
    author_email = "dietrich@ivs.cs.uni-magdeburg.de",
    description = ("This toolbox generates automatically a vtk-visualization for an ode (Open Dynamics Engine) simulation under Python. You only have to define the simulation space and world and forward these entities to the visualization."),
    license = "BSD",
    keywords = "ode, vtk",
    url = "https://pypi.python.org/pypi/ode-viz",
    packages=['odeViz'],
    long_description=read('README'),
    install_requires=['PyVTK', 'PyODE'],
    dependency_links = ["https://pypi.python.org/packages/source/P/PyODE/PyODE-1.2.1.tar.gz", "http://cens.ioc.ee/projects/pyvtk/rel-0.x/PyVTK-0.latest.tar.gz"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)