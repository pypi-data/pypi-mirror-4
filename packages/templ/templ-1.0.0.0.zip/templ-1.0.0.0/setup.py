import ez_setup
ez_setup.use_setuptools()

from setuptools import setup
import sys
import os
import cStringIO


### This is a lot of screwing around to populate the README for the package from
# a template we have in the templ directory.
sys.path.insert(0, "templ")
import version as templVersion
import templ
import tstreams
import texec

globs = texec.getGlobalScope()

os.chdir("misc")
readmePath = "README.txt.templ"
istream = open(readmePath, "r")
ostream = cStringIO.StringIO()
otstream = tstreams.TemplateStreamOutputStream(ostream)
templ.process(istream, otstream, globs, iname="readmePath", debug=True)
istream.close()
readme = ostream.getvalue()
otstream.close()
os.chdir("..")

lid = open("LICENSE.txt", "r")
license = lid.read()
lid.close()

setup(
    name='templ',
    version=templVersion.setuptools_string(),
    author='Brian Mearns',
    author_email='bmearns@ieee.org',
    packages=['templ',],
    url='https://bitbucket.org/bmearns/templ/',
    license=license,
    description='Template Processing Language.',
    long_description=readme,
    entry_points = {
        "console_scripts" : [
            'templ = templ.templ:main',
        ],
    },
    data_files = [
        ('misc', ['LICENSE.txt', 'README.txt', 'BUGS.txt', 'CHANGES.txt']),
    ],
)

