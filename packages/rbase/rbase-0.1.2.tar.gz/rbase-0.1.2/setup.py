"""
rbase
-----

A simple redis base class.
"""
from setuptools import setup, find_packages


setup(
    name='rbase',
    version='0.1.2',
    url='http://github.com/jarodl/rbase',
    license='MIT',
    author='Jarod Luebbert',
    author_email='jarodluebbert@gmail.com',
    description='A simple redis base class',
    packages=find_packages(),
    long_description=__doc__,
    zip_safe=False,
    platforms='any',
    install_requires=['redis'],
    include_package_data=True,
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
