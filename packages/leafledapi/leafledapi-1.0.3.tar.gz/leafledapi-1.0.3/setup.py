from distutils.core import setup
setup(
    name = "leafledapi",
    packages = ["leafledapi"],
    version = "1.0.3",
    description = "Leafled REST-API Library and CLI",
    author = "Bastian Bense",
    author_email = "bb@neo.de",
    url = "http://leafled.de/",
    keywords = ["leafled", "i18n", "json", "publishing"],
    requires = ['requests'],
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 1 - Planning",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Environment :: Web Environment"
        ],
    long_description = """\
Leafled REST-API Library and CLI
-------------------------------------

The official Leafled API and Command Line Interface (CLI) for automating the Leafled Portal Server.

More information at:
http://leafled.de/
"""
)
