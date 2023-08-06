# django-salesforce
#
# by Phil Christensen
# (c) 2012-2013 Freelancers Union (http://www.freelancersunion.org)
# See LICENSE.md for details
#

DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.sqlite3',
		'NAME': 'salesforce_testrunner_db',
	},
	'salesforce': {
		'ENGINE': 'salesforce.backend',
		"CONSUMER_KEY" : '3MVG9GiqKapCZBwFshmMJ7ry5oSWhmdsiCNrTorw.cBx3EOvNPfkX6mPksUdHXoH6hI4q0UX8S7uyHaseqHJN',
		"CONSUMER_SECRET" : '3051006413681161256',
		'USER': 'admins@freelancersunion.org.pac2',
		'PASSWORD': 'Vs^o=D9yu3',
		'HOST': 'https://test.salesforce.com',
	},
}

