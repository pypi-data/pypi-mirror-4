import sys
import yaml
from os import path
import re
from opster import command


def get_data(filename):
	if not sys.stdin.isatty():
		f = sys.stdin
	else:
		if filename:
			if path.exists(filename):
				f = open(filename)
			else:
				print("%s not found" % filename)
				sys.exit(1)
		else:
			return None
	data = yaml.safe_load(f)
	f.close()
	return data


def parse(data, extension):
	global_names = {}
	local_names = {}
	for key, val in data.items():
		if isinstance(val, dict) or val is None:
			dotfile = "%s.%s" % (path.expanduser(key), extension)
			print("found %s" % dotfile)
			if path.exists(dotfile) and not path.isdir(dotfile):
				local_names[path.expanduser(key)] = {} if val is None else val
			else:
				print("%s not found" % dotfile)
		else:
			global_names[key] = val
	return global_names, local_names


def render(tmpl, names):
	def get_val_by_name(obj):
		key = obj.group(1)
		if key in names:
			return names[key]
		else:
			return ''
	return re.sub(r'#\{([a-zA-Z0-9_-]+)\}', get_val_by_name, tmpl)


def render_from_tmpl(tmpl, names, output):
	with open(tmpl) as i:
		result = render(i.read(), names)
		with open(output, 'w') as o:
			o.write(result)
			return True


@command(usage='[--extension tpl] data.yaml')
def main(dirname=None, extension=('e', 'tpl', 'extion of the template file')):
	'''rendering dotfiles from template'''
	data = get_data(dirname)
	if data is None:
		raise command.Error('no input')
	global_names, local_names = parse(data, extension)
	if local_names:
		for tmpl, names in local_names.items():
			if render_from_tmpl("%s.%s" % (tmpl, extension), dict(global_names, **names), tmpl):
				print("wrote %s" % tmpl)
			else:
				print("faied to handle %s" % tmpl)
	else:
		print('nothing to do')


def redact():
	main.command()
