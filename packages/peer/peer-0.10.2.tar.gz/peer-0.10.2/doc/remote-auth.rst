Remote Authentication
=====================

In this section you will learn how to configure your PEER instance to allow
other authentication mechanism besides the standard local authentication
system based on user names and passwords stored locally.

There are three other ways to handle the authentication in PEER:

- SAML
- Remote User
- x509 client certificates

Other Django ways may apply such as LDAP authentication backends but they
are out of the scope of this document.

SAML Authentication
-------------------

With this method your PEER instance is said to be federated with another
system that handles the identity of your users. Using standard SAML terminology
PEER is the Service Provider and the other system is the Identity Provider.

Actually PEER is an application protected by an embedded native Service
Provider implemented using the djangosaml2 library, which in turn, use the
PySAML2 library. But enough with the buzzwords, let's see how to configure
the PEER instance in this manner.

There are two things you need to setup to configure the SAML support:

1. **local_settings.py** as you may know, it is the main Django
   configuration file.
2. **PySAML2** specific files such as the certificate and the remote metadata.

Changes in the local_settings.py file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default SAML support is disabled in PEER and you need to explicitly enable
it with the SAML_ENABLED option:

.. code-block:: python

  SAML_ENABLED = True

This will change the login and logout pages adding the necessary options to let
the user start and finish his session with the help of a SAML Identity Provider.

Some Identity Providers do not handle the logout process very well since it is
a quite complex operation not very reliable in all the cases. For this reason
it is recommended to set the SESSION_EXPIRE_AT_BROWSER_CLOSE Django option to
True when enabling SAML:

.. code-block:: python

  SESSION_EXPIRE_AT_BROWSER_CLOSE = SAML_ENABLED

What this mean is that when the user closes the browser application, the
session will be destroyed.

Finally, there is a third option that controls if the PEER instance should let
any user that comes from a registered IdP to start the session or only allow
those users that previously existed in the database. This option is named
SAML_CREATE_UNKNOWN_USER and by default it is True:

.. code-block:: python

  SAML_CREATE_UNKNOWN_USER = True

By default the PEER instance is configured to store certain fields of the
user identity in the Django user object. It is not recommended to change
this option unless you know what you are doing since some parts of PEER may
stop working. The default value for this SAML_ATTRIBUTE_MAPPING is as this:

.. code-block:: python

  SAML_ATTRIBUTE_MAPPING = {
      'mail': ('username', 'email'),
      'givenName': ('first_name', ),
      'sn': ('last_name', ),
      }

Which means that the `mail` attribute that comes from the SAML assertion will
be stored in the Django user fields `username` and `email`. The `givenName`
SAML attribute will be mapped to the `first_name` Django user field and the
`sn` SAML attribute will be mapped to the `last_name` Django user field.


PySAML2 specific files and configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once you have finished configuring your Django project you have to start
configuring PySAML2. If you use this library directly you need to put your
configuration options in a file and initialize PySAML2 with the path to
that file.

With djangosaml2 you just put the same information in the Django
local_settings.py file under the SAML_CONFIG option. Following is a typical
configuration for protecting a PEER instance:

.. code-block:: python

  from os import path
  import saml2
  BASEDIR = path.dirname(path.abspath(__file__))
  PEER_HOST = 'localhost'
  PEER_PORT = '8000'
  PEER_BASE_URL = 'http://' + PEER_HOST + ':' + PEER_PORT

  SAML_CONFIG = {
    # full path to the xmlsec1 binary programm
    'xmlsec_binary': '/usr/bin/xmlsec1',

    # your entity id, usually your subdomain plus the url to the metadata view
    'entityid': PEER_BASE_URL + '/saml2/metadata/',

    # directory with attribute mapping
    'attribute_map_dir': path.join(BASEDIR, 'pysaml2', 'attributemaps'),

    # this block states what services we provide
    'service': {
        # we are just a lonely SP
        'sp' : {
            'name': 'PEER SP',
            'endpoints': {
                # url and binding to the assetion consumer service view
                # do not change the binding or service name
                'assertion_consumer_service': [
                    (PEER_BASE_URL + '/saml2/acs/', saml2.BINDING_HTTP_POST),
                    ],
                # url and binding to the single logout service view
                # do not change the binding or service name
                'single_logout_service': [
                    (PEER_BASE_URL + '/saml2/ls/', saml2.BINDING_HTTP_REDIRECT),
                    ],
                },

             # attributes that this project need to identify a user
            'required_attributes': ['mail'],

             # attributes that may be useful to have but not required
            'optional_attributes': ['givenName', 'sn'],

            # in this section the list of IdPs we talk to are defined
            'idp': {
                # we do not need a WAYF service since there is
                # only an IdP defined here. This IdP should be
                # present in our metadata

                # the keys of this dictionary are entity ids
                'https://localhost/simplesaml/saml2/idp/metadata.php': {
                    'single_sign_on_service': {
                        saml2.BINDING_HTTP_REDIRECT: 'https://localhost/simplesaml/saml2/idp/SSOService.php',
                        },
                    'single_logout_service': {
                        saml2.BINDING_HTTP_REDIRECT: 'https://localhost/simplesaml/saml2/idp/SingleLogoutService.php',
                        },
                    },
                },
            },
        },

    # where the remote metadata is stored
    'metadata': {
        'local': [path.join(BASEDIR, 'pysaml2', 'remote_metadata.xml')],
        },

    # set to 1 to output debugging information
    'debug': 1,

    # certificate
    'key_file': path.join(BASEDIR, 'mycert.key'),  # private part
    'cert_file': path.join(BASEDIR, 'mycert.pem'),  # public part

    # own metadata settings
    'contact_person': [
        {'given_name': 'Lorenzo',
         'sur_name': 'Gil',
         'company': 'Yaco Sistemas',
         'email_address': 'lgs@yaco.es',
         'contact_type': 'technical'},
        {'given_name': 'Angel',
         'sur_name': 'Fernandez',
         'company': 'Yaco Sistemas',
         'email_address': 'angel@yaco.es',
         'contact_type': 'administrative'},
        ],
    # you can set multilanguage information here
    'organization': {
        'name': [('Yaco Sistemas', 'es'), ('Yaco Systems', 'en')],
        'display_name': [('Yaco', 'es'), ('Yaco', 'en')],
        'url': [('http://www.yaco.es', 'es'), ('http://www.yaco.com', 'en')],
        },
    'valid_for': 24,  # how long is our metadata valid
    }

