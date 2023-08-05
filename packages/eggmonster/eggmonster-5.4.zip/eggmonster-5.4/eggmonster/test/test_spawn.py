import os
import sys
import subprocess
import textwrap
import platform

import pkg_resources
import pytest

@pytest.mark.skipif("platform.system() == 'Windows'")
class TestSpawn(object):

    @classmethod
    def setup_class(cls):
        cls.setup_env()
        cls.create_runner_scripts()

    @classmethod
    def teardown_class(cls):
        for name in cls.scripts:
            os.remove(name)

    @classmethod
    def setup_env(cls):
        """
        Set up an environment which adds the test plugins to the PYTHONPATH
        variable, faking an install of an eggmonster app.
        Also be sure to include sys.path so that any paths set up to support
        this eggmonster install are also present.
        """
        cls.env = os.environ.copy()
        plugins = pkg_resources.resource_filename('eggmonster.test',
            'plugins')
        cls.env.update(PYTHONPATH=os.pathsep.join([plugins] + sys.path))

    scripts = {
        'fake-monster': """
            #!{sys.executable}
            import eggmonster.runner
            eggmonster.runner.FakeMonster.run()
            """,
        'monster_run': """
            #!{sys.executable}
            import eggmonster.commands.monster_run as mr
            mr.run()
            """,
    }

    @classmethod
    def create_runner_scripts(cls):
        """
        When eggmonster is tested using pytest-runner, it isn't installed
        anywhere, so the console_scripts aren't created. This method creates
        the scripts necessary to run these tests.
        """
        for name, script in cls.scripts.iteritems():
            with open(name, 'wb') as f:
                f.write(textwrap.dedent(script.format(sys=sys)).lstrip())
            os.chmod(name, 0o700)

    def test_fake_monster_spawn(self):
        config_file = os.path.join(os.path.dirname(__file__),
            'test_spawn_flat.yaml')
        output = subprocess.check_output(
            './fake-monster sum_app.do_sum --config-path=%s 10'
            % config_file, shell=True, env=self.env)
        assert output == '18'

    def test_monster_run_spawn(self):
        config_file = os.path.join(os.path.dirname(__file__),
            'test_spawn_struct.yaml')
        output = subprocess.check_output(
            './monster_run %s sum_app.do_sum ! 10' % config_file,
            shell=True, env=self.env)
        assert output == '18'
