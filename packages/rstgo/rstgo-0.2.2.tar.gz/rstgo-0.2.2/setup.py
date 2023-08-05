#!/usr/bin/env python

from setuptools import setup

setup(
    name='rstgo',
    version='0.2.2',
    description='A package to render go diagrams and embed them in reStructuredText documents',
    long_description=open('README.txt').read(),
    author='J. Cliff Dyer',
    author_email='jcd@sdf.lonestar.org',
    url='http://bitbucket.org/cliff/rstgo',
    packages=['rstgo'],
    package_data={'rstgo': ['resources/*/*.png', 'examples/*']},
    scripts=['bin/rst2html+go.py'],
    license='LICENSE.txt',
    install_requires=[
        'docutils',
        'pillow',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Topic :: Documentation',
        'Topic :: Games/Entertainment :: Board Games',
        'Topic :: Games/Entertainment :: Turn Based Strategy',
    ],
)
