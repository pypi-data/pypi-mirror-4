from distutils.core import setup
import tikidb.TikiDB
setup(
    name='TikiDB',
    version='0.1.0',
    author='Matthew Kasfeldt',
    author_email='mkasfeldt@data-hut.com',
    url='http://',
    packages=['tikidb','examples',],
    license='LICENSE.txt',
    description='A framework to create, maintain and search ZODBs',
    long_description=open('README.txt').read(),
    requires=["ZODB3 (>= 3.10.3)"],
)
