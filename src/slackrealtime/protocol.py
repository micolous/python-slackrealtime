"""
slackrealtime/protocol.py - Twisted Protocol library for Slack RTM
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
from autobahn.twisted.websocket import WebSocketClientProtocol
from sys import maxint
from twisted.python import log
from .event import decode_event

try:
	# SimpleJSON is better for many cases in modern Python.
	import simplejson as json
except ImportError:
	import json


class RtmProtocol(WebSocketClientProtocol):
	def _seedMetadata(self, meta):
		self.meta = meta
		self.meta.protocol = self
		self.next_message_id = 1
		return self

	def onMessage(self, msg, binary):
		# What to do on getting messages.
		msg = decode_event(json.loads(msg))

		# Attempt to update metadata
		try:
			self.meta.update(msg)
		except:
			log.msg('Error updating metadata.')
			log.err()

		# Fire off event
		try:
			self.onSlackEvent(msg)
		except:
			log.msg('Error calling onSlackEvent().')
			log.err()

	def onSlackEvent(self, event):
		log.msg('Default onSlackEvent() handler called.')

	def sendCommand(self, **msg):
		"""
		Sends a raw command to the Slack server, generating a message ID automatically.
		"""
		assert 'type' in msg, 'Message type is required.'

		msg['id'] = self.next_message_id
		self.next_message_id += 1

		if self.next_message_id >= maxint:
			self.next_message_id = 1

		self.sendMessage(json.dumps(msg))
		return msg['id']


	def sendChatMessage(self, text, id=None, user=None, group=None, channel=None, parse='none', link_names=True, unfurl_links=True, unfurl_media=False, send_with_api=False):
		"""
		Sends a chat message to a given id, user, group or channel.

		Note: channel names must **not** be preceeded with ``#``.
		"""
		if id is not None:
			assert user is None, 'id and user cannot both be set.'
			assert group is None, 'id and group cannot both be set.'
			assert channel is None, 'id and channel cannot both be set.'
		elif user is not None:
			assert group is None, 'user and group cannot both be set.'
			assert channel is None, 'user and channel cannot both be set.'

			# Private message to user, get the IM name
			id = self.meta.find_im_by_user_name(user, auto_create=True)[0]
		elif group is not None:
			assert channel is None, 'group and channel cannot both be set.'

			# Message to private group, get the group name.
			id = self.meta.find_group_by_name(group)[0]
		elif channel is not None:
			# Message sent to a channel
			id = self.meta.find_channel_by_name(channel)[0]
		else:
			raise Exception, 'Should not reach here.'

		if send_with_api:
			return self.meta.api.chat.postMessage(
				token=self.meta.token,
				channel=id,
				text=text,
				parse=parse,
				link_names=link_names,
				unfurl_links=unfurl_links,
				unfurl_media=unfurl_media,
			)
		else:
			return self.sendCommand(
				type='message',
				channel=id,
				text=text,
				parse=parse,
				link_names=link_names,
				unfurl_links=unfurl_links,
				unfurl_media=unfurl_media,
			)
