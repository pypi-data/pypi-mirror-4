#!/usr/bin/env python
from setuptools import setup, find_packages
from setuptools.command.install import install as _install

class install(_install):
    
    def run(self):
        _install.run(self)

setup(
    name = "GaeAssetBundler",
    cmdclass={'install': install},
    version = "0.4",
    description='Assets compression and bundling for GAE',
    author='Fabio Sussetto',
    author_email='fabio@bynd.com',
    packages = find_packages(),
    scripts=['gae_asset_bundler/gae_asset_bundler.py'],
    install_requires = ['jsmin', 'cssmin']
)