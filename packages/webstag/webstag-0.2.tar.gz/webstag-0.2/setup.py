#!/usr/bin/env python
# vim: set fileencoding=utf-8 expandtab tabstop=4 shiftwidth=4 :

from setuptools import setup, find_packages


setup(  name = "webstag",
        version = "0.2",
        # Metadata
        description = "Generate static HTML galleries with photos and videos",
        long_description = open("README.txt").read(),
        author = "Aurelien Bompard",
        author_email = "aurelien@bompard.org",
        url = "https://gitorious.org/webstag",
        license = "GPLv3+",
        classifiers = [
            "Development Status :: 5 - Production/Stable",
            "Environment :: Console",
            "Environment :: Web Environment",
            "Intended Audience :: End Users/Desktop",
            "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
            "Topic :: Multimedia :: Graphics :: Viewers",
            "Topic :: Multimedia :: Video",
        ],
        # Content
        packages = find_packages(),
        include_package_data = True,
        zip_safe = False, # template files
        # Dependances
        install_requires = [
            "PyYAML",
            "jinja2",
        ],
        # Scripts
        entry_points = {
            "console_scripts": [
                "webstag = webstag:main",
            ],
        },
     )
