"""fragment

Usage:
  fragment gen [--output=<folder>] [--extension=<md>] [--filter=<headlines>] <source_folder>
  fragment reset-templates <source_folder>

Options:
  -h --help     Show this screen.
  --version     Show version.

Example:
  fragment gen --output /var/www/ --filter public,codesnip ~/wiki/diary
"""

import os
from collections import defaultdict
import shutil
import pkg_resources

import markdown2
from docopt import docopt
from pystache import render

dist = pkg_resources.get_distribution('fragment')


def mkdir_p(path):
	path = os.path.dirname(path)
	if not os.path.isdir(path):
		os.makedirs(path)


def get_markdowns(path, extension):
	extension = "." + extension
	walker = os.walk(path)
	_, _, markdowns = next(walker)
	for m in markdowns:
		name, ext = os.path.splitext(m)
		if ext == extension:
			yield name, ext


def split_by_headline(content):
	headline = None
	body = []
	for line in content.splitlines():
		if line[:2] == '# ':
			if headline is not None:
				yield (headline, "\n".join(body))
			headline = line[2:]
			body = []
		else:
			body.append(line)
	yield (headline, "\n".join(body))


def get_template(source_folder, name):
	with open(os.path.join(source_folder, name)) as f:
		return f.read()


def update_html(src, output, template, includes):
	with open(src, 'r') as f:
		for headline, body in split_by_headline(f.read()):
			if headline in includes or len(includes) == 0:
				output_path = output(headline)
				mkdir_p(output_path)
				body = markdown2.markdown(body)
				with open(output_path, 'w') as o:
					o.write(render(template, locals()))
					print("wrote %s" % output_path)
				yield headline


def copy_assets(source_folder, output_folder):
	shutil.copy(os.path.join(source_folder, 'style.css'), output_folder)
	print("wrote %s" % os.path.join(output_folder, 'style.css'))


def ensure_template(source_folder, force=False):
	for template in ['index.html', 'single.html', 'style.css']:
		if not os.path.exists(os.path.join(source_folder, template)) or force:
			shutil.copy(os.path.join(dist.location, 'fragment', template),
					os.path.join(source_folder, template))
			print("wrote %s" % os.path.join(source_folder, template))


def generate(source_folder, output, includes, extension):

	markdowns = get_markdowns(source_folder, extension)

	ensure_template(source_folder)

	single_template = get_template(source_folder, 'single.html')
	index_template = get_template(source_folder, 'index.html')

	headlines = defaultdict(list)
	for name, ext in markdowns:
		for headline in update_html(os.path.join(source_folder, name + ext),
				lambda headline: os.path.join(output, headline, name + '.html'),
				single_template,
				includes):
			headlines[headline].append(name)

	for headline, files in headlines.items():
		index_path = os.path.join(output, headline, 'index.html')
		links = ({"link": f} for f in files)
		with open(index_path, 'w') as index:
			index.write(render(index_template, locals()))
			print('wrote index %s %d links' % (index_path, len(files)))
			copy_assets(source_folder, os.path.join(output, headline))


def main():
	args = docopt(__doc__, version='fragment 0.0.2')
	source_folder = args['<source_folder>']

	if args['reset-templates']:
		ensure_template(source_folder, True)
	elif args['gen']:
		extension = 'md' if args['--extension'] is None else args['--extension']
		output = source_folder if args['--output'] is None else args['--output']
		includes = [] if args['--filter'] is None else args['--filter'].split(',')
		generate(source_folder, output, includes, extension)
