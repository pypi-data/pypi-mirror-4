from setuptools import setup

setup(
    name='pinscher',
    version='0.1dev',
    author='William Mayor',
    author_email='mail@williammayor.co.uk',
    url='http://pinscher.williammayor.co.uk',
    license='LICENSE.txt',
    description='Core utilities for interacting with pinscher password files',
    long_description=open('README.txt').read(),
    install_requires=['pycrypto', ],
    packages=['pinscher', 'pinscher.test', ],
    test_suite='pinscher.test',
    scripts=['scripts/pinscher-cli', 'scripts/pinscher-alfred']
)
