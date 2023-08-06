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

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import send_mail, mail_admins
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string

from peer.entity.models import Entity

DEFAULT_THRESHOLD = datetime.timedelta(days=1)


class Command(BaseCommand):

    help = 'Issues expiration warnings for rotten metadata'

    def handle(self, *args, **options):
        now = datetime.datetime.now()
        threshold = self.get_threshold()
        for entity in Entity.objects.all():
            if not entity.metadata:
                continue

            valid_until = entity.valid_until
            if valid_until is None:
                continue

            if now > valid_until:
                self.alert(entity, valid_until)
            elif (valid_until - now) < threshold:
                self.warn(entity, valid_until)

    def get_threshold(self):
        try:
            return settings.EXPIRATION_WARNING_TIMEDELTA
        except AttributeError:
            return DEFAULT_THRESHOLD

    def get_recipients(self, entity):
        recipients = set()

        if entity.owner and entity.owner.email:
            recipients.add(entity.owner.email)

        for delegate in entity.delegates.all():
            if delegate.email:
                recipients.add(delegate.email)

        return list(recipients)

    def send_email(self, subject, recipients, context):
        if recipients:
            message = render_to_string(
                'entity/expiration_alert_to_owners.txt', context)
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL,
                      list(recipients), fail_silently=False)
        else:
            message = render_to_string(
                'entity/expiration_alert_to_admins.txt', context)
            mail_admins(subject, message, fail_silently=False)

    def alert(self, entity, valid_until):
        subject = 'The metadata for entity %s has expired' % entity.name
        recipients = self.get_recipients(entity)

        template_context = {
            'entity': entity,
            'valid_until': valid_until,
            'is_expired': True,
            'site': Site.objects.get_current(),
            }
        self.send_email(subject, recipients, template_context)

    def warn(self, entity, valid_until):
        subject = 'The metadata for entity %s is about to expire' % entity.name
        recipients = self.get_recipients(entity)

        template_context = {
            'entity': entity,
            'valid_until': valid_until,
            'is_expired': False,
            'site': Site.objects.get_current(),
            }
        self.send_email(subject, recipients, template_context)
