"""
slackrealtime/testclient.py - Simple test client for Slack RTM
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
from argparse import ArgumentParser
from twisted.internet import reactor
from twisted.python import log
from sys import stdout
from . import connect, RtmProtocol


class TestClientProtocol(RtmProtocol):
	def onSlackEvent(self, event):
		log.msg(event)


def main():
	parser = ArgumentParser()

	parser.add_argument(
		'token',
		nargs=1,
		help='API key to use'
	)

	options = parser.parse_args()
	log.startLogging(stdout)

	conn = connect(options.token[0], TestClientProtocol)
	reactor.run()


if __name__ == '__main__':
	main()

