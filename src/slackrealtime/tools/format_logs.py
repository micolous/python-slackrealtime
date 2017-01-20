"""
slackrealtime/tools/format_logs.py
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
from datetime import datetime
import json
import re
from pytz import timezone, utc
from sys import stdout
from ..api import SlackApi

USERNAME_RE = re.compile(r'\<@(U[A-Z0-9]+)\|([a-zA-Z0-9]+)\>')
BOLD_RE = re.compile(r'(\s)\*([^*\n]+?)\*')
ITALIC_RE = re.compile(r'(\s)_([^_\n]+?)_') 
PRETTY_HYPERLINK_RE = re.compile(r'\<(http[^>|\n]+?)(\|([^>\n]+?))?\>')

def slack_to_markdown(i):
	# Transform bold to real bold
	o = BOLD_RE.sub(lambda m: ('%s**%s**' % (m.group(1), m.group(2))), i)
	o = ITALIC_RE.sub(lambda m: ('%s*%s*' % (m.group(1), m.group(2))), o)
	o = USERNAME_RE.sub(lambda m: ('**@%s**' % (m.group(2),)), o)
	o = PRETTY_HYPERLINK_RE.sub(lambda m: ' %s ' % (('[%s](%s)' % (m.group(3), m.group(1))) if m.group(2) else m.group(1)), o)
	
	return o

def format_logs(input_files, output_file, tz='UTC'):
	tz = timezone(tz)
	start_time = utc.localize(datetime.utcnow()).astimezone(tz)

	logs = []
	for input_file in input_files:
		logs += json.load(input_file)
		input_file.close()

	# Do this first, because we want a float later.
	for e in logs:
		e['ts'] = float(e['ts'])

	# Sort the logs chronologically
	logs.sort(key=lambda x: x['ts'])

	# Now start converting bits.
	output_file.write('''# slackrealtime format_logs

Dump generated %(timestamp)s

All times shown are `%(tz)s`.

## Input files

* %(input_files)s


## Messages

''' % dict(
		timestamp=start_time.isoformat(),
		input_files='\n* '.join([f.name for f in input_files]),
		tz=tz.zone))

	last_day = None

	# Now write out all the messages.
	for m in logs:
		ts = utc.localize(datetime.utcfromtimestamp(m['ts'])).astimezone(tz)

		# Write out the date header if it differs
		if ts.date() != last_day:
			last_day = ts.date()
			output_file.write('### %s\n\n' % last_day.isoformat())
		
		if m['type'] == 'message':
			output_file.write('**%(ts)s**: **@%(username)s**: %(text)s\n\n' % dict(
				ts=ts.time().replace(microsecond=0).isoformat(),
				username=m['user_name'],
				text=slack_to_markdown(m['text'])))
				
			# TODO: handle reactions
		else:
			print ('Unhandled type %s' % m['type'])
			
	output_file.flush()
	output_file.close()


def main():
	parser = ArgumentParser()
	
	parser.add_argument('input_files', nargs='+',
		type=FileType('rb'), help='Input JSON files to mark down')

	parser.add_argument('-o', '--output', required=True,
		type=FileType('wb'), help='Output Markdown file')

	parser.add_argument('-t', '--tz', default='UTC',
		help='Timezone to display times in [default: %(default)s]')

	options = parser.parse_args()
	format_logs(options.input_files, options.output, options.tz)

if __name__ == '__main__':
	main()

