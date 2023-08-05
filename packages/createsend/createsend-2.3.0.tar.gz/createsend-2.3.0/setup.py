import sys
import os
from distutils.core import setup

from createsend import __version__

setup(name = "createsend",
      version = __version__,
      description = "A library which implements the complete functionality of v3 of the createsend API.",
      author = "James Dennes",
      author_email = 'jdennes@gmail.com',
      packages = ['createsend'])
