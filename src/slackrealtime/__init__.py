"""
slackrealtime/__init__.py
Copyright 2014-2017 Michael Farrell <http://micolous.id.au>

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
from autobahn.twisted.websocket import WebSocketClientFactory, connectWS
import warnings

from .protocol import RtmProtocol
from .session import request_session

def connect(token, protocol=RtmProtocol, factory=WebSocketClientFactory, factory_kwargs=None, api_url=None, debug=False):
	"""
	Creates a new connection to the Slack Real-Time API.

	Returns (connection) which represents this connection to the API server.

	"""
	if factory_kwargs is None:
		factory_kwargs = dict()

	metadata = request_session(token, api_url)
	wsfactory = factory(metadata.url, **factory_kwargs)
	if debug:
		warnings.warn('debug=True has been deprecated in autobahn 0.14.0')

	wsfactory.protocol = lambda *a,**k: protocol(*a,**k)._seedMetadata(metadata)
	connection = connectWS(wsfactory)
	return connection

