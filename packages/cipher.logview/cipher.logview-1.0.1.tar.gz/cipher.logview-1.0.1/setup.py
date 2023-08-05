###############################################################################
#
# Copyright 2012 by CipherHealth, LLC
#
###############################################################################

import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


setup(
    name='cipher.logview',
    version='1.0.1',
    author='CipherHealth LLC',
    author_email='dev@cipherhealth.com',
    license='MIT',
    url='https://github.com/CipherHealth/cipher.logview',
    description="WSGI middleware that shows you log messages"
                " produced during request handling.",
    long_description=read('README.rst') + '\n\n' + read('CHANGES.rst'),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2.7',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope3',
    ],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Dozer',
        'Paste', # Dozer also requires it
    ],
    extras_require={
        'test': [
            'zope.browserpage',     # for test_pagetemplate.py
            'zope.app.publication', # for test_publication.py
        ],
    },
    entry_points={
        'paste.filter_factory': [
            'main = cipher.logview.middleware:logview_filter_factory',
        ],
    },
)
