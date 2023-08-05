import os

import pkg_resources

import eggmonster.config
import eggmonster.state

class TestConfig(object):
    def load_config(self, name, reset=True):
        if reset:
            self.state = eggmonster.state.RunningState()
        filename = pkg_resources.resource_filename('eggmonster.test', name)
        config = eggmonster.config.ClusterConfig.from_file(filename)
        self.state.update_config(config)

    def test_set_initial_config(self):
        self.load_config('test1.yaml')

    def test_initial_launch(self):
        self.load_config('test1.yaml')
        node1_needs = list(self.state.launch_check('node1'))
        assert len(node1_needs) == 2
        node2_needs = list(self.state.launch_check('node2'))
        assert len(node2_needs) == 4
        node3_needs = list(self.state.launch_check('node3'))
        assert len(node3_needs) == 1
        node_missing_needs = list(self.state.launch_check('missing'))
        assert len(node_missing_needs) == 0

    def test_startstop(self):
        self.load_config('test1.yaml')
        node1_needs = list(self.state.launch_check('node1'))
        node2_needs = list(self.state.launch_check('node2'))

        # Run one of the node1 things
        one_to_run = node1_needs[0]
        self.state.node_started('node1', one_to_run)

        # should be one shorter now--b/c one is running
        node1_needs = list(self.state.launch_check('node1'))
        assert len(node1_needs) == 1

        # now, stop it again
        self.state.node_stopped('node1', one_to_run)

        node1_needs = list(self.state.launch_check('node1'))
        assert len(node1_needs) == 2

    def test_change_yaml(self):
        self.load_config('test1.yaml')

        for host in ['node1', 'node2', 'node3']:
            for node in self.state.launch_check(host):
                self.state.node_started(host, node)

        for host in ['node1', 'node2', 'node3']:
            assert len(list(self.state.launch_check(host))) == 0

        self.load_config('test2.yaml', reset=False)

        restarts = set([(host, node.key) for host, node in self.state.kill_check()])
        assert len(restarts) == 5
        assert ('node2', ('foobar.admin', 2)) in restarts
        assert ('node1', ('foobar.ivw', 1)) in restarts
        assert ('node2', ('foobar.ivw', 1)) in restarts
        assert ('node2', ('foobar.ivw', 2)) in restarts
        assert ('node3', ('barfoo.main', 1)) in restarts

        assert len(list(self.state.launch_check('node4'))) == 1
