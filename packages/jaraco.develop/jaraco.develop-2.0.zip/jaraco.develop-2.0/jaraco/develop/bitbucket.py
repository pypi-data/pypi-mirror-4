from __future__ import print_function

import sys
import urlparse
import functools
import argparse
import getpass
import collections

import requests
import keyring
from jaraco.util.string import local_format as lf

api_url = 'https://api.bitbucket.org/1.0/'
make_url = functools.partial(urlparse.urljoin, api_url)

def create_repository(name, auth, private=False):
	resp = requests.post(make_url('repositories/'),
		data=dict(name=name, is_private=private, scm='hg',
			language='python'), auth=auth,
		headers=dict(Accept='text/json'),
	)
	if not 200 <= resp.status_code <= 300:
		print(lf("Error occurred: {resp.status_code}"), file=sys.stderr)
		raise SystemExit(1)
	return resp.json()

def add_version(project, version, auth):
	"""
	project should be something like user/project
	"""
	url = make_url(lf('repositories/{project}/versions'))
	resp = requests.post(
		url,
		params=dict(name=version),
		auth=auth,
		headers=dict(Accept='text/json'),
	)
	if not 200 <= resp.status_code <= 300:
		print(lf("Error occurred: {resp.status_code}"), file=sys.stderr)
		raise SystemExit(1)
	return resp.json()

Credential = collections.namedtuple('Credential', 'username password')

def get_mercurial_creds(username=None):
	"""
	Return named tuple of username,password in much the same way that
	Mercurial would (from the keyring).
	"""
	# todo: consider getting this from .hgrc
	username = username or getpass.getuser()
	root = 'https://bitbucket.org'
	keyring_username = '@@'.join((username, root))
	system = 'Mercurial'
	password = keyring.get_password(system, keyring_username)
	if not password:
		password = getpass.getpass()
	return Credential(username, password)

def print_result(res):
	width = max(len(key) for key in res) + 1
	for key, value in res.iteritems():
		print(lf("{key:<{width}}: {value}"))

def basic_auth(userpass):
	return Credential(userpass.split(':'))

def create_repository_cmd():
	parser = argparse.ArgumentParser()
	parser.add_argument('repo_name')
	parser.add_argument(
		'-a', '--auth', type=basic_auth, default=get_mercurial_creds(),
	)
	parser.add_argument('-p', '--private', default=False,
		action="store_true")
	args = parser.parse_args()
	res = create_repository(args.repo_name, args.auth,
		private = args.private)
	print_result(res)

def update_wiki(project, title, path, content):
	url = make_url('repositories/{project}/wiki/{title}'.format(**vars()))
	data = dict(path=path, data=content)
	requests.put(url, data=data, auth=get_mercurial_creds())

if __name__ == '__main__':
	create_repository_cmd()
