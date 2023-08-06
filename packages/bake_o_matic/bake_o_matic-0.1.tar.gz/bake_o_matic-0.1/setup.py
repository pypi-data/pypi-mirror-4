from setuptools import setup, Extension

setup(
    name='bake_o_matic',
    version='0.1',

    py_modules = ["bake_o_matic"],

    license = "LGPL",
    description = "baker boilerplate reduction",
    long_description="""import bake_o_matic at the end of a script to turn it into a baked command script.

$ cat say.py
#!/usr/bin/python

def hi(msg, **opt):
    "greet"
    print 'OH HAI', msg, opt

import bake_o_matic

$ ./say.py 
Usage: ./say.py COMMAND <options>

Available commands:
 hi  greet

Use './say.py <command> --help' for individual command help.


$ ./say.py hi ho
OH HAI ho {}


""",
    author = "tengu",
    author_email = "karasuyamatengu@gmail.com",
    # url = "https://github.com/tengu/bake_o_matic",
    # test_suite='nose.collector',
    # tests_require=['nose'],
)
