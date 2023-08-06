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

"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import urllib2

from django.test import TestCase

import fudge

from peer.domain.validation import validate_ownership, generate_validation_key


class ValidationTest(TestCase):

    @fudge.patch('urllib2.urlopen')
    def test_validate_ownership(self, urlopen):
        data = None
        timeout = 10
        url = 'http://www.example.com/valid_key'
        (urlopen.expects_call()
                .with_args(url, data, timeout)
                .returns(
                    (fudge.Fake('addinfourl')
                          .expects('getcode')
                          .returns(
                              ( 200 )
                              ))
                 ))
        self.assertEquals(True, validate_ownership(url))

        url = 'http://www.invalid-domain.com/garbage'
        (urlopen.expects_call()
                 .with_args(url, data, timeout)
                 .raises(urllib2.URLError()))

        self.assertEquals(False, validate_ownership(url))

        url = 'http://www.example.com/non_valid_key'
        (urlopen.expects_call()
                 .with_args(url, data, timeout)
                 .raises(urllib2.HTTPError()))

        self.assertEquals(False, validate_ownership(url))

    @fudge.patch('hashlib.sha256')
    def test_generate_validation_key(self, fake_sha256):
        (fake_sha256.expects_call()
                    .returns_fake()
                    .provides('update')
                    .times_called(2)  # initial and datetime
                    .provides('hexdigest')
                    .calls(lambda: 'ValidationKey'))
        self.assertEquals('ValidationKey',
                          generate_validation_key('www.example.com'))

        (fake_sha256.expects_call()
                    .returns_fake()
                    .provides('update')
                    .times_called(3)  # initial, datetime and owner
                    .provides('hexdigest')
                    .calls(lambda: 'ValidationKeyWithOwnerInfo'))
        self.assertEquals('ValidationKeyWithOwnerInfo',
                          generate_validation_key('www.example.com', 'owner'))
