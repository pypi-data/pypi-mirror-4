"""
Flask-MetaRoute
-------------

Flask-MetaRoute adds some useful decorators for routing
"""
from setuptools import setup

setup(
    name='Flask-MetaRoute',
    version='1.0',
    url='http://code.google.com/p/flask-metaroute/',
    license='BSD',
    author='Orca',
    author_email='deep.orca@gmail.com',
    description='Extra routing capabilities for Flask',
    long_description=__doc__,
    packages=['flask_metaroute'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)