#!/usr/bin/env python

#from setuptools import setup, find_packages
from distutils.core import setup

setup(name='python-audiodb',
      version='0.1',
      description='To manage song library',
      author='dal',
      author_email='kedals0@gmail.com',
      url='http://pyaudiodb.tuxfamily.org/',
#      packages=find_packages("audiodb"), #["audiodb.core","audiodb.model"],
      packages=["audiodb","audiodb.core","audiodb.model"],
      license="GPLv3",
      classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Topic :: Multimedia :: Sound/Audio :: Players',
        'Topic :: Software Development :: Libraries :: Python Modules'],
      long_description=""" python-audiodb is a library to manage audio song via database.  It
offers several default tables such as play, stop, seek events but you
can easily add new tables.

It generates an audioprint (based on chromaprint) and uses it as the
song id in database. This permits to be stable over file moving,
renaming, tagging and maybe more ...

A cli client is provided to get some information from database. """
      )
