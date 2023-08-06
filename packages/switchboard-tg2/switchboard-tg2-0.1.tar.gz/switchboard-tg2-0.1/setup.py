# -*- coding: utf-8 -*-
import os

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

install_requires = [
    "TurboGears2 >= 2.1.4",
    "tg.devtools",
    "tgext.pluggable",
    "switchboard",
]

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.rst')).read()
except IOError:
    README = ''

setup(
    name='switchboard-tg2',
    version='0.1',
    description='',
    long_description=README,
    author='Kyle Adams',
    author_email='kadams54@users.sourceforge.net',
    url='http://sf.net/projects/switchboard-tg2',
    keywords='turbogears2.application',
    setup_requires=["PasteScript >= 1.7"],
    paster_plugins=[],
    packages=find_packages(exclude=['ez_setup']),
    install_requires=install_requires,
    include_package_data=True,
    entry_points="""
    """,
    dependency_links=[
        "http://www.turbogears.org/2.1/downloads/current/"
        ],
    zip_safe=False
)
