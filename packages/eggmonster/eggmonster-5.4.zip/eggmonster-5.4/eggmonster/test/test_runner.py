import os
import contextlib
import tempfile
import textwrap

from eggmonster import runner

@contextlib.contextmanager
def environment_context(**kwargs):
    env = os.environ.copy()
    os.environ.update(**kwargs)
    try:
        yield
    finally:
        for k in kwargs:
            del os.environ[k]
        os.environ.update(env)


@contextlib.contextmanager
def sample_config():
    _config = textwrap.dedent("""
        test_project:
            Package: == 1.1
            Directory: "."
            Environment:
                production: 1
            Applications:
                - Name: main
                  Environment:
                    foo: bar
                    baz: other
                    port: 7083
                  Nodes:
                    jam: 1
        """).lstrip()
    tf = tempfile.NamedTemporaryFile(delete=False)
    tf.write(_config)
    tf.close()
    try:
        yield tf.name
    finally:
        os.remove(tf.name)

def test_load_config_from_environment_var():
    with sample_config() as config_path:
        with environment_context(EGGMONSTER_CONFIG_PATH=config_path):
            config = runner._load_config("ENVIRONMENT")
            assert 'test_project.main' in config.apps

def test_load_config_from_specific_environment_var():
    with sample_config() as config_path:
        with environment_context(SOME_CONFIG=config_path):
            config = runner._load_config("ENVIRONMENT:SOME_CONFIG")
            assert 'test_project.main' in config.apps

class TestFakeMonster(object):
    def test_parse_args_no_config(self):
        app, config = runner.FakeMonster.parse_args(['foo.bar'])
        assert str(app) == 'foo.bar'
        assert config == 'settings.yaml'

    def test_parse_args_with_config(self):
        app, config = runner.FakeMonster.parse_args(['foo.bar',
            '--config-path', 'my config.yaml'])
        assert config == 'my config.yaml'

    def test_parse_args_with_app_args(self):
        app, config = runner.FakeMonster.parse_args(['foo.bar',
            '--config-path', 'my config.yaml', 'a', 'b'])
        assert app.args == ['a', 'b']
