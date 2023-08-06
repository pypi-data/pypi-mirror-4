
import os
import shutil
import py.test
from tiddlyweb.config import config

from tiddlyweb.store import Store

from tiddlyweb.store import StoreMethodNotImplemented, StoreError
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.model.user import User


def setup_module(module):
    try:
        shutil.rmtree('testpackage/resources/store')
    except:  # not there
        pass
    environ = {'tiddlyweb.config': config}
    wstore = Store('tiddlywebplugins.pkgstore',
            {'package': 'testpackage', 'read_only': False},
            environ)
    module.wstore = wstore
    rstore = Store('tiddlywebplugins.pkgstore',
            {'package': 'testpackage', 'read_only': True},
            environ)
    module.rstore = rstore


def test_base_structure():
    assert os.path.exists('testpackage/resources/store')
    assert os.path.isdir('testpackage/resources/store')
    assert os.path.exists('testpackage/resources/store/recipes')
    assert os.path.isdir('testpackage/resources/store/recipes')
    assert os.path.exists('testpackage/resources/store/bags')
    assert os.path.isdir('testpackage/resources/store/bags')
    assert os.path.exists('testpackage/resources/store/users')
    assert os.path.isdir('testpackage/resources/store/users')


def test_put_bag():
    bag = Bag('testone')
    wstore.put(bag)
    assert os.path.exists('testpackage/resources/store/bags/testone')
    assert os.path.isdir('testpackage/resources/store/bags/testone')


def test_put_recipe():
    recipe = Recipe('testone')
    wstore.put(recipe)
    assert os.path.exists('testpackage/resources/store/recipes/testone')
    assert os.path.isfile('testpackage/resources/store/recipes/testone')
    wstore.delete(recipe)
    assert not os.path.exists('testpackage/resources/store/recipes/testone')


def test_put_tiddler():
    tiddler = Tiddler('tiddlerone', 'testone')
    tiddler.text = 'oh hi'
    wstore.put(tiddler)
    assert os.path.exists(
            'testpackage/resources/store/bags/testone/tiddlers/tiddlerone')
    assert os.path.isdir(
            'testpackage/resources/store/bags/testone/tiddlers/tiddlerone')
    with open(
            'testpackage/resources/store/bags/testone/tiddlers/tiddlerone/1') as tiddler_file:
        content = tiddler_file.read().split('\n\n')[1].strip()
        assert content == 'oh hi'


def test_get_tiddler():
    tiddler = Tiddler('tiddlerone', 'testone')
    tiddler = wstore.get(tiddler)
    assert tiddler.text == 'oh hi'

    tiddler = rstore.get(tiddler)
    assert tiddler.text == 'oh hi'

    py.test.raises(StoreMethodNotImplemented, 'rstore.put(tiddler)')
    py.test.raises(StoreMethodNotImplemented, 'rstore.delete(tiddler)')

    wstore.delete(tiddler)
    py.test.raises(StoreError, 'rstore.get(tiddler)')


def test_skip_bags():
    bag = Bag('skippedbag')
    wstore.put(bag)
    tiddler = Tiddler('thing', 'skippedbag')
    wstore.put(tiddler)

    config['pkgstore.skip_bags'] = ['skippedbag']

    bag = wstore.get(Bag('skippedbag'))
    py.test.raises(StoreError, 'rstore.get(Bag("skippedbag"))')

    tiddler = wstore.get(Tiddler('thing', 'skippedbag'))
    py.test.raises(StoreError, 'rstore.get(Tiddler("thing", "skippedbag"))')

    bags = wstore.list_bags()
    assert len(list(bags)) == 2
    bags = rstore.list_bags()
    assert len(list(bags)) == 1


def test_cover_write_and_readonly():
    recipe = Recipe('testone')
    wstore.put(recipe)
    recipe2 = rstore.get(recipe)
    assert recipe2.name == recipe.name
    py.test.raises(StoreMethodNotImplemented, 'rstore.put(recipe)')
    py.test.raises(StoreMethodNotImplemented, 'rstore.delete(recipe)')

    bag = Bag('testone')
    wstore.put(bag)
    bag2 = rstore.get(bag)
    assert bag2.name == bag.name
    py.test.raises(StoreMethodNotImplemented, 'rstore.put(bag)')
    py.test.raises(StoreMethodNotImplemented, 'rstore.delete(bag)')
    wstore.delete(bag)
    assert not os.path.exists('testpackage/resources/store/bags/testone')


def test_user_not_supported():
    user = User('me')

    py.test.raises(StoreMethodNotImplemented, 'rstore.put(user)')
    py.test.raises(StoreMethodNotImplemented, 'rstore.get(user)')
    py.test.raises(StoreMethodNotImplemented, 'rstore.delete(user)')
