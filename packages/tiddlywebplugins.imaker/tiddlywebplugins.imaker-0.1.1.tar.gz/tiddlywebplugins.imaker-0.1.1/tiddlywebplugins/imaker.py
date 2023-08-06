"""
A collection of tools and functions for creating instances
from tiddlywebplugins packages hosting pre-determined
tiddlers, bags, and recipes.
"""

import os
import sys

from time import time
from random import random
from pprint import pformat

from tiddlyweb.manage import make_command
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.model.user import User
from tiddlyweb.store import Store
from tiddlyweb.util import sha

from tiddlywebplugins.utils import get_store


__version__ = '0.1.1'
CONFIG_NAME = 'tiddlywebconfig.py'


def init(config):
    """
    Establish commands.
    """

    @make_command()
    def udpate(args):
        """Update the default tiddlers for this instance."""
        instance = Instance('.', config)
        instance.update_store()


def spawn(instance_path, init_config, instance_module):
    """
    convenience wrapper for instance-creation scripts
    """
    # extend module search path for access to local tiddlywebconfig.py
    sys.path.insert(0, os.getcwd())
    from tiddlyweb.util import merge_config
    from tiddlyweb.config import config
    merge_config(config, init_config)

    instance = Instance(instance_path, config, instance_module.instance_config)
    instance.spawn(instance_module.store_structure)
    instance.update_store()


class Instance(object):
    """
    prefconfigured TiddlyWeb instance
    """

    def __init__(self, directory, init_config, instance_config=None):
        """
        creates instance in given directory

        init_config: a TiddlyWeb configuration dictionary used when creating
        the instance

        instance_config: is an optional dictionary with configuration values
        for the default tiddlywebconfig.py (usually referencing init_config in
        system_plugins and twanager_plugins)

        Note that init_config may contain an entry "instance_config_head" whose
        value is prepended to the generated tiddlywebconfig.py.
        """
        self.root = os.path.abspath(directory)
        self.init_config = init_config
        self.instance_config = instance_config

    def spawn(self, store_structure=None):
        """
        creates the instance, optionally pre-configuring the store structure
        """
        cwd = os.getcwd()
        os.mkdir(self.root)
        os.chdir(self.root)

        self._write_config()

        if store_structure:
            self._init_store(store_structure)
        os.chdir(cwd)

    def update_store(self):
        """
        prepopulates/updates store contents by (re)importing instance_tiddlers
        """
        cwd = os.getcwd()
        os.chdir(self.root)

        store = get_store(self.init_config)
        for package_name in self.init_config['instance_pkgstores']:
            source_store = Store('tiddlywebplugins.pkgstore',
                    {'package': package_name, 'read_only': True}, {})
            for bag in source_store.list_bags():
                for tiddler in source_store.list_bag_tiddlers(bag):
                    tiddler = source_store.get(tiddler)
                    store.put(tiddler)
        os.chdir(cwd)

    def _init_store(self, struct):
        """
        creates basic store structure with bags, recipes and users

        (no support for user passwords for security reasons)
        """
        store = get_store(self.init_config)

        bags = struct.get("bags", {})
        for name, data in bags.items():
            desc = data.get("desc")
            bag = Bag(name, desc=desc)
            constraints = data.get("policy", {})
            _set_policy(bag, constraints)
            store.put(bag)

        recipes = struct.get("recipes", {})
        for name, data in recipes.items():  # TODO: DRY
            desc = data.get("desc")
            recipe = Recipe(name, desc=desc)
            recipe.set_recipe(data["recipe"])
            constraints = data.get("policy", {})
            _set_policy(recipe, constraints)
            store.put(recipe)

        users = struct.get("users", {})
        for name, data in users.items():
            note = data.get("note")
            user = User(name, note=note)
            password = data.get("_password")
            if password:
                user.set_password(password)
            for role in data.get("roles"):
                user.add_role(role)
            store.put(user)

    def _write_config(self):
        """
        creates a default tiddlywebconfig.py in the working directory

        uses values from instance_config plus optional instance_config_head
        from init_config
        """
        intro = "%s\n%s\n%s" % ("# A basic configuration.",
            '# `pydoc tiddlyweb.config` for details on configuration items.',
            self.init_config.get("instance_config_head", ""))

        config = {
            "secret": _generate_secret()
        }
        config.update(self.instance_config or {})

        config_string = "config = %s\n" % _pretty_format(config)
        config_file = open(CONFIG_NAME, "w")
        config_file.write("%s\n%s" % (intro, config_string))
        config_file.close()


def _set_policy(entity, constraints):
    """
    applies contstraints to entity

    entity is a Bag or a Recipe, constraints a dictionary
    """
    for constraint, value in constraints.items():
        setattr(entity.policy, constraint, value)


def _generate_secret():
    """
    create a pseudo-random secret

    This is used for message authentication.
    """
    digest = sha(str(time()))
    digest.update(str(random()))
    digest.update("lorem foo ipsum")
    return digest.hexdigest()


def _pretty_format(dic):
    """
    generate an indented string representation of a dictionary
    """
    def escape_strings(value):
        if hasattr(value, "join"):
            return "'%s'" % value
        elif hasattr(value, "keys"):
            return pformat(value)
        else:
            return value
    lines = ("    '%s': %s" % (k, escape_strings(v)) for k, v in dic.items())
    return "{\n%s,\n}" % ",\n".join(lines)
