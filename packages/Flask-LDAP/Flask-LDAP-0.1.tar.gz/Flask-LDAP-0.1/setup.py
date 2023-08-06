# coding=utf-8
"""
Flask-LDAP
-------------

This is the description for that library
"""
from setuptools import setup


setup(
    name='Flask-LDAP',
    version='0.1',
    url='https://bitbucket.org/ellersseer/flask-ldap/',
    license='BSD',
    author='Dmitry Zhiltsov',
    author_email='dzhiltsov@me.com',
    description='Flask extension for LDAP auth and profile user',
    long_description=__doc__,
    py_modules=['flask_ldap'],
    packages=['flask_ldap'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask', 'python-ldap'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
