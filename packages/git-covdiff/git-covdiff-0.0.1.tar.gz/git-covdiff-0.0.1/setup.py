import os
from setuptools import setup, find_packages

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="git-covdiff",
    version="0.0.1",
    author="Yusuke MURAOKA",
    author_email="yusuke@nttmcl.com",
    description="Highlight newly appeared coverage missing in latest changeset in git.",
    entry_points={
        'console_scripts': [
            'git-covdiff = gitcovdiff:main',
        ]
    },
    license="BSD",
    keywords="git coverage",
    url="https://github.com/nttmcl/git-covdiff",
    packages=find_packages(),
    install_requires=["coverage>=3.6b1", "pygit2>=0.17.3"],
    long_description=read('README.rst'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)
