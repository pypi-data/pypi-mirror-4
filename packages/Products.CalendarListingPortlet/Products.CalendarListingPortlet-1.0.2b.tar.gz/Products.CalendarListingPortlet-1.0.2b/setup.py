from setuptools import setup, find_packages
import os

version = '1.0.2b'

setup(name='Products.CalendarListingPortlet',
      version=version,
      description="List events published for intranet",
      long_description=open(os.path.join("Products", "CalendarListingPortlet", "readme.txt")).read() + '\n\n' +\
          open(os.path.join("Products", "CalendarListingPortlet", "changes.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Plone",
        "Intended Audience :: End Users/Desktop",
        "Operating System :: OS Independent",
        "Topic :: Office/Business :: Groupware"
        ],
      keywords='python plone calendar presentation portlet',
      author='Nidelven IT',
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
