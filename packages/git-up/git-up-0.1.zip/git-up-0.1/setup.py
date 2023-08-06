# coding=utf-8
from setuptools import setup, find_packages

README = None
with open('README.rst', 'r') as f:
    README = f.read()

setup(
    name = "git-up",
    version = "0.1",
    packages = find_packages(),
    scripts = ['PyGitUp/gitup.py'],
    install_requires = ['GitPython', 'colorama', 'termcolor'],

    entry_points = {
        'console_scripts': [
            'git-up = gitup:run'
        ]
    },

    package_data = {
        # If any package contains *.txt or *.md files, include them:
        '': ['*.txt', '*.md', 'LICENCE', 'check-bundler.rb']
    },

    # development metadata
    use_2to3 = True,
    zip_safe = True,

    # metadata for upload to PyPI
    author = "Markus Siemens",
    author_email = "markus@m-siemens.de",
    description = "A python implementation of 'git up'",
    license = "MIT",
    keywords = "git git-up",
    url = "https://github.com/msiemens/PyGitUp",
    classifiers  = [
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Topic :: Software Development :: Version Control",
        "Topic :: Utilities"
    ],
    bugtrack_url = 'https://github.com/msiemens/PyGitUp/issues',

    long_description = README
    # could also include download_url etc.
)
