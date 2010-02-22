#!python
from __future__ import print_function
import sys
import re
import inspect
import optparse
import shutil
import urllib2
from StringIO import StringIO

def get_options():
	global options
	parser = optparse.OptionParser()
	parser.add_option('-U', '--url', help="Trac URL from which to retrieve source")
	options, args = parser.parse_args()
	try:
		options.filename = args.pop()
	except IndexError:
		parser.error("Filename required")

# each of the replacement functions should have a docstring
#  which is a regular expression to be matched.

def replace_external_link(matcher):
	r"\[(?P<href>(?P<scheme>\w+)\://.+?) (?P<name>.+?)\]"
	return '`{name} <{href}>`_'.format(**matcher.groupdict())

def replace_wiki_link(matcher):
	r"\[wiki\:(?P<ref>.+?) (?P<name>.+?)\]"
	return '`{name} <TODO-fix wiki target {ref}>`_'.format(**matcher.groupdict())

# character array indexed by level for characters
heading_characters = [None, '*', '=', '-', '^']

def replace_headings(matcher):
	r"^(?P<level>=+) (?P<name>.*) (?P=level)$"
	level = len(matcher.groupdict()['level'])
	char = heading_characters[level]
	name = matcher.groupdict()['name']
	return '\n'.join([name, char*len(name)])

def indent(block):
	add_indent = lambda s: '    ' + s
	lines = StringIO(block)
	i_lines = map(add_indent, lines)
	return ''.join(i_lines)

def replace_inline_code(matcher):
	r"\{\{\{(?P<code>[^\n]*?)\}\}\}"
	return '``{code}``'.format(**matcher.groupdict())

def replace_code_block(matcher):
	r"\{\{\{\n(?P<code>(.|\n)*?)^\}\}\}"
	return '::\n\n' + indent(matcher.groupdict()['code'])

def replace_page_outline(matcher):
	r"\[\[PageOutline\]\]\n"
	return ''


# a number of the files end in
"""{{{
#!html
<h2 class='compatibility'>Older versions</h2>
}}}""" # and everything after is garbage, so just remove it.
def remove_2x_compat_notes(matcher):
	r"\{\{\{\n#!html\n<h2(.|\n)*"
	return ''

replacements = [remove_2x_compat_notes] + \
	[func for name, func in globals().items() if name.startswith('replace_')]

def normalize_linebreaks(text):
	return text.replace('\r\n', '\n')

def convert_file():
	filename = options.filename
	if options.url:
		text = urllib2.urlopen(options.url).read()
		text = normalize_linebreaks(text)
	else:
		shutil.copy(filename, filename+'.bak')
		text = open(filename).read()
	# iterate over each of the replacements and execute it
	new_text = text
	for repl in replacements:
		pattern = re.compile(inspect.getdoc(repl), re.MULTILINE)
		new_text = pattern.sub(repl, new_text)

	open(filename, 'w').write(new_text)
	print("done")


def handle_command_line():
	get_options()
	convert_file()

if __name__ == '__main__':
	handle_command_line()