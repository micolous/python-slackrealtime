"""
slackrealtime/factory.py
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

from __future__ import absolute_import
from autobahn.twisted.websocket import WebSocketClientFactory
from twisted.internet import reactor


class DyingWebSocketClientFactory(WebSocketClientFactory):
	"""
	Implements a light wrapper on autobahn's WebSocketClientFactory in order to
	stop the Twisted reactor on a connection failure or other connection loss.

	This has the effect of making the bot quit when it loses connection,
	allowing it to be restarted.

	The "better" way is to handle the disconnect and then initiate a new RTM
	session on a connection loss, but it also means rewriting lots of the
	metadata.

	Without this alternate factory, when the connection to the Slack RTM service
	is lost, the reactor will keep running, effectively making your bot "hang".

	This can be used with the following code::

		conn = connect(
			slack_api_token,
			protocol=MySlackbotProtocol,
			factory=DyingWebSocketClientFactory
		)

	"""
	def clientConnectionLost(self, connector, reason):
		print 'Connection lost:', reason
		reactor.stop()


	def clientConnectionFailed(self, connector, reason):
		print 'Connection failed:', reason
		reactor.stop()

