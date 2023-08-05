#!/usr/bin/env python

version = '0.1.2.26'

fd = open('btcnet_info/version.py', 'wb')
fd.seek(0)
fd.write("""__version__ = "%s" """ % version)
fd.close()

from setuptools import setup, find_packages
setup(name='btcnet_info',
        version=version,
        description='BitCoin Network Information Library',
        author='Colin Rice',
        author_email='dah4k0r@gmail.com',
        packages=['btcnet_info'],
        include_package_data = True,
        package_data = { "":["*/*"]},
        url='github.com/c00w/btcnet_info',
        classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'Topic :: System :: Networking',
            'License :: OSI Approved :: MIT License',
            ],
        license = 'MIT Expat License',
        install_requires = [
            'gevent', 
            'httplib2'
            ]
        )
