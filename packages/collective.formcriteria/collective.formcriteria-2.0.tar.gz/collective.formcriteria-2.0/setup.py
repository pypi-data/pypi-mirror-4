from setuptools import setup, find_packages
import os

version = '2.0'

tests_require = ['plone.app.testing',
                 'collective.monkeypatcher',
                 'zope.testbrowser>3.3']

setup(name='collective.formcriteria',
      version=version,
      description=(
          "Add forms for user enterable search criteria to collections."),
      long_description='\n'.join(
          open(os.path.join(*path)).read() for path in [
              ("src", "collective", "formcriteria", "README.rst"),
              ("src", "collective", "formcriteria", "criteria",
               "sort.rst"),
              ("src", "collective", "formcriteria", "csv",
               "README.rst"),
              ("src", "collective", "formcriteria", "foldercontents",
               "README.rst"),
              ("docs", "HISTORY.rst"), ("docs", "TODO.rst")]),
      # Get more strings from
      # http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Ross Patterson',
      author_email='me@rpatterson.net',
      url='http://pypi.python.org/pypi/collective.formcriteria',
      license='GPL',
      packages=find_packages('src', exclude=['ez_setup']),
      package_dir={'': 'src'},
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'Plone',
          'plone.browserlayer',
      ],
      tests_require=tests_require,
      extras_require={'tests': tests_require,
                      'chameleon': 'five.pt>2.1.1'},
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
