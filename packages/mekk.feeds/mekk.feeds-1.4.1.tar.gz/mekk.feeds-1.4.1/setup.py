# -*- coding: utf-8 -*-
# (c) 2008, Marcin Kasperski

from setuptools import setup, find_packages

version = '1.4.1'
long_description = open("README.txt").read()
classifiers = [
    "Programming Language :: Python",
    "Intended Audience :: Developers",
    "Topic :: Software Development :: Libraries :: Python Modules",
    # TODO: Development Status, Environment, Topic
    ]

setup(name='mekk.feeds',
      version=version,
      description="RSS scripting",
      long_description=long_description,
      classifiers=classifiers,
      keywords='org',
      license='BSD',
      author='Marcin Kasperski',
      author_email='Marcin.Kasperski@mekk.waw.pl',
      url='http://mekk.waw.pl/',
      package_dir={'':'src'},
      packages=find_packages('src', exclude=['ez_setup', 'examples', 'tests']),
      namespace_packages = ['mekk'],
      test_suite = 'nose.collector',
      include_package_data = True,
      package_data = {
        'mekk': [
            'README.txt',
            'LICENSE.txt',
            'doc/usage.txt',
            ],
        },
      zip_safe = True,
      install_requires=[
        'lxml', 'simplejson', 'keyring', 'mekk.greader',
      ],
      tests_require=[
        'nose',
        ],
      entry_points = """
[console_scripts]
greader2org = mekk.feeds.greader2org.run:main
""",
)
