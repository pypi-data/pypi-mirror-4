#!/usr/bin/env python

import setuptools
import os

version = '1.0.1'


setuptools.setup(
    name='assetreload',
    version=version,
    author='Callum Jefferies',
    author_email='callum@callumj.co.uk',
    description='Broadcast changes in your assets to the browser.',
    long_description=open(os.path.join(os.path.dirname(__file__),
                          'README.md')).read(),
    license='MIT License',
    keywords='websocket css javascript web browser tornado',
    url='https://github.com/callum-/assetreload',
    download_url=('http://github.com/callum-/'
                  'assetreload/archive/%s.tar.gz' % version),
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=[
        'tornado',
        'watchdog'
    ],
    entry_points={
        'console_scripts': [
            'assetreload = assetreload:main'
        ]
    }
)
