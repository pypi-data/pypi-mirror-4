#!/usr/bin/env python
from setuptools import setup, find_packages
setup(
    name="pbundler",
    version="0.0.5",
    packages=find_packages(),
    zip_safe=False,
    install_requires=['virtualenv>=1.7', 'distribute', 'pip>=1.1'],
    package_data={
        '': ['*.md'],
    },
    entry_points={
        'console_scripts': [
            'pbundle = PBundler.entrypoints:pbcli',
            'pbundle-py = PBundler.entrypoints:pbpy',
        ],
    },

    # metadata for upload to PyPI
    author="Christian Hofstaedtler",
    author_email="ch--pypi@zeha.at",
    description="Bundler for Python",
    license="MIT",
    keywords="bundler bundle pbundler pbundle dependency dependencies management virtualenv pip packages",
    url="http://github.com/zeha/pbundler/",
    download_url="https://github.com/zeha/pbundler/downloads",
)
