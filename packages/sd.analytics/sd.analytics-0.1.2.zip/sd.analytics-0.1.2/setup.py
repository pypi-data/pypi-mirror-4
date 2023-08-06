from setuptools import setup, find_packages
import os

version = '0.1.2'

setup(name='sd.analytics',
      version=version,
      description="Google analytics integration for Singing & Dancing",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='google analytics singing dancing newsletter trackingaddon extension',
      author='Thomas Clement Mogensen',
      author_email='thomas@headnet.dk',
      url='http://www.headnet.dk',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['sd'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'collective.dancing',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
