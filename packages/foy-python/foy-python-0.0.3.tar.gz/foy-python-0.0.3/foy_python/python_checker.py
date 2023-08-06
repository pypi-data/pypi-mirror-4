import sh
import sys
import re

def check_pypi_for_updates(package):
	yolk = sh.Command("yolk")
	output = str(yolk("-V", package))
	if output:
		regex = re.compile("^.*$",re.MULTILINE)
		avaliable_versions = regex.findall(output)
		_, version = avaliable_versions[0].split()
		print version