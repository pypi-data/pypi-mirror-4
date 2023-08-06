#   @author         Martin Gergov    <martingergov1@gmail.com>
#   @license        MIT/X11

from setuptools import setup, find_packages
import os

VERSION = {
    'major' : 0,
    'minor' : 0,
    'patch' : 2,
    }

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
        name            = 'ringbuffer',
        version         = '%(major)i.%(minor)i.%(patch)s' % VERSION,
        description     = """Random access associative ring buffer""",
        author          = 'Martin Gergov',
        author_email    = 'martingergov1@gmail.com',
        packages        = ['ringbuffer'],
        license         = 'MIT/X11',
        download_url    = 'https://bitbucket.org/marto1/ringbuffer/',
        keywords        = ["ring buffer", "container"],
        long_description=read('README.rst'),
        classifiers     = [
            'License :: OSI Approved :: MIT License',
            'Topic :: Utilities',
            'Programming Language :: Python :: 2.7'
            ],
    )
