import os
from setuptools import setup, find_packages


def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()


setup(
    name='gears-handlebars',
    version='0.1.2',
    url='https://github.com/gears/gears-handlebars',
    license='ISC',
    author='Mike Yumatov',
    author_email='mike@yumatov.org',
    description='Handlebars compiler for Gears',
    long_description=read('README.rst'),
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
)
