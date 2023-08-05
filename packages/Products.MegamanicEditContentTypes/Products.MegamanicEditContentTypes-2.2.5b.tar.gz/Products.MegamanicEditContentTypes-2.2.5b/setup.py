from setuptools import setup, find_packages
import os

version = '2.2.5b'

setup(name='Products.MegamanicEditContentTypes',
      version=version,
      description="Various content types that are usable in the MegamanicEdit framework",
      long_description=open(os.path.join("Products", "MegamanicEditContentTypes", "readme.txt")).read() + "\n\n" + \
          open(os.path.join("Products", "MegamanicEditContentTypes", "changes.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Plone",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Topic :: Communications :: Email",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Office/Business :: Groupware",
        ],
      keywords='python zope plone archetypes content megamanicedit',
      author='Morten W. Petersen',
      author_email='info@nidelven-it.no',
      url='http://www.nidelven-it.no/d',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'email_backport>=4.0.3b',
          'Products.RFC822AddressFieldValidator',
          'VariousDisplayWidgets>=0.1',
          'MegamanicEdit>=2.0.2',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
