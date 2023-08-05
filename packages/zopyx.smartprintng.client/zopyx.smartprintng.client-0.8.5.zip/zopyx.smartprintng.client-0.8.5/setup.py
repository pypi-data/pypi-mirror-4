##########################################################################
# zopyx.smartprintng.client - client library for the SmartPrintNG server
# (C) 2009, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################


from setuptools import setup, find_packages
import os

version = '0.8.5'

setup(name='zopyx.smartprintng.client',
      version=version,
      url='http://pypi.python.org/pypi/zopyx.smartprintng.client',
      description="ZOPYX SmartPrintNG Client Library",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='Produce Publish Python Zope Plone PDF',
      author='Andreas Jung',
      author_email='info@zopyx.com',
      license='ZPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['zopyx', 'zopyx.smartprintng'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
