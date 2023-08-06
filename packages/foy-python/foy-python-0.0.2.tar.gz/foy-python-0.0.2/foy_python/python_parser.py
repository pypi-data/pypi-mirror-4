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

def get_operator(requirement):
    equal = re.compile(".*==.*")
    equal_major = re.compile(".*>=.*")
    equal_minor = re.compile(".*<=.*")
    major = re.compile(".*>.*")
    minor = re.compile(".*<.*")
    op = ""
    if equal.match(requirement):
        op = "=="
    elif equal_major.match(requirement):
        op = ">="
    elif equal_minor.match(requirement):
        op = "<="
    elif major.match(requirement):
        op = ">"
    elif minor.match(requirement):
        op = "<"
    return op

def get_packages_and_versions(string):
    regex = re.compile("^[^#].*[==,>,>=]\S*",re.MULTILINE)
    requirements_list = regex.findall(string)
    for requirement in requirements_list:
        op = get_operator(requirement)
        package, version = requirement.split(op)
        print "{package} {version}".format(package=package, version=version)