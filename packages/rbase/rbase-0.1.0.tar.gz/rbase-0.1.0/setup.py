"""
rbase
-----

A simple redis base class.
"""
from setuptools import setup


setup(
    name='rbase',
    version='0.1.0',
    url='http://github.com/jarodl/rbase',
    license='MIT',
    author='Jarod Luebbert',
    author_email='jarodluebbert@gmail.com',
    description='',
    long_description=__doc__,
    zip_safe=False,
    platforms='any',
    install_requires=['redis'],
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
