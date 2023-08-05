# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

long_desc = open('README').read()

requires = ['Sphinx>=0.6', 'mercurial>=1.8' ]

setup(
    name='sphinxcontrib-mercurial',
    version='0.1',
    url='http://bitbucket.org/cointoss1973/sphinxcontrib-mercurial',
    download_url='http://pypi.python.org/pypi/sphinxcontrib-mercurial',
    license='GPLv3',
    author='Takayuki KONDO',
    author_email='tkondou@gmail.com',
    description='Sphinx "mercurial" extension',
    long_description=long_desc,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Documentation',
        'Topic :: Utilities',
    ],
    platforms='any',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires,
    namespace_packages=['sphinxcontrib'],
)
