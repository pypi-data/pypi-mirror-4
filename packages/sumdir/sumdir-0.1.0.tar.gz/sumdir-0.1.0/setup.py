# -*- encoding: utf-8 -*-

from setuptools import setup, find_packages

version = '0.1.0'

setup(name='sumdir',
    version=version,
    description="Display sizes of the current subdirectories",
    long_description="""\
Display sizes of the current subdirectories""",
    # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Intended Audience :: Developers",
        "Environment :: Console",
        "Development Status :: 4 - Beta",
        "Programming Language :: Python",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],
    keywords='',
    author='Ginés Martínez Sánchez',
    author_email='ginsmar at artgins.com',
    url='artgins.com',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # -*- Extra requirements: -*-
    ],
    entry_points="""
        [console_scripts]
        sumdir = sumdir:main
    """,
)
