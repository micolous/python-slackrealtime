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

