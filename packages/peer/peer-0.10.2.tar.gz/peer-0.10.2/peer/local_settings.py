import os
import saml2

BASEDIR = os.path.abspath(os.path.dirname(__file__))

ADMINS = (
    ('Lorenzo Gil', 'lgs@yaco.es'),
)

EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025

RECAPTCHA_PUBLIC_KEY = '6LegA8ASAAAAAF9AhuaPUPYb94p3vE4IkHOxfgAi'
RECAPTCHA_PRIVATE_KEY = '6LegA8ASAAAAAAI-nxu0DcCdDCQIzuWCNbKOXPw3'

DEFAULT_FROM_EMAIL = 'no-reply@beta.terena-peer.yaco.es'
SECRET_KEY = 'mc=$+amv4$m5p9dv-l_cko(&qp3@t*6c3!)r1#cxm#qzfapgjy'

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ENTITIES_PER_PAGE = 10

PEER_HOST = 'localhost'
PEER_PORT = '8000'
PEER_BASE_URL = 'http://' + PEER_HOST + ':' + PEER_PORT

SAML_CONFIG2 = {
    # full path to the xmlsec1 binary programm
    'xmlsec_binary': '/usr/bin/xmlsec1',

    # your entity id, usually your subdomain plus the url to the metadata view
    'entityid': PEER_BASE_URL + '/saml2/metadata/',

    # directory with attribute mapping
    'attribute_map_dir': os.path.join(BASEDIR, 'pysaml2', 'attribute-maps'),

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
        'local': [os.path.join(BASEDIR, 'pysaml2', 'remote_metadata.xml')],
        },

    # set to 1 to output debugging information
    'debug': 1,

    # certificate
    'key_file': os.path.join(BASEDIR, '..', 'parts', 'beta.terena-peer.yaco.es.key'),  # private part
    'cert_file': os.path.join(BASEDIR, '..', 'parts', 'beta.terena-peer.yaco.es.crt'),  # public part

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
