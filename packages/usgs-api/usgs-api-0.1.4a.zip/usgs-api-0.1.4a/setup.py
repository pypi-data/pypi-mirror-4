__author__ = 'nicksantos'

from setuptools import setup

setup(name='usgs-api',
	version='0.1.4a',
	long_description='''Please note that the module name is usgs, not usgs-api for importing. Also, Windows users may
	need to install `pandas <http://pypi.python.org/pypi/pandas/>`_ separately via the binary installer. Pandas, in turn, requires numpy, which may also
	need to be installed using the binary installer if you do not already have it installed.

	A wrapper around the USGS Water Information System JSON API that provides native Python access. Documentation is available at Read the Docs (https://usgs-api.readthedocs.org/en/latest). The code and documentation are licensed under a Creative Commons Attribution-ShareAlike 3.0 Unported License.
	''',
    description='A Python wrapper for the USGS National Water Information System JSON API',
	url='https://bitbucket.org/UltraAyla/usgs-api',
	author='Nick Santos',
	author_email='python@nicksantos.com',
    keywords=('usgs','api','nwis','water','data','wrapper'),
	license='Creative Commons Attribution Sharealike 3.0 Unported',
	packages=['usgs','docs'],
	install_requires=[
		'pandas',
		],
	zip_safe=False)

