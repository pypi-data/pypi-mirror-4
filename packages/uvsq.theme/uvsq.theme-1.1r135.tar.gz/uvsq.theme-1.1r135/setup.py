from setuptools import setup, find_packages
import os

version = '1.1r135'

setup(name='uvsq.theme',
      version=version,
      description="An installable theme for Plone 3",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='',
      author='Jerome Navarro (Universite Nice Sophia Antipolis UNS), Bordonado Christophe (UNS)',
      author_email='tice@unice.fr',
      url='http://svn.plone.org/svn/collective/',
      license='CECILL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['uvsq'],
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
