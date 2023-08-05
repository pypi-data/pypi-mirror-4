from setuptools import setup
#from distutils.core import setup # for 'flat' install
    
setup(
    name = "valstream",
    version = "0.0.5",

    # scripts = ["valstream.py"],
    entry_points="""
    [console_scripts]
    valstream = valstream:_main
    """,

    packages=['valstream'],

    license = "LGPL",
    description = "Generalization of Unix pipeline to jsonable data",
    author = "tengu",
    author_email = "karasuyamatengu@gmail.com",
    url = "https://github.com/tengu/py-valstream",

    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Environment :: Console",
        "Programming Language :: Python",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP", 
        "Topic :: Text Processing :: Filters", 
        "Topic :: Utilities", 
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
    long_description="""
""",
    )
