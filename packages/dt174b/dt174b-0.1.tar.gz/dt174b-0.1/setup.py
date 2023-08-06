from distutils.core import setup
import os
import glob
import fnmatch
from textwrap import dedent

## Code borrowed from wxPython's setup and config files
## Thanks to Robin Dunn for the suggestion.
## I am not 100% sure what's going on, but it works!
def opj(*args):
    path = os.path.join(*args)
    return os.path.normpath(path)

def find_data_files(srcdir, *wildcards, **kw):
    # get a list of all files under the srcdir matching wildcards,
    # returned in a format to be used for install_data
 
    ## A list of partials within a filename that would disqualify it
    ## from appearing in the tarball.
    badnames = [".pyc", "~"]
    def walk_helper(arg, dirname, files):
        if 'CVS' in dirname: ## ADD/CHANGE as you need here too.
            return
        names = []
        lst, wildcards = arg
        for wc in wildcards:
            wc_name = opj(dirname, wc)
            for f in files:
                filename = opj(dirname, f)
                #if ".pyc" not in filename:
                ## This hairy looking line excludes the filename
                ## if any part of one of  badnames is in it:
                if not any(bad in filename for bad in badnames):
                    if fnmatch.fnmatch(filename, wc_name) and not os.path.isdir(filename):
                        names.append(filename)
        if names:
            lst.append( (dirname, names ) )

    file_list = []
    recursive = kw.get('recursive', True)
    if recursive:
        os.path.walk(srcdir, walk_helper, (file_list, wildcards))
    else:
        walk_helper((file_list, wildcards),
                    srcdir,
                    [os.path.basename(f) for f in glob.glob(opj(srcdir, '*'))])
    return file_list

## This is a list of files to install, and where:
## Make sure the MANIFEST.in file points to all the right 
## directories too.
#files = find_data_files('share', '*')

setup(
    author = "Jaroslav Henner",
    author_email = "jhenner@redhat.com",
    description = dedent("""\
            Python tool for interfacing the CEM DT-174B Weather Datalogger that 
            is talking on USB by some specific protocol.
            """),
    entry_points = {
        'console_scripts': [
            'dt174b = dt174b.dt174b:main'
        ]
    },
    requires = "pyusb pyaml".split(),
    keywords = "cem datalogger weather usb",
    license = "GNU GPLv3",
    name='dt174b',
    packages=['dt174b'],
    package_dir = { 'dt174b': 'dt174b' },
    package_data = {'dt174b': ['logging.conf']},
    url = 'https://github.com/jaryn/dt174b',
    download_url = 'git://github.com/jaryn/dt174b.git',
    version = '0.1',

    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Development Status :: 1 - Planning",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Atmospheric Science",
        "Topic :: System :: Hardware :: Hardware Drivers",
        "Topic :: Utilities",
        ],
)
