from setuptools import setup, find_packages

setup(
    name='python-boxcar',
    version='0.1.2',
    packages=find_packages(),
    install_requires=['requests>=1.1.0'],
    scripts=[
        'bin/boxcar-subscribe.py',
        'bin/boxcar-notify.py',
        'bin/boxcar-broadcast.py'],
    author='Mark Caudill',
    author_email='mark@markcaudill.me',
    description='A Boxcar.io API library.',
    license='GPLv3',
    keywords='boxcar api notify',
    url='https://github.com/markcaudill/boxcar')
