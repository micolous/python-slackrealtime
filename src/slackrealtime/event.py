"""
slackrealtime/event.py - Event handling for Slack RTM.
Copyright 2014-2015 Michael Farrell <http://micolous.id.au>

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

from datetime import datetime
from pytz import UTC

class BaseEvent(object):
	def __init__(self, body):
		self._b = body

		# Not all events have a timestamp.
		if 'ts' in self._b:
			# Time value is present in the message, parse it.
			self.has_ts = True
			self.ts = datetime.fromtimestamp(float(self._b['ts']), UTC)
		else:
			# Time value is missing in the message, infer it based on recieve time.
			self.has_ts = False
			self.ts = datetime.now(UTC)

	def __getattr__(self, attr):
		attr = unicode(attr)
		if attr in self._b:
			return self._b[attr]
		else:
			raise AttributeError, attr

	def copy(self):
		return decode_event(self._b)

	def __str__(self):
		return '<BaseEvent: @%r %r>' % (self.ts, self._b)

class Unknown(BaseEvent):
	def __str__(self):
		return '<Unknown: @%r %r>' % (self.ts, self._b)


class Hello(BaseEvent): pass

class Message(BaseEvent):
	def __getattr__(self, attr):
		try:
			return super(Message, self).__getattr__(attr)
		except AttributeError:
			if attr in ['user', 'username', 'subtype', 'attachments']:
				# Bot message types are different
				return None

			# Raise other AttributeErrors
			raise

	def __str__(self):
		subtype = self.subtype
		if subtype is None:
			subtype = ''

		user = self.user
		if user is None:
			# Bot
			user = self.username
		else:
			user = u'@' + user

		attachments = ''
		if self.attachments:
			attachments = ' attachments=' + repr(self.attachments)
			if len(attachments) > 40:
				attachments = attachments[:37] + '...'

		return '<Message(%s): %s: <%s> %s %s>' % (subtype, self.channel, user, self.text, attachments)

class BaseHistoryChanged(BaseEvent):
	def __init__(self, body):
		super(BaseHistoryChanged, self).__init__(body)
		self.latest = datetime.fromtimestamp(float(self._b['latest']), UTC)
		self.event_ts = datetime.fromtimestamp(float(self._b['event_ts']), UTC)

class BaseReactionEvent(BaseEvent):
	def __init__(self, body):
		super(BaseReactionEvent, self).__init__(body)
		self.event_ts = datetime.fromtimestamp(float(self._b['event_ts']), UTC)

class Ack(BaseEvent): pass
class ChannelArchive(BaseEvent): pass
class ChannelCreated(BaseEvent): pass
class ChannelDeleted(BaseEvent): pass
class ChannelHistoryChanged(BaseHistoryChanged): pass
class ChannelJoined(BaseEvent): pass
class ChannelLeft(BaseEvent): pass
class ChannelMarked(BaseEvent): pass
class ChannelRename(BaseEvent): pass
class ChannelUnarchive(BaseEvent): pass

class ImClose(BaseEvent): pass
class ImCreated(BaseEvent): pass
class ImHistoryChanged(BaseHistoryChanged): pass
class ImMarked(BaseEvent): pass
class ImOpen(BaseEvent): pass

class GroupJoined(BaseEvent): pass
class GroupLeft(BaseEvent): pass
class GroupOpen(BaseEvent): pass
class GroupClose(BaseEvent): pass
class GroupArchive(BaseEvent): pass
class GroupUnarchive(BaseEvent): pass
class GroupRename(BaseEvent): pass
class GroupMarked(BaseEvent): pass
class GroupHistoryChanged(BaseHistoryChanged): pass

class BotAdded(BaseEvent): pass
class BotChanged(BaseEvent): pass

class ReactionAdded(BaseReactionEvent): pass
class ReactionRemoved(BaseReactionEvent): pass

class PresenceChange(BaseEvent): pass
class UserChange(BaseEvent): pass
class UserTyping(BaseEvent): pass
class TeamPrefChange(BaseEvent): pass
class TeamJoin(BaseEvent): pass

EVENT_HANDLERS = {
	u'hello': Hello,
	u'message': Message,
	u'channel_archive': ChannelArchive,
	u'channel_created': ChannelCreated,
	u'channel_deleted': ChannelDeleted,
	u'channel_history_changed': ChannelHistoryChanged,
	u'channel_joined': ChannelJoined,
	u'channel_left': ChannelLeft,
	u'channel_marked': ChannelMarked,
	u'channel_rename': ChannelRename,
	u'channel_unarchive': ChannelUnarchive,

	u'im_close': ImClose,
	u'im_created': ImCreated,
	u'im_history_changed': ImHistoryChanged,
	u'im_marked': ImMarked,
	u'im_open': ImOpen,

	u'group_joined': GroupJoined,
	u'group_left': GroupLeft,
	u'group_open': GroupOpen,
	u'group_close': GroupClose,
	u'group_archive': GroupArchive,
	u'group_unarchive': GroupUnarchive,
	u'group_rename': GroupRename,
	u'group_marked': GroupMarked,
	u'group_history_changed': GroupHistoryChanged,

	u'bot_added': BotAdded,
	u'bot_changed': BotChanged,

	u'reaction_added': ReactionAdded,
	u'reaction_removed': ReactionRemoved,

	u'presence_change': PresenceChange,
	u'user_change': UserChange,
	u'user_typing': UserTyping,
	u'team_pref_change': TeamPrefChange,
	u'team_join': TeamJoin,
}

def decode_event(event):
	event = event.copy()
	if 'type' not in event:
		# This is an acknowledgement of a previous command.
		return Ack(event)
	elif event['type'] in EVENT_HANDLERS:
		t = event['type']
		return EVENT_HANDLERS[t](event)
	else:
		return Unknown(event)

