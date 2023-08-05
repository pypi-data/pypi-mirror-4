from setuptools import setup, find_packages
import os

version = '1.0b1'

setup(name='buildout.sanitycheck',
      version=version,
      description="Sanity checks for buildout environment.",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Buildout :: Extension",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        ],
      keywords='',
      author='Steve McMahon',
      author_email='steve@dcn.org',
      url='http://svn.plone.org/svn/collective/',
      license='GPLv2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['buildout'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
      ],
      entry_points={
        'zc.buildout.extension': ['ext = buildout.sanitycheck:main'],
      },
      )
