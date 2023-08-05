# minpower's setup script

#build using:
#python setup.py sdist

#udpate pypi using:
#python setup.py register
#python setup.py sdist upload
#git tag -a v2.0 -m 'version 2.0'; git push --tags
#info: http://packages.python.org/distribute/setuptools.html#basic-use


from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

setup(
    name = "minpower",
    version = "4.0.0", # dont forget to increment __init__.py
    download_url = "https://github.com/adamgreenhall/minpower/zipball/v4.0.0",

    entry_points="""
    [console_scripts]
    minpower = minpower.solve:main
    standalone_minpower = minpower.solve:standaloneUC
    hyak_minpower = minpower.experiments.minpower_hyak:main
    """,

    install_requires=[
        'Coopr>=3.2.6148', #3.1.5409
        'coopr.core>=1.0',
        'pyutilib>=4.0',
        'numpy>=1.6.1',
        'pandas>=0.9.1',  #pip install --upgrade git+git://github.com/pydata/pandas.git#egg=pandas
        'python-dateutil>=1.4.1',
        'ordereddict>=1.1',
        'PyYAML>=3.10',
    ],
    tests_require=[
        'nose',
        'objgraph'
        ],

    description = "power systems optimization made beautiful",
    author = "Adam Greenhall",
    author_email = "minpower@adamgreenhall.com",
    url = "http://minpowertoolkit.com/",

    packages = find_packages(),
    keywords = ["power systems","optimization"],
    
    classifiers = [    
        "Development Status :: 4 - Beta",
        "Environment :: Other Environment",
        "Intended Audience :: Science/Research",      
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",    
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Mathematics",
        ],
    long_description = """\
power systems tools made beautiful
-----------------------------------------

* Solves ED, OPF, and UC problems.
* Problems can be defined in simple spreadsheets. 
* Visualizations are created for the answers. 
* Many solvers are supported.


* `Full documentation and tutorials <http://minpowertoolkit.com>`_
* `Actively developed <http://github.com/adamgreenhall/minpower>`_

"""
)
