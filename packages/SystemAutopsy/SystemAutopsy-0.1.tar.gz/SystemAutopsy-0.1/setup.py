#! /usr/bin/env python

from setuptools import setup, find_packages

setup(name="SystemAutopsy",
      version="0.1",
      author="Rory McCann",
      author_email="rory@technomancy.org",
      packages=['system_autopsy'],
      licence='GPLv3+',
      description="Extensible tool to take a snapshot of important things a system is doing while you're firefighting",
      entry_points = {
          'console_scripts': [
              'autopsy = system_autopsy:main',
          ]
      },
)
