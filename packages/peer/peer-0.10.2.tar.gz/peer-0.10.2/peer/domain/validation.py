# Copyright 2011 Terena. All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:

#    1. Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.

#    2. Redistributions in binary form must reproduce the above copyright notice,
#       this list of conditions and the following disclaimer in the documentation
#        and/or other materials provided with the distribution.

# THIS SOFTWARE IS PROVIDED BY TERENA ``AS IS'' AND ANY EXPRESS OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
# EVENT SHALL TERENA OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# The views and conclusions contained in the software and documentation are those
# of the authors and should not be interpreted as representing official policies,
# either expressed or implied, of Terena.

import datetime
import hashlib
import httplib
import urllib2
import dns.resolver
from dns.exception import DNSException

from django.conf import settings
from django.utils.encoding import smart_str

CONNECTION_TIMEOUT = 10


def get_custom_user_agent():
    if hasattr(settings, 'DOP_USER_AGENT'):
        return settings.DOP_USER_AGENT
    else:
        return None


def http_validate_ownership(validation_url, timeout=CONNECTION_TIMEOUT):
    """ True if the validation_url exists and returns a 200 status code.

    False otherwise
    """
    if not validation_url:
        return False

    try:
        request = urllib2.Request(validation_url)
        custom_user_agent = get_custom_user_agent()
        if custom_user_agent:
            request.addheaders = [('User-agent', custom_user_agent)]
        response = urllib2.urlopen(request, None, timeout)
    except (urllib2.URLError, httplib.BadStatusLine):
        return False

    if response.getcode() == 200:
        valid = True
    else:
        valid = False
    response.close()
    return valid


def dns_validate_ownership(domain, validation_record, timeout=CONNECTION_TIMEOUT):
    """ True if validation_record is in any of the DNS TXT records.

    False otherwise
    """
    if not validation_record:
        return False

    resolver = dns.resolver.Resolver()
    resolver.timeout = timeout
    try:
        answers = resolver.query(domain, 'TXT')
    # All DNS exceptions subclass from this one
    except DNSException:
        # Check for TXT in root domain
        segs = domain.split('.')
        if len(segs) > 2:
            root_domain = '.'.join(segs[-2:])
            dns_validate_ownership(root_domain, validation_record)
        return False

    for ans in answers:
        if ans.to_text().strip('\"') == validation_record:
            return True
    else:
        return False


def generate_validation_key(domain_name, domain_owner=None):
    """ Generates a unique validation key """
    m = hashlib.sha256()
    m.update(smart_str(domain_name))

    # add also current datetime and owner for more security
    m.update(datetime.datetime.now().isoformat())
    if domain_owner:
        m.update(domain_owner)

    return m.hexdigest()
