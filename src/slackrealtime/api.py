"""
slackrealtime/api.py - Barebones implementation of the Slack API.
Copyright 2014 Michael Farrell <http://micolous.id.au>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import absolute_import
import requests
from urlparse import urljoin

SLACK_API_URL = 'https://slack.com/api/'

class SlackError(Exception):
	pass

class SlackMethod(object):
	def __init__(self, url, group, method):
		self.url = url
		self.method = group + '.' + method

	def __call__(self, **params):
		print 'calling: %s(%r)' % (self.method, params)
		response = requests.post(urljoin(self.url, self.method), data=params)
		
		print 'response = %r' % (urljoin(self.url, self.method),)
		response = response.json()

		assert response['ok'] in (True, False), 'ok must be True or False'
		if not response['ok']:
			raise SlackError, response['error']

		# Trim this attribute as it is no longer required
		del response['ok']
		return response

	def __str__(self):
		return '<SlackMethod: %s at %s>' % (self.method, self.url)


class SlackMethodGroup(object):
	def __init__(self, url, group):
		self.url = url
		self.group = group

	def __getattr__(self, method):
		return SlackMethod(self.url, self.group, method)

	def __str__(self):
		return '<SlackMethodGroup: %s at %s>' % (self.group, self.url)


class SlackApi(object):
	def __init__(self, url=SLACK_API_URL):
		if not url.endswith('/'):
			url += '/'
		self.url = url
	
	def __getattr__(self, group):
		# Gets a method descriptor
		return SlackMethodGroup(self.url, group)

