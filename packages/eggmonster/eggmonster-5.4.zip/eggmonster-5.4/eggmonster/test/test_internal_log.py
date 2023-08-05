import socket
import os

import dingus
import py.test

from eggmonster import internal_log

class TestGetHost:
	def setup_method(self, method):
		# save the environment
		self.orig_env = dict(os.environ)
		if 'EGGMONSTER_LOG_HOST' in os.environ:
			os.environ.pop('EGGMONSTER_LOG_HOST')

	def teardown_method(self, method):
		# restore the environment if necessary
		if not os.environ == self.orig_env:
			os.environ.clear()
			os.environ.update(self.orig_env)

	@dingus.patch('socket.gethostbyname')
	def test_get_host_env(self):
		os.environ['EGGMONSTER_LOG_HOST'] = 'eggmonster-log-host.example.com:5000'
		host, port = internal_log.get_host()
		assert host == 'eggmonster-log-host.example.com'
		assert port == 5000
		assert not socket.gethostbyname.calls()

	@dingus.patch('socket.gethostbyname', dingus.exception_raiser(socket.gaierror('foo')))
	def test_get_host_missing(self):
		assert internal_log.get_host() is None

	@dingus.patch('socket.gethostbyname', dingus.Dingus(return_value='127.0.0.1'))
	def test_get_host_present(self):
		host, port = internal_log.get_host()
		assert host == 'eggmonster-log'
		assert port == 13000
		calls = socket.gethostbyname.calls()
		assert len(calls) == 1
		call, = calls
		assert call.args == ('eggmonster-log',)
