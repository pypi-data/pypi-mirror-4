from setuptools import setup

from proxypypi import __version__

setup(
    name='proxypypi',
    version=__version__,
    author="Richard Jones",
    author_email="rjones@ekit-inc.com",
    description="A PyPI caching proxy",
    long_description=open('README.txt').read(),
    url='https://bitbucket.org/r1chardj0n3s/proxypypi',
    license="BSD",
    packages=['proxypypi'],
    entry_points={
        'console_scripts': [
            'proxypypi = proxypypi.server:main',
        ],
    },
    install_requires=['gunicorn', 'bottle', 'lockfile', 'distlib>=0.1.2'],
)
