import sys
import re
import codecs

def requirements_parser(file_path):
	string = get_string_from_file(file_path)
	get_packages_and_versions(string)

def get_string_from_file(file_path):
	input = codecs.open(file_path, mode="r", encoding="utf-8")
	string = input.read()
	return string

def get_packages_and_versions(string):
	regex = re.compile("^[^#].*==.*$",re.MULTILINE)
	requirements_list = regex.findall(string)
	requirements = {}
	for requirement in requirements_list:
		package, version = requirement.split('==')
		print "{package} {version}".format(package=package, version=version)