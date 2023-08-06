# Copyright (c) 2013 Daniel Foote.
#
# See the file LICENSE for copying permission.

import sys
import json
import os

# Try to import Yaml. This only works if pyyaml is installed.
# If we can't do this, then we don't support yaml configuration files.
try:
	import yaml
except ImportError, ex:
	yaml = None

class PaasmakerInterfaceError(Exception):
	pass

class PaasmakerInterface(object):
	"""
	A helper library for applications, to be easily able to read
	in their services configuration when running on Paasmaker.

	Also contains the ability to load a configuration file, in
	JSON format, if the application is not running on Paasmaker.
	This allows for easy development using the exact same code
	paths for production.

	:arg list override_paths: A list of paths to look for configuration
		files. For example, supply ``['../project-name.json']`` to look
		one level above your project root.
	"""
	def __init__(self, override_paths):
		if isinstance(override_paths, basestring):
			override_paths = [override_paths]

		self._override_paths = override_paths
		self._is_on_paasmaker = False
		self._variables = {}
		self._services = {}
		# It's over 9000.
		self._port = 9001

		self._parse_metadata()

	def _parse_metadata(self):
		# Parse the metadata, or load the override configuration
		# if we're not on a Paasmaker node.
		if 'PM_SERVICES' in os.environ and 'PM_METADATA' in os.environ:
			# We're running on a Paasmaker node.
			self._is_on_paasmaker = True

			self._services = json.loads(os.environ['PM_SERVICES'])
			self._variables = json.loads(os.environ['PM_METADATA'])

			if 'PM_PORT' in os.environ:
				self._port = int(os.environ['PM_PORT'])
		else:
			# We're not on a node. Locate and load a configuration
			# file.
			self._load_configuration_file()

	def _load_configuration_file(self):
		for path in self._override_paths:
			user_path = os.path.expanduser(path)

			if os.path.exists(user_path):
				# It exists.
				raw = open(path, 'r').read()

				if user_path.endswith('.yml'):
					# Try to load as Yaml.
					if not yaml:
						raise PaasmakerInterfaceError("Tried to read a YAML configuration file, but 'pyyaml' not installed.")

					data = yaml.safe_load(raw)

					if not data:
						raise PaasmakerInterfaceError("Failed to parse YAML.")

				elif user_path.endswith('.json'):
					# Try to load as JSON.
					data = json.loads(raw)

				self._store_configuration(user_path, data)
				return

		raise PaasmakerInterfaceError("Could not find configuration file to load.")

	def _store_configuration(self, filename, data):
		# Check that any required sections are present, raising exceptions
		# if not.
		if 'services' not in data:
			data['services'] = {}

		if 'workspace' not in data:
			data['workspace'] = {}

		if 'node' not in data:
			data['node'] = {}

		if 'application' not in data:
			raise PaasmakerInterfaceError("You must supply an application section in your configuration.")

		if 'port' in data:
			self._port = int(data['port'])

		# Check for a few keys in the application section.
		required_keys = ['name', 'version', 'workspace', 'workspace_stub']
		for key in required_keys:
			if key not in data['application']:
				raise PaasmakerInterfaceError("Missing required key %s in application configuration." % key)

		# Store it all away.
		self._services = data['services']
		self._variables = data

	def get_service(self, name):
		"""
		Return the configuration for a named service. If the service
		is not present, raises a ``NameError``.

		:arg str name: The name of the service to fetch.
		"""
		if name in self._services:
			return self._services[name]
		else:
			raise NameError("No such service %s." % name)

	def get_all_services(self):
		"""
		Return a dict containing all services.
		"""
		return self._services

	def is_on_paasmaker(self):
		"""
		Determine if this application is currently running on
		Paasmaker or not.
		"""
		return self._is_on_paasmaker

	def get_application_name(self):
		"""
		Get the name of this application.
		"""
		return self._variables['application']['name']

	def get_application_version(self):
		"""
		Get the version number of this application.
		"""
		return self._variables['application']['version']

	def get_workspace_name(self):
		"""
		Get the workspace name - this is a full name.
		"""
		return self._variables['application']['workspace']

	def get_workspace_stub(self):
		"""
		Get the workspace stub - this is the short url-friendly
		name for the workspace.
		"""
		return self._variables['application']['workspace_stub']

	def get_node_tags(self):
		"""
		Get any node specific tags. These are defined by the system
		administrator per node.
		"""
		return self._variables['node']

	def get_workspace_tags(self):
		"""
		Get any workspace specific tags. These are configured
		per workspace.
		"""
		return self._variables['workspace']

	def get_port(self):
		"""
		Fetch the TCP port that your application should be listening on.
		"""
		return self._port