import os
import platform
import importlib

import dingus
import pytest

server = None

def setup_module(mod):
    if platform.system() == 'Windows':
        pytest.skip("Can't import eggmonster.server on Windows")
    mod.server = importlib.import_module('eggmonster.server')

def fake_stat(filepath):
    # create a fake time that's always the same for a given path
    fake_time = hash(filepath) % 2**32
    return os.stat_result((0,)*7 + (fake_time,)*3)

class TestConfig(object):
    sample_listing = ['{num}.yaml'.format(**vars()) for num in xrange(1,11)]
    listdir_patch = dingus.patch(
        'os.listdir',
        dingus.Dingus(return_value=sample_listing),
    )
    stat_patch = dingus.patch(
        'os.stat',
        fake_stat,
    )
    pathjoin_patch = dingus.patch(
        'os.path.join',
        lambda *args: args[-1],
    )

    @pathjoin_patch
    @stat_patch
    @listdir_patch
    def test_config_nums(self):
        assert sorted(server.config_nums()) == range(1,11)

    @pathjoin_patch
    @stat_patch
    @listdir_patch
    def test_latest_config(self):
        assert server.latest_config() == 10
