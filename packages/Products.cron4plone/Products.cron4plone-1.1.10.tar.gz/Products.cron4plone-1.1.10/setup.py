from setuptools import setup, find_packages
import os

version = '1.1.10'

setup(name='Products.cron4plone',
      version=version,
      description="cron4plone can do scheduled tasks in Plone",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='crontab plone cron scheduling',
      author='Goldmund, Wyldebeast & Wunderliebe',
      author_email='info@gw20e.com',
      url='http://www.gw20e.com/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
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
