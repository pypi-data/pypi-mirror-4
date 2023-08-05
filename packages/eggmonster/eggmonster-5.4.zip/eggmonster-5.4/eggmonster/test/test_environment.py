from eggmonster import Environment

def test_defaults():
	default_items = dict(
		a = 1,
		b = 2.0,
		c = 'three',
	)
	local_items = dict(
		d = 4,
		b = 'bee',
	)
	env = Environment()
	env._defaults.update(default_items)
	env.update(local_items)
	assert env.a == 1
	assert env.d == 4
	assert env.b == 'bee'

def test_as_obscured_dict():
	env = Environment()
	d = dict(not_a_password = 'public', password = 'SECRET1')
	env._defaults.update(dict(a = 1, b = 2.0, d = d, password = 'SECRET2'))
	env.update(dict(b = 'bee'))
	assert env.a == 1
	assert env.b == 'bee'
	assert env.d == d
	assert env.password == 'SECRET2'
	assert env.as_obscured_dict() == dict(
		a = 1,
		b = 'bee',
		password = '********',
		d = dict(not_a_password = 'public', password = '********')
		)
