from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(
	name='ckanext-nationdata',
	version=version,
	description="Ckan Extension for the Nation Media Group data portal",
	long_description="""\
	""",
	classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
	keywords='',
	author='Jude Mwenda',
	author_email='judemwenda@gmail.com',
	url='http://www.afrigeo.com',
	license='GPL 2',
	packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
	namespace_packages=['ckanext', 'ckanext.nationdata'],
	include_package_data=True,
	zip_safe=False,
	install_requires=[
		# -*- Extra requirements: -*-
	],
	entry_points=\
	"""
        [ckan.plugins]
	# Add plugins here, eg
	# myplugin=ckanext.nationdata:PluginClass
        nationdata=ckanext.nationdata.plugin:NationDataPlugin
	""",
)
