#!/usr/bin/env python
from __future__ import with_statement

import os
import sys
import re
import shutil
import jsmin
import cssmin
import time
from optparse import OptionParser
import logging

class Asset(object):
    
    def __init__(self, src):
        self.src = src
        
    def __normalize_asset_filename(self, filename):
        querystring_index = filename.find('?')
        if querystring_index > 1:
            filename = filename[:querystring_index]
        return filename    
    
    def __repr__(self):
        return "<%s src=%s>" % (self.__class__.__name__, self.src)

class CssAsset(Asset):
    pass

class JsAsset(Asset):
    pass
    

class BundleCollection(list):
    
    def __init__ (self, bundles=[]):
        list.__init__(self, bundles)
        
    def get_by_name(self, name):
        for bundle in list:
            if bundle.name == name:
                return bundle
        return None
    
class JsBundleCollection(BundleCollection):
    pass

class CssBundleCollection(BundleCollection):
    pass

class BaseBundle(object):
    
    def __init__(self, name, timestamp=None, raw_content='', burst_cache=True, base_path=None):
        self._assets = []
        self.name = name
        self.timestamp = timestamp
        self.raw_content = raw_content
        self.burst_cache = burst_cache
        self.base_path = base_path
        
    def add_asset(self, asset):
        self._assets.append(asset)
        
    @property    
    def filename(self):
        if self.burst_cache:
            filename = '%s.%s.%s' % (self.name, self.timestamp, self.ASSET_EXTENSION)
        else:
            filename = '%s.%s' % (self.name, self.ASSET_EXTENSION)
            
        return filename
    
    @property
    def assets(self):
        self._assets = []
        if not self.raw_content:
            return []
        
        for m in self.content_regex.finditer(self.raw_content):
            asset = self.asset_class(m.group('src'))
            asset.src = asset.src.strip('/')
            asset_path = os.path.join(self.base_path, asset.src)
            if not os.path.isfile(asset_path):
                logging.warn('Skipping missing static file: %s', asset_path)
                continue
            self.add_asset(asset)
            
        return self._assets
    
    def __repr__(self):
        return "<%s name=%s, assets=%s>" % (self.__class__.__name__, self.name, self.assets)
        
    @property
    def processed_content(self):
        content = []
        for asset in self.assets:
            asset_path = os.path.join(self.base_path, asset.src)
            with open(asset_path, 'r') as f:
                content.append(f.read())
        return '\n'.join(content)
                
        
class JsBundle(BaseBundle):
    
    ASSET_EXTENSION = 'js'
    content_regex = re.compile(r'<script (?P<attrs_before>[^>]*)src="(?P<src>[^"]+)"(?P<attrs_after>[^>]*)>')
    asset_class = JsAsset
    
    def compress(self):
        return jsmin.jsmin(self.processed_content)
    
class CssBundle(BaseBundle):
    
    ASSET_EXTENSION = 'css'
    content_regex = re.compile(r'<link (rel="stylesheet" )?(?P<attrs_before>[^>]*)href="(?P<src>[^"]+)"(?P<attrs_after>[^>]*)( rel="stylesheet" )?>')
    asset_class = CssAsset
    
    def compress(self):
        return cssmin.cssmin(self.processed_content)
        

class BundleParser(object):
    
    def __init__(self, base_path):
        self.__bundles = []
        self.base_path = base_path
    
    def run(self, content):
        bundles = self.parse(content)
        return bundles, self.replace(content, bundles)
    
    def parse(self, content):
        bundle_collection = JsBundleCollection()
        for match in self.regex.finditer(content):
            if not match.group('content'):
                continue
            bundle = self.bundle_class(match.group('name'), timestamp=int(time.time()), raw_content=match.group('content'), base_path=self.base_path)
            bundle_collection.append(bundle)
        return bundle_collection
    
    def replace(self, content, bundle_collection):
        replaced_template = content
        for bundle in bundle_collection:
            regex = re.compile(self.replace_template % bundle.name, re.DOTALL)
            replaced_template = regex.sub(
                self.replace_with % bundle.filename,
                replaced_template
            )
        return replaced_template
        
        
