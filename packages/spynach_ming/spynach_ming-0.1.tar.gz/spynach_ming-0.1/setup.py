from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='spynach_ming',
    version=version,
    description="Ming MongoDB ODM plugin for Spynach web framework",
    long_description="""\
Ming MongoDB ODM plugin for Spynach web framework
""",
    classifiers=["Development Status :: 5 - Production/Stable",
                 "License :: OSI Approved :: GNU General Public License (GPL)",
                 "Environment :: Web Environment"],
    keywords='spynach mongodb ming odm',
    author='Simone Marzola',
    author_email='marzolasimone@gmail.com',
    url='http://simock85.github.com/spynach.ming/',
    license='GPL',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    data_files=[('', ['README.rst'])],
    zip_safe=False,
    install_requires=[
        'spynach',
        'paste',
        'ming',
    ],
    entry_points="""
      # -*- Entry points: -*-
      """,
)
