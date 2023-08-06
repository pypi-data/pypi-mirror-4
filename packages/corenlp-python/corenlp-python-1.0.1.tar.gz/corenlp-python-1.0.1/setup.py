from distutils.core import setup

PACKAGE = "corenlp"
NAME = "corenlp-python"
DESCRIPTION = "A Stanford Core NLP wrapper"
AUTHOR = "Hiroyoshi Komatsu"
AUTHOR_EMAIL = "hiroyoshi.komat@gmail.com"
URL = "https://bitbucket.org/torotoki/corenlp-python"
VERSION = "1.0.1"

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=open("README.md").read(),
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    # packages=['corenlp']
    # package_data=find_package_data(
    #     PACKAGE,
    #     only_in_packages=False
    # )
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
        "Programming Language :: Python",
    ],
    zip_safe=False,
)