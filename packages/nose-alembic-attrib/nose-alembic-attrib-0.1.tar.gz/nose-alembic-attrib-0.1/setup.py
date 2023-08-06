#!/usr/bin/env python

from setuptools import *

setup(
    name='nose-alembic-attrib',
    version='0.1',
    description='Alembic attributes for nose',
    long_description='This is a nose plugin for adding alembic related attributes.',
    author='Jonathan Sokolowski',
    author_email='jonathan.sokolowski@gmail.com',
    url='https://github.com/jsok/nose-alembic-attrib',
    license='BSD',
    packages=find_packages(exclude=['test', 'test.*']),
    install_requires=['setuptools', 'nose>=1.2.0', 'alembic>=0.4.2'],
    entry_points='''
        [nose.plugins.0.10]
        nose_alembic_attrib = nose_alembic_attrib.alembic_attrib:AlembicAttrib
        ''',
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Testing",
    ],
    keywords='test nosetests nose nosetest plugin alembic sqlalchemy',
)
