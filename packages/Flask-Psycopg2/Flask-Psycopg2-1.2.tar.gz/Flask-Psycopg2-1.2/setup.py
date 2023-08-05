"""
Flask-Psycopg2  
-------------

Flask extension for Python's postgresql adapter Psycopg2
"""
from setuptools import setup


setup(
    name='Flask-Psycopg2',
    version='1.2',
    url='http://example.com/flask-psycopg2/',
    license='Public Domain',
    author='Stefan Brink',
    author_email='brefan@gmail.com',
    description='postgresql adapter for Flask',
    long_description=__doc__,
    py_modules=['flask_psycopg2'],
    # if you would be using a package instead use packages instead
    # of py_modules:
    # packages=['flask_psycopg2'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask',
        'Psycopg2'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: Public Domain',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
