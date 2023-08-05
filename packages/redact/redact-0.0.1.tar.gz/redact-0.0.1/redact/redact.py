import sys
import yaml
from os import path
import re

usage = """usage:

redact data.yaml

redact --extension tpl data.yaml"""


def get_data():
	if not sys.stdin.isatty():
		f = sys.stdin
	else:
		if len(sys.argv) > 1:
			if path.exists(sys.argv[-1]):
				f = open(sys.argv[-1])
			else:
				print("%s not found" % sys.argv[-1])
				sys.exit(1)
		else:
			return None
	data = yaml.safe_load(f)
	f.close()
	return data


def get_extension():
	extension = "tpl"
	for idx, arg in enumerate(sys.argv[:-1]):
		if arg == '--extension':
			extension = sys.argv[idx + 1]
	return extension


def parse(data, ext):
	global_names = {}
	local_names = {}
	for key, val in data.items():
		if isinstance(val, dict) or val is None:
			dotfile = "%s.%s" % (path.expanduser(key), ext)
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


def redact():
	data = get_data()
	if data is None:
		print(usage)
		sys.exit(0)
	ext = get_extension()
	global_names, local_names = parse(data, ext)
	if local_names:
		for tmpl, names in local_names.items():
			if render_from_tmpl("%s.%s" % (tmpl, ext), dict(global_names, **names), tmpl):
				print("wrote %s" % tmpl)
			else:
				print("faied to handle %s" % tmpl)
	else:
		print('nothing to do')
