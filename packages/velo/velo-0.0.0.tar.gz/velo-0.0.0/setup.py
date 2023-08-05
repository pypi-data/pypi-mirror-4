#!/usr/bin/env python

import setuptools

if not getattr(setuptools, "_distribute", False):
    raise SystemExit("Setuptools is not supported. Please install Distribute (create your virtualenv with --distribute)")

setup_requires = [
    # d2to1 bootstrap
    'd2to1',

    # Testing dependencies (the application doesn't need them to *run*)
    'nose',
    'nosexcover',
    'coverage',
    'mock',
    'webtest'
]


dependency_links=[
    'https://crate.io/',
]


setuptools.setup(
    setup_requires=setup_requires,
    d2to1=True,
    dependency_links=dependency_links,
    package_data={"velo": [
        "templates/*.*",
        "templates/*/*.*",
        "static/*.*",
        "static/*/*.*",
        "static/*/*/*.*",
    ]},
    entry_points = """\
        [paste.app_factory]
        main = velo:main
    """
)
