from setuptools import setup, find_packages
import os

version = '1.0.1'

setup(name='Products.FakeZopeUser',
      version=version,
      description="A product that enables faking another logged-in user.",
      long_description=open(os.path.join("Products", "FakeZopeUser", "readme.txt")).read() + '\n\n' + \
          open(os.path.join("Products", "FakeZopeUser", "changes.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Zope2",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries",
        ],
      keywords='python zope zope2 authentication',
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
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
