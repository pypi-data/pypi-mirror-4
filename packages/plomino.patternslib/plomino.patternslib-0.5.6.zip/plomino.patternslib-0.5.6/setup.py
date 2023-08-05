from setuptools import setup, find_packages
import os

version = '0.5.6'

long_description = (
    open('README.rst').read()
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    open('docs/CONTRIBUTORS.txt').read()
    + '\n' +
    open('docs/CHANGES.txt').read()
    + '\n')

setup(name='plomino.patternslib',
      version=version,
      description="A Plomino plugin that provides fields and other form elements built using the Patterns javascript library.",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='Plomino, Patternslib, Patterns, Javascript, Fields',
      author='Fulvio Casali',
      author_email='fulviocasali@gmail.com',
      url='https://github.com/plomino/plomino.patternslib',
      license='gpl',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['plomino', ],
      package_data={'': ['docs/*']},
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'distribute',
          # -*- Extra requirements: -*-
      ],
      extras_require={'test': ['plone.app.testing']},
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      setup_requires=["PasteScript"],
      paster_plugins=["templer.localcommands"],
      )
