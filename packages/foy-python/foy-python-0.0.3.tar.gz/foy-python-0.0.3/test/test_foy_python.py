from foy_python import check_pypi_for_updates
from foy_python import requirements_parser
from foy_python import get_string_from_file
from foy_python import get_operator
from foy_python import get_packages_and_versions
import pytest
import os


here = os.path.dirname(os.path.abspath(__file__))
TESTS_DATA = os.path.join(here, 'data')

REQUIREMENTS_STRING = u'#comment\nFlask==0.9\nJinja2==2.6\nrtmp2img>0.1.5\n#another comment\nWerkzeug<=0.8.3\nrequests==0.14.2\nDjango<1.4.5\n#and another comment\nsh>=1.07\nwsgiref==0.1.2 #what if...\nyolk==0.4.3'

def test_get_string_from_file():
	input_file_path = os.path.join(TESTS_DATA, 'requirements_test.txt')
	assert get_string_from_file(input_file_path) == REQUIREMENTS_STRING

def test_foy_should_get_the_right_operator():
    ops = [get_operator('rtmp2img==0.1.5'), get_operator('rtmp2img>=0.1.5'), get_operator('rtmp2img<=0.1.5'), get_operator('rtmp2img>0.1.5'), get_operator('rtmp2img<0.1.5')]
    assert ops == ['==', '>=', '<=', '>', '<']

#TODO test for get_packages_and_versions and check_pypi_for_updates