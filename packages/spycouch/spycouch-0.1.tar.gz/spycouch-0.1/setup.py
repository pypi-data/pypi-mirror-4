from distutils.core import setup

setup(
    name='spycouch',
    version='0.1',
    author='Cerny Jan',
    author_email='cerny.jan@hotmail.com',
    packages=['spycouch',],
    url='http://pypi.python.org/pypi/spycouch/',
    license='LICENSE.txt',    
    description='Client in python for CouchDB',
    long_description=open('README.txt').read(),
)