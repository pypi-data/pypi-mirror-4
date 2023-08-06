# quidditas setup.py
from distutils.core import setup
import quidditas

setup(
    name = "quidditas",
    packages = ["quidditas"],
    version= quidditas.__version__,
    description = "Entity framework for games",
    author = "Dominik Schacht",
    author_email = "domschacht@gmail.com",
    url = "http://quidditas.googlecode.com/",
    keywords = ["entity", "entities", "games"],
    license = "BSD",
    download_url = "https://quidditas.googlecode.com/files/quidditas-0.9.tar.gz",
    classifiers = [
        "License :: OSI Approved :: BSD License",
        "Intended Audience :: Developers",
        "Development Status :: 4 - Beta",
        "Topic :: Games/Entertainment",
    ]

)


