from distutils.core import setup

setup(
    name='impermagit',
    version='1.0.0',
    author='Edmund Jorgensen',
    author_email='edmund@hut8labs.com',
    packages=['impermagit', 'impermagit.test'],
    url='http://pypi.python.org/pypi/impermagit/',
    license='LICENSE.txt',
    description='Create temporary git repos in python.',
    long_description=open('README.txt').read(),
    install_requires=[],
)