.. note::

  Please check the `PySAML2 documentation`_ for more information about
  these and other configuration options.

.. _`PySAML2 documentation`: http://packages.python.org/pysaml2/

There are several external files and directories you have to create according
to this configuration.

The xmlsec1 binary was mentioned in the installation section. Here, in the
configuration part you just need to put the full path to xmlsec1 so PySAML2
can call it as it needs.

The ``metadata`` option is a dictionary where you can define several types of
metadata for remote entities. Usually the easiest type is the ``local`` where
you just put the name of a local XML file with the contents of the remote
entities metadata. This XML file should be in the SAML2 metadata format.

The ``key_file`` and ``cert_file`` options references the two parts of a
standard x509 certificate. You need it to sign your metadata an to encrypt
and decrypt the SAML2 assertions.

.. note::

  Check your openssl documentation to generate a test certificate but don't
  forget to order a real one when you go into production.


IdP setup
~~~~~~~~~

Congratulations, you have finished configuring the SP side of the federation.
Now you need to send the entity id and the metadata of this new SP to the
IdP administrators so they can add it to their list of trusted services.

You can get this information starting your Django development server and
going to the http://localhost:8000/saml2/metadata url. If you have included
the djangosaml2 urls under a different url prefix you need to correct this
url.


Remote User Authentication
--------------------------

The REMOTE_USER header authentication is a common way to delegate the
authentication step to the web server. It doesn't matter how the
web server handles the authentication, when a user is authenticated, the
web server puts the user information in a REMOTE_USER header before
passing the request into the application.

The PEER application can read the user information from the REMOTE_USER
and create a user session for that user. It will create the user in
the PEER database if it is not already created.

In this section we will cover how to setup this mechanism in PEER using
a simple authentication mechanism with the Apache web server. A
htpasswd type file will be use to store user credentials and Auth Basic
will be used to challenge the user for entering those credentials. Please
note that this is just an example and any authentication method supported
by Apache or any other web server will just work the same way.

Web server setup
~~~~~~~~~~~~~~~~

As said in the previous parragraph a htpasswd file will be use to store
the users credentials. So it need to be created:

.. code-block:: bash

  $ htpasswd -c /tmp/passwords.htpasswd lgs@yaco.es
  New password: 
  Re-type new password: 
  Adding password for user lgs@yaco.es

As you can see, emails are used as identifiers for PEER users.

.. note::

  Make sure the passwords.htpasswd file is readable for the user
  running the web server.

Then the Apache web server needs to be configured to handle the
authentication. Go to the virtual host section where the PEER
application is being served and add this code:

.. code-block:: bash

  <Location /remote-user-login>
      AuthType Basic
      AuthName "PEER realm"
      AuthUserFile /tmp/passwords.htpasswd
      Require valid-user
  </Location>

Note that in the AuthUserFile option you need to put the full path
for the file you created in the previous step.

PEER setup
~~~~~~~~~~

Once the web server is configured to send the authenticated user
in the REMOTE_USER request header we need to enable that in PEER.

There are three settings you need to change in the *local_settings.py*
file. First, a middleware to process the header need to be added to
the MIDDLEWARE_CLASSES option:

.. code-block:: python

  MIDDLEWARE_CLASSES = (
      'django.middleware.common.CommonMiddleware',
      'django.contrib.sessions.middleware.SessionMiddleware',
      'django.middleware.csrf.CsrfViewMiddleware',
      'django.contrib.auth.middleware.AuthenticationMiddleware',
      'django.contrib.auth.middleware.RemoteUserMiddleware',  # This is the addition
      'django.contrib.messages.middleware.MessageMiddleware',
  )

Then, a new authentication backend need to be added:

.. code-block:: python

  AUTHENTICATION_BACKENDS = (
      'django.contrib.auth.backends.RemoteUserBackend',
  )

Finally, a PEER specific option needs to be enabled to show
this authentication option in the login page:

.. code-block:: python

  REMOTE_USER_ENABLED = True