class JsBundleParser(BundleParser):
    
    regex = re.compile(r'<!--\s*jsbundle "(?P<name>\w*)"\s*-->(?P<content>.*?)<!--\s*endbundle\s*-->', re.DOTALL)
    replace_template = r'<!--\s*jsbundle "%s"\s*-->(.*?)<!--\s*endbundle\s*-->'
    replace_with = '<script type="text/javascript" src="/bundles/%s"></script>'
    bundle_class = JsBundle
    bundle_collection = JsBundleCollection    
            

class CssBundleParser(BundleParser):
    
    regex = re.compile(r'<!--\s*cssbundle "(?P<name>\w*)"\s*-->(?P<content>.*?)<!--\s*endbundle\s*-->', re.DOTALL)
    replace_template = r'<!--\s*cssbundle "%s"\s*-->(.*?)<!--\s*endbundle\s*-->'
    replace_with = '<link rel="stylesheet" href="/bundles/%s" />'
    bundle_class = CssBundle
    bundle_collection = CssBundleCollection
        
class TemplateScanner(object):
    
    def __init__(self, parsers=[]):
        self.__registered_parser = parsers
        
    def register_parser(self, parser):
        self.__registered_parser.append(parser)

    def run(self, content):
        found_bundles = []
        for parser in self.__registered_parser:
            bundles, content = parser.run(content)
            if bundles:
                found_bundles.append(bundles)
        return found_bundles, content
        

class FilesystemBundleStorage(object):
    
    def write_bundles(self, bundle_collection, dest_base_path):
        for bundle in bundle_collection:
            if not os.path.isdir(dest_base_path):
                os.makedirs(dest_base_path)
            dest_path = os.path.join(dest_base_path, bundle.filename)
            with open(dest_path, 'w+') as f:
                f.write(bundle.compress())
            
            
class FilesystemBundleReader(object):
    
    def read(self):
        pass
        
        
class AssetBundler(object):
    
    def __init__(self, app_path, burst_cache=True):
        self.app_path = app_path
        self.template_dir = os.path.join(app_path, 'templates')

        self.templates_min_path = os.path.join(self.app_path, '_bundled_templates')
        self.static_path = os.path.join(self.app_path, 'static')
        self.gen_bundles_path = os.path.join(self.static_path, 'bundles')
        self.burst_cache = burst_cache
    
    def run(self):
        logging.info("Processing template files ...")
        for root, subFolders, files in os.walk(self.template_dir):
            for filename in files:
                filePath = os.path.join(root, filename)
                logging.info("- Parsing template %s", filename)
                with open(filePath, 'r') as f:
                    bundles, content = TemplateScanner(
                        parsers=[JsBundleParser(base_path=self.static_path), CssBundleParser(base_path=self.static_path)]
                    ).run(f.read())
                if bundles:
                    base_path = root.replace(self.template_dir, '')
                    full_path = os.path.join(self.templates_min_path, base_path[1:])
                    if not os.path.exists(full_path):
                        os.makedirs(full_path)
                    new_file_path = os.path.join(full_path, filename)
                    
                    bundle_storage = FilesystemBundleStorage()
                    for bundle_collection in bundles:
                        logging.info("Found %s bundle(s): %s" % (
                                bundle_collection.__class__.__name__,
                                ', '.join(item.name for item in bundle_collection))
                            )
                        bundle_storage.write_bundles(bundle_collection, self.gen_bundles_path)
                        
                    with open(new_file_path, 'w+') as f:
                        f.write(content)

if __name__ == '__main__':
    logging.basicConfig(format=('%(levelname)s %(filename)s:'
                              '%(lineno)s %(message)s '), level=logging.INFO)
    
    app_path = os.path.abspath(sys.argv[1])
    bundler = AssetBundler(app_path)
    bundler.run()
