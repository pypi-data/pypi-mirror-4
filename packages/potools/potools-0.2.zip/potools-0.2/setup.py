import os
from setuptools import setup, find_packages

version = '0.2'

setup(name='potools',
      version=version,
      description="Python scripts to help with managing translations",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "changes.rst")).read(),
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Wolfgang Thomas, Manuel Reinhardt, JC Brand',
      author_email='info@syslab.com',
      url='http://syslab.com',
      license='GPL',
      namespace_packages=['potools'],
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'polib',
          'mr.developer',
          'translate-toolkit',
      ],
      extras_require={
          'test': ['z3c.testsetup'],
      },
      entry_points="""
      [console_scripts]
      podiff = potools.podiff:main
      pogetnew = potools.poget:main
      pocheck = potools.pocheck:main
      """,
      )
