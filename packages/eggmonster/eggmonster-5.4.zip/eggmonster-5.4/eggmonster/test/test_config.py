from eggmonster.config import ClusterConfig
import os

basedir = os.path.dirname(__file__)

class TestConfig(object):
    @classmethod
    def setup_class(cls):
        cls.config = ClusterConfig.from_file(os.path.join(basedir,
            'test1.yaml'))

    def test_basic_node_existence(self):
        assert 'node1' in self.config.host_nodes
        assert 'node2' in self.config.host_nodes
        assert 'node3' in self.config.host_nodes
        assert 'other' not in self.config.host_nodes

    def test_host_entry(self):
        n2_conf = self.config.host_nodes['node2']
        assert ('foobar.admin', 1) in n2_conf
        assert ('foobar.admin', 2) in n2_conf
        assert ('foobar.ivw', 1) in n2_conf
        assert ('foobar.ivw', 2) in n2_conf
        assert ('barfoo.main', 1) not in n2_conf

        n3_conf = self.config.host_nodes['node3']
        assert ('barfoo.main', 1) in n3_conf

    def test_env(self):
        n2_conf = self.config.host_nodes['node2']
        admin = n2_conf[('foobar.admin', 1)]
        assert admin.env == {'email_error' : True, 'trace' : False, 'radiation_percentage' : 25,
        'port' : 5000, 'threads' : 5}
        assert 'turbo' not in admin.env

        ivw = n2_conf[('foobar.ivw', 1)]
        assert 'turbo' in ivw.env

    def test_ep(self):
        n2_conf = self.config.host_nodes['node2']
        ivw = n2_conf[('foobar.ivw', 1)]
        admin = n2_conf[('foobar.admin', 1)]

        assert admin.entry_point == 'admin'
        assert ivw.entry_point == 'ivw'

    def test_pkg(self):
        n2_conf = self.config.host_nodes['node2']
        n3_conf = self.config.host_nodes['node3']
        ivw = n2_conf[('foobar.ivw', 1)]
        main = n3_conf[('barfoo.main', 1)]

        assert ivw.pkginfo == 'foobar == 2.20.8'
        assert main.pkginfo == 'barfoo == 3.5.4.1'
