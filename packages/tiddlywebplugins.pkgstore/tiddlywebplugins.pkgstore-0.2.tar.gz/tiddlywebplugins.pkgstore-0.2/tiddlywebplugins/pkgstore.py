"""
Use package resources of a package as a place to store
tiddlers etc.
"""

import os

try:    
        from pkg_resources import resource_filename
except ImportError:
        from tiddlywebplugins.utils import resource_filename

from tiddlyweb.store import (StoreMethodNotImplemented, NoBagError,
        NoTiddlerError)
from tiddlyweb.stores.text import Store as TextStore

class Store(TextStore):
    """
    A store which keeps entities inside a package.
    """

    def __init__(self, store_config=None, environ=None):
        package = store_config['package']
        self.read_only = store_config.get('read_only', True)
        store_root_base = resource_filename(package, 'resources')
        if not self.read_only:
            try:
                os.makedirs(store_root_base)
            except OSError, exc:
                if exc.errno == 17:
                    pass
        store_config['store_root'] = '%s/store' % store_root_base
        super(Store, self).__init__(store_config, environ)

    def _init_store(self):
        if self.read_only:
            return
        super(Store, self)._init_store()

    def recipe_put(self, recipe):
        if self.read_only:
            raise StoreMethodNotImplemented('store is read only')
        super(Store, self).recipe_put(recipe)

    def bag_put(self, bag):
        if self.read_only:
            raise StoreMethodNotImplemented('store is read only')
        super(Store, self).bag_put(bag)

    def tiddler_put(self, tiddler):
        if self.read_only:
            raise StoreMethodNotImplemented('store is read only')
        super(Store, self).tiddler_put(tiddler)

    def recipe_delete(self, recipe):
        if self.read_only:
            raise StoreMethodNotImplemented('store is read only')
        super(Store, self).recipe_delete(recipe)

    def bag_delete(self, bag):
        if self.read_only:
            raise StoreMethodNotImplemented('store is read only')
        super(Store, self).bag_delete(bag)

    def tiddler_delete(self, tiddler):
        if self.read_only:
            raise StoreMethodNotImplemented('store is read only')
        super(Store, self).tiddler_delete(tiddler)

    def user_put(self, user):
        raise StoreMethodNotImplemented('store does not handle users')

    def user_delete(self, user):
        raise StoreMethodNotImplemented('store does not handle users')

    def user_get(self, user):
        raise StoreMethodNotImplemented('store does not handle users')

    def bag_get(self, bag):
        bag = super(Store, self).bag_get(bag)
        skip_bags = self._skip_bags()
        if self.read_only and skip_bags:
            if bag.name in skip_bags:
                raise NoBagError('%s skipped by config' % bag.name)
        return bag

    def tiddler_get(self, tiddler):
        tiddler = super(Store, self).tiddler_get(tiddler)
        skip_bags = self._skip_bags()
        if self.read_only and skip_bags:
            if tiddler.bag in skip_bags:
                raise NoTiddlerError('Bag %s skipped by config' % tiddler.bag)
        return tiddler

    def list_bags(self):
        bags = super(Store, self).list_bags()
        skip_bags = self._skip_bags()
        if self.read_only and skip_bags:
            return (bag for bag in bags if bag.name not in skip_bags)
        return bags

    def _skip_bags(self):
        return self.environ.get('tiddlyweb.config', {}).get(
                'pkgstore.skip_bags', [])
