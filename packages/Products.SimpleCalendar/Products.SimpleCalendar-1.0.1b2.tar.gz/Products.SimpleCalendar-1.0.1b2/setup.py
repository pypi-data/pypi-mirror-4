from setuptools import setup, find_packages
import os

version = '1.0.1b2'

setup(name='Products.SimpleCalendar',
      version=version,
      description="Simple to install and use calendaring solution",
      long_description=open(os.path.join("Products", "SimpleCalendar", "readme.txt")).read() + '\n\n' + \
          open(os.path.join("Products", "SimpleCalendar", "changes.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Framework :: Plone :: 4.1",
        "Operating System :: OS Independent",
        "Topic :: Office/Business :: Groupware",
        "Topic :: Office/Business :: Scheduling",
        ],
      keywords='python zope plone calendaring calendar events',
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

          'dateable.chronos==0.8',
          'dateable.kalends==0.5',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
