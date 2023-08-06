
import shutil
from random import shuffle

from tiddlyweb.config import config

from tiddlyweb.store import Store
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.user import User
from tiddlyweb.model.tiddler import Tiddler

from tiddlywebplugins.migrate import migrate_entities

def setup_module(module):
    environ = {'tiddlyweb.config': config}
    source_store = Store(config['server_store'][0],
            config['server_store'][1], environ)
    target_store = Store(config['target_store'][0],
            config['target_store'][1], environ)

    module.source_store = source_store
    module.target_store = target_store
    module.environ = environ
    base_content(source_store)


def reset_stores(new_only=False):
    # cleanup
    for store_root in ['store', 'newstore']:
        if new_only and store_root is 'store':
            continue
        try:
            shutil.rmtree(store_root)
        except:
            pass
    if new_only:  # reinit new store
        target_store = Store(config['target_store'][0],
                config['target_store'][1], environ)


def base_content(store):
    bags = ['one', 'two', 'three']
    for name in bags:
        bag = Bag(name)
        store.put(bag)
        for title in ['alpha', 'bravo', 'corpuscle']:
            tiddler = Tiddler(title, name)
            store.put(tiddler)

    for name in ['cake', 'pudding', 'sauce']:
        recipe = Recipe(name)
        shuffle(bags)
        recipe_list = [(name, '') for name in bags]
        recipe.set_recipe(recipe_list)
        store.put(recipe)

    for name in ['john', 'jane', 'clancy']:
        user = User(name)
        store.put(user)


def test_migrate_all():
    new_bags = target_store.list_bags()
    assert len(list(new_bags)) == 0

    migrate_entities(source_store, target_store)

    new_bags = target_store.list_bags()
    assert len(list(new_bags)) == 3
    new_recipes = target_store.list_recipes()
    assert len(list(new_recipes)) == 3
    new_users = target_store.list_users()
    assert len(list(new_users)) == 3

    new_tiddlers = target_store.list_bag_tiddlers(Bag('one'))
    assert len(list(new_tiddlers)) == 3


def test_migrate_one_bag():
    reset_stores(True)
    new_bags = target_store.list_bags()
    assert len(list(new_bags)) == 0

    migrate_entities(source_store, target_store, ['one'])

    new_bags = target_store.list_bags()
    assert len(list(new_bags)) == 1

    new_recipes = target_store.list_recipes()
    assert len(list(new_recipes)) == 0
    new_users = target_store.list_users()
    assert len(list(new_users)) == 0

    new_tiddlers = target_store.list_bag_tiddlers(Bag('one'))
    assert len(list(new_tiddlers)) == 3
