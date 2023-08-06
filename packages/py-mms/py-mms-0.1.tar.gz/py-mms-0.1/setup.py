import os
from distutils.core import setup


f = open(os.path.join(os.path.dirname(__file__), 'README.md'))
long_description = f.read()
f.close()

setup(
    name='py-mms',
    version='0.1',
    author='COEX CZ',
    author_email='support@coex.cz',
    url='https://github.com/COEXCZ/py-mms',
    install_requires=[
        'python-dateutil',
        'python-jsonrpc==2.0',
    ],
    dependency_links=[
        'https://github.com/davvid/python-jsonrpc/tarball/v2.0#egg=python-jsonrpc-2.0',
    ],
    packages=[
        'mms',
    ],
    license='ISC license',
    long_description=long_description,
)
