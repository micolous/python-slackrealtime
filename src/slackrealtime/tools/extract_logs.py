"""
slackrealtime/tools/extract_logs.py
Copyright 2016 Michael Farrell <http://micolous.id.au>

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
from argparse import ArgumentParser, FileType
from isodate import parse_datetime
import json
from pytz import utc
from sys import stdout
from ..api import SlackApi


def main():
	parser = ArgumentParser()

	parser.add_argument(
		'-t', '--token',
		required=True,
		help='API key to use')

	parser.add_argument(
		'-c', '--channel',
		required=True,
		help='Group to take logs from')

	parser.add_argument(
		'-s', '--start',
		required=True,
		help='ISO8601 start datetime to fetch logs from')

	parser.add_argument(
		'-e', '--end',
		required=True,
		help='ISO8601 end datetime to fetch logs until')

	parser.add_argument(
		'-C', '--chunk-size',
		type=int, default=1000,
		help='Number of messages at a time to grab from Slack API')
		
	parser.add_argument(
		'-o', '--output',
		type=FileType('wb'),
		required=True,
		help='Where to write the JSON file to')

	options = parser.parse_args()

	api = SlackApi()
	
	users = api.users.list(token=options.token)
	
	channels = api.groups.list(token=options.token)
	channel_id = None
	for channel in channels['groups']:
		if channel['name'] == options.channel:
			channel_id = channel['id']
			break
	
	if channel_id is None:
		raise Exception, 'channel not found'
	
	start_time = utc.localize(parse_datetime(options.start))
	end_time = utc.localize(parse_datetime(options.end))
	
	history = []
	latest = end_time
	while True:
		chunk = api.groups.history(token=options.token, channel=channel_id, latest=latest, oldest=start_time, count=options.chunk_size)
		history += chunk['messages']
		if not chunk['has_more']:
			break
		
		# Find new spot to search from
		latest = float(chunk['latest'])
		for msg in chunk['messages']:
			ts = float(msg['ts'])
			if ts < latest:
				latest = ts		

		# ...and continue!

	json.dump(history, options.output)
	print 'done grabbing, got %d messages' % len(history)

if __name__ == '__main__':
	main()

