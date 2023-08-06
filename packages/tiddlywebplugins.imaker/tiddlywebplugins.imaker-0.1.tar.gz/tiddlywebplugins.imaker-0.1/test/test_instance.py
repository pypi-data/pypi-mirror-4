"""
Test instance creation.
"""

import shutil
import os

from tiddlywebplugins.imaker import spawn

def setup_module(module):
    try:
        shutil.rmtree('testinstance')
    except:
        pass


def test_spawn():
    from testpackage import instance as instance_module
    from testpackage.config import config as init_config

    spawn('testinstance', init_config, instance_module)

    assert os.path.exists('testinstance/tiddlywebconfig.py')
    assert os.path.exists('testinstance/store/bags/testbag/tiddlers/testtiddler')
