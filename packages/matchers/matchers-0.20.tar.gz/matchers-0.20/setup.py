# -*- coding: utf-8 -*-

import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, u'README.rst')).read()
requires = open(os.path.join(here, 'reqs.txt')).read().splitlines()

setup(
    name=u'matchers',
    description=u'Collection of highly reusable hamcrest matchers',
    version=u'0.20',
    long_description=README + u'\n',
    classifiers=[
        u"Programming Language :: Python",
        u"Topic :: Software Development :: Testing",
        u"Operating System :: OS Independent",
        u"Intended Audience :: Developers",
    ],
    install_requires=requires,
    packages=find_packages(),
    test_suite=u'nose.collector',
    url=u'https://github.com/grupotaric/matchers',
    download_url=u'https://github.com/grupotaric/matchers/tags',
    author=u'Taric S.A.',
    author_email=u'appregs@taric.es',
)
