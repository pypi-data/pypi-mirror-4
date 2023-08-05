from setuptools import setup, find_packages
import sys, os

version = '0.2'

README = open(os.path.join(os.path.dirname(__file__), 'README')).read()
                           
setup(name='repoze.who.cas',
      version=version,
      description="a CAS plugin for repoze.who",
      long_description=README,
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='CAS authentication repoze.who',
      author='Matthew J. Desmarais',
      author_email='matthew.desmarais@gmail.com',
      url='',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        "webob>=0.9.6.1",
        "pycrypto>=2.0.1",
        ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
