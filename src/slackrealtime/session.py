"""
slackrealtime/session.py - Session management for Slack RTM
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
from .api import SlackApi
from .event import *
import requests
from twisted.internet import reactor

def transform_metadata(blob):
	"""
	Transforms metadata types about channels / users / bots / etc. into a dict
	rather than a list in order to enable faster lookup.

	"""
	o = {}
	for e in blob:
		i = e[u'id']
		del e[u'id']
		o[i] = e
	return o


class SessionMetadata(object):
	def __init__(self, data, api, token):
		self.api = api
		self.token = token

		self.url = data['url']
		self.me = data['self']
		self.team = data['team']

		# All users on the Slack instance.
		self.users = transform_metadata(data['users'])

		# All public channels on the Slack instance.
		self.channels = transform_metadata(data['channels'])

		# All private groups on the Slack instance.
		self.groups = transform_metadata(data['groups'])

		# All private messages on the Slack instance.
		self.ims = transform_metadata(data['ims'])

		# All bots on the slack instance.
		self.bots = transform_metadata(data['bots'])

	def _find_resource_by_key(self, resource_list, key, value):
		"""
		Finds a resource by key, first case insensitive match.

		Returns tuple of (key, resource)

		Raises KeyError if the given key cannot be found.
		"""
		original = value
		value = unicode(value.upper())
		for k, resource in resource_list.iteritems():
			if key in resource and resource[key].upper() == value:
				return k, resource

		raise KeyError, original

	def find_channel_by_name(self, name):
		"""
		Finds the channel's resource by name.
		"""
		return self._find_resource_by_key(self.channels, u'name', name)

	def find_user_by_name(self, name):
		return self._find_resource_by_key(self.users, u'name', name)

	def find_group_by_name(self, name):
		return self._find_resource_by_key(self.groups, u'name', name)

	def find_im_by_user_id(self, uid):
		return self._find_resource_by_key(self.ims, u'user', uid)

	def find_im_by_user_name(self, name, auto_create=True):
		"""
		Finds the ID of the IM with a particular user by name, with the option
		to automatically create a new channel if it doesn't exist.
		"""
		uid = self.find_user_by_name(name)[0]
		try:
			return self.find_im_by_user_id(uid)
		except KeyError:
			# IM does not exist, create it?
			if auto_create:
				response = self.api.im.open(token=self.token, user=uid)
				return response[u'channel'][u'id']
			else:
				raise

	def update(self, event):
		"""
		All messages from the Protocol get passed through this method.  This
		allows the client to have an up-to-date state for the client.
		
		However, this method doesn't actually update right away.  Instead, the
		acutal update happens in another thread, potentially later, in order to
		allow user code to handle the event faster.
		
		"""
		
		# Create our own copy of the event data, as we'll be pushing that to
		# another data structure and we don't want it mangled by user code later
		# on.
		event = event.copy()

		# Now just defer the work to later.
		reactor.callInThread(self._update_deferred, event)

	def _update_deferred(self, event):
		"""
		This does the actual work of updating channel metadata.  This is called
		by the update(), and runs this method in another thread.
		"""
		if isinstance(event, ChannelCreated):
			i = event.channel[u'id']
			del event.channel[u'id']
			event.channel[u'is_archived'] = event.channel[u'is_member'] = False

			self.channels[i] = event.channel
		elif isinstance(event, ChannelArchive):
			self.channels[event.channel][u'is_archived'] = True
		elif isinstance(event, ChannelDeleted):
			# FIXME: Handle delete events properly.
			# Channels don't really get deleted, they're more just archived.
			self.channels[event.channel][u'is_archived'] = True
			self.channels[event.channel][u'is_open'] = False
		elif isinstance(event, ChannelJoined):
			cid = event.channel[u'id']
			del event.channel[u'id']
			
			self.channels[cid] = event.channel
		elif isinstance(event, ChannelLeft):
			self.channels[event.channel][u'is_member'] = False
		elif isinstance(event, ChannelMarked):
			# TODO: implement datetime handler properly
			self.channels[event.channel][u'last_read'] = event._b[u'ts']
		elif isinstance(event, ChannelRename):
			self.channel[event.channel[u'id']][u'name'] = event.channel[u'name']
		elif isinstance(event, ChannelUnarchive):
			self.channels[event.channel][u'is_archived'] = False
		elif isinstance(event, ImClose):
			self.ims[event.channel][u'is_open'] = False
		elif isinstance(event, ImCreated):
			i = event.channel[u'id']
			del event.channel[u'id']
			event.channel[u'user'] = event.user

			self.ims[i] = event.channel
		elif isinstance(event, ImMarked):
			# TODO: implement datetime handler properly
			self.ims[event.channel][u'last_read'] = event._b[u'ts']
		elif isinstance(event, ImOpen):
			self.ims[event.channel][u'is_open'] = True
		elif isinstance(event, PresenceChange):
			self.users[event.user][u'presence'] = event.presence
		elif isinstance(event, UserChange):
			# Everything but the status is provided
			# Copy this out of the existing object

			uid = event.user[u'id']
			del event.user[u'id']

			if event.user[u'status'] is None and u'presence' in self.users[uid]:
				event.user[u'status'] = self.users[uid][u'presence']

			self.users[uid] = event.user
		elif isinstance(event, TeamPrefChange):
			self.team[u'prefs'][event.name] = event.value
		elif isinstance(event, TeamJoin):
			uid = event.user[u'id']
			del event.user[u'id']

			self.users[uid] = event.user

def request_session(token, url=None):
	"""
	Requests a WebSocket session for the Real-Time Messaging API.
	
	Returns a SessionMetadata object containing the information retrieved from
	the API call.
	"""
	if url is None:
		api = SlackApi()
	else:
		api = SlackApi(url)

	response = api.rtm.start(token=token)
	return SessionMetadata(response, api, token)

