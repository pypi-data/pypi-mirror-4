from os.path import dirname, abspath, join
from setuptools import setup

setup(
    name='foy-python',
    description='Python handler for fountain-of-youth',
    author='Renata Carreira',
    author_email='re.carreira@gmail.com',
    url='https://github.com/fountain-of-youth/foy-python-handler',
    license='LICENSE.txt',
    version='0.0.3',
    zip_safe=False,
    include_package_data=True,
    entry_points={
        'console_scripts':
        ['foy.python = foy_python.cli:main'],
        },
    packages=[
        'foy_python',
        ],
    install_requires=[
        'yolk==0.4.3',
		'sh==1.07',
        'pytest==2.3.4'
        ],
)
