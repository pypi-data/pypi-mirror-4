import os
from os.path import join
from setuptools import setup, find_packages

def read(*pathnames):
    return open(os.path.join(os.path.dirname(__file__), *pathnames)).read()

name = 'eea.eggmonkeytesttarget'
path = name.split('.') + ['version.txt']
version = open(join(*path)).read().strip()

setup(name=name,
        version=version,
        description="A dummy package to test eea.eggmonkey",
        long_description='\n'.join([
            read('docs', 'README.txt'),
            read('docs', 'HISTORY.txt'),
            ]),
        classifiers=[
            "Programming Language :: Python",
            ],
        keywords='buildout',
        author='Tiberiu Ichim',
        author_email='tiberiu@eaudeweb.ro',
        url='https://svn.eionet.europa.eu/repositories/Zope/trunk/eea.eggmonkeytesttarget',
        license='GPL',
        packages=find_packages(),
        namespace_packages=['eea'],
        include_package_data=True,
        zip_safe=False,
        install_requires=['setuptools'],
        )
