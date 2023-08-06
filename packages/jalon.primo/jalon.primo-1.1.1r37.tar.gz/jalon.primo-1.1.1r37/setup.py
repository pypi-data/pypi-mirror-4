# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os

version = '1.1.1r37'

setup(name='jalon.primo',
      version=version,
      description="Primo connecteur",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='',
      author='Bordonado Christophe - Université Nice Sophia Antipolis (uns) Service TICE/ Jean Bado - Université Versaille Saint-Quentin(UVSQ)',
      author_email='tice@unice.fr',
      url='http://unice.fr',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['jalon'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      setup_requires=["PasteScript"],
      paster_plugins=["ZopeSkel"],
      )
