from setuptools import setup, find_packages
import sys, os

# Hack to prevent TypeError: 'NoneType' object is not callable error
# on exit of python setup.py test
try:
    import multiprocessing
except ImportError:
    pass

version = '0.2'

setup(name='sqla_declarative',
      version=version,
      description="Extended SQLAlchemy declarative_base class",
      long_description=open('README.rst').read().split('Build Status')[0],
      classifiers=[
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: SQL',
        'Topic :: Database',
        'Topic :: Database :: Front-Ends',
      ],
      keywords='',
      author='Aur\xc3\xa9lien Matouillot',
      author_email='a.matouillot@gmail.com',
      url='https://github.com/LeResKP/sqla_declarative',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          "sqlalchemy >= 0.7",
          "tw2.sqla",
      ],
      test_suite = 'nose.collector',
      tests_require=[
          'nose',
          "zope.sqlalchemy >= 0.4",
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
