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

import os

from django import forms
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe


HAS_SOUTH = True
try:
    from south.modelsinspector import add_introspection_rules
except ImportError:
    HAS_SOUTH = False


class SafeCharField(models.CharField):
    """This field make sure fields with just spaces won't validate"""

    def to_python(self, value):
        if value is not None:
            value = value.strip()
        return super(SafeCharField, self).to_python(value)

if HAS_SOUTH:
    add_introspection_rules([
        (
            [SafeCharField],
            [],
            {},
        ),
    ], ["^peer\.customfields\.SafeCharField"])


def readfile(filename):
    if os.path.exists(filename):
        return open(filename, 'r').read()


def readtou(tou):
    filename = getattr(settings, tou, None)
    if filename is not None:
        return readfile(filename)



class TermsOfUseWidget(forms.CheckboxInput):

    class Media:
        css = {
            'all': ('css/terms-of-use.css', ),
            }
        js = ('js/terms-of-use.js', )

    def __init__(self, legal_text=None, *args, **kwargs):
        self.legal_text = legal_text
        super(TermsOfUseWidget, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None):
        attrs = attrs or {}
        attrs['class'] = 'legalInput'
        value = super(TermsOfUseWidget, self).render(name, value, attrs)
        if self.legal_text:
            value = mark_safe(u'%s<textarea class="legalTerms">%s</textarea>' % (
                    value, self.legal_text))

        return value


TOU_ERROR_MESSAGES = {
    'required': _('You must accept the terms of use'),
}


class TermsOfUseField(forms.BooleanField):

    widget = TermsOfUseWidget

    def __init__(self, legal_text=None, required=True,
                 label=_('I have read and accept the terms of use'),
                 error_messages=TOU_ERROR_MESSAGES,
                 *args, **kwargs):
        super(TermsOfUseField, self).__init__(required=required, label=label,
                                              error_messages=error_messages,
                                              *args, **kwargs)
        self.widget.legal_text = legal_text
