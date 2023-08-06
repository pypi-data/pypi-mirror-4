from setuptools import setup, find_packages

setup(
    name='python-boxcar',
    version='0.1.1',
    packages=find_packages(),
    install_requires=['requests>=1.1.0'],
    author='Mark Caudill',
    author_email='mark@markcaudill.me',
    description='A Boxcar.io API library.',
    license='GPLv3',
    keywords='boxcar api notify',
    url='https://github.com/markcaudill/boxcar')
