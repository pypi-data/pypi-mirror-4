Paasmaker Python Interface Library
==================================

This is a simple Python library that is designed to read in the Paasmaker
configuration of the container, falling back to a custom configuration
file in development.

You can read more about the Paasmaker PaaS at
`http://paasmaker.org/ <http://paasmaker.org/>`_.

Usage
-----

In the startup of your application create an interface object. Supply the
constructor with a list of locations to look for override configuration
files for development. You won't need override configuration files if you
are using the development directory SCM in Paasmaker.

.. code-block:: python

	import pminterface

	interface = pminterface.PaasmakerInterface(['../my-project.yml'])

	interface.is_on_paasmaker() # Returns true if on Paasmaker.

	# Raises NameError if no such service exists.
	service = interface.get_service('named-service')
	# service now is a dict of the parameters. Typically this will
	# have the keys 'hostname', 'username', 'password', etc. Use this
	# to connect to revelant services.

	# Get other application metadata.
	application = interface.get_application_name()

Override configuration files can be in either YAML or JSON format. If using
the YAML format, be sure to install ``pyyaml`` first. If ``pyyaml`` isn't present,
only the JSON format is supported, and it will raise an exception when
trying to read YAML files.

Example YAML configuration file:

.. code-block:: yaml

	services:
	  parameters:
	    foo: bar

	application:
	  name: test
	  version: 1
	  workspace: Test
	  workspace_stub: test

Example JSON configuration file:

.. code-block:: json

	{
		"services": {
			"parameters": {
				"foo": "bar"
			}
		},
		"application": {
			"name": "test",
			"version": 1,
			"workspace": "Test",
			"workspace_stub": "test"
		}
	}

Development
-----------

You can run the unit tests with the ``test.py`` script in the
root directory.

The code is currently stored on BitBucket at:

git@bitbucket.org:paasmaker/paasmaker-interface-python.git

Feel free to fork and submit pull requests.