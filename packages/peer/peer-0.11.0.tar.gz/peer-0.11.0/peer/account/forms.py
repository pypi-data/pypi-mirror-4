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


from django import forms
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User

from captcha.fields import ReCaptchaField
from registration.forms import RegistrationForm

from peer.customfields import TermsOfUseField, readtou


class RegistrationFormCaptchaTOU(RegistrationForm):

    captcha = ReCaptchaField(attrs={'theme': 'white'})

    tou = TermsOfUseField(readtou('USER_REGISTER_TERMS_OF_USE'))

    def __init__ (self, *args, **kwargs):
        super(RegistrationFormCaptchaTOU, self).__init__(*args, **kwargs)
        username_field = self.fields['username']
        username_field.help_text = _(
            u"This will be the name to login into PEER.")
        username_field.label = _(u"Username")

        email_field = self.fields['email']
        email_field.help_text = _(
            u"This email address will be used for account activation and "
            u"password recovery. It won't be displayed publicly."
            )
        email_field.label = _(u"Email")

        self.fields['password1'].label = _(u"Password")
        self.fields['password2'].label = _(u"Password (again)")

class PersonalInformationForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


class FriendInvitationForm(forms.Form):

    destinatary = forms.EmailField('destinatary',
                    required=True,
                label=_(u'Destinatary'),
            help_text=_(u'Email address to send the invitation to'))

    body_text = forms.CharField('body_text',
                label=_(u'Body text'),
            help_text=_(u'Text to be sent as the body of the email'),
        widget=forms.Textarea())
