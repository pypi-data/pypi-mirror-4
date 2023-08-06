#!/usr/bin/env python
"""
wnyc_recommender
======

WNYC's Recommendation engine
"""

from setuptools import setup

setup(
    name='wnyc_recommender',
    version='0.0.0',
    author='Adam DePrince',
    author_email='adeprince@nypublicradio.org',
    description='Recommender',
    long_description=__doc__,
    py_modules = [
        "wnyc_recommender/__init__",
        "wnyc_recomemnder/server",
        "wnyc_recommender/fetcher",
        "wnyc_recommender/engine",
        ],
    packages = ["wnyc_recommender"],
    zip_safe=True,
    license='GPL',
    include_package_data=True,
    classifiers=[
        ],
    scripts = [
        'scripts/wnyc_recommendation_engine',
        ],
    url = "https://github.com/wnyc/recommender",
    install_requires = [
        "crab",
        "gevent",
        "python-gflags",
        "numpy",
        "scikits.learn",
        ]
)

