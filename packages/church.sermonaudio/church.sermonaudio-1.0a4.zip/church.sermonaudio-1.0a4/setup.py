from setuptools import setup, find_packages
import os

version = '1.0a4'

setup(name='church.sermonaudio',
      version=version,
      description="Sermon Audio",
      long_description=open("README.txt").read() + "\n" +
                     open(os.path.join("docs", "HISTORY.txt")).read() + "\n" +
                     open(os.path.join("docs", "INSTALL.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='audio,archive,sermon',
      author='David Bain',
      author_email='david@alteroo.com',
      url='http://svn.plone.org/svn/collective/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['church'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.app.dexterity',
          'plone.namedfile [blobs]',
          'collective.mediaelementjs',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      # The next two lines may be deleted after you no longer need
      # addcontent support from paster and before you distribute
      # your package.
      # setup_requires=["PasteScript"],
      # paster_plugins = ["ZopeSkel"],

      )
