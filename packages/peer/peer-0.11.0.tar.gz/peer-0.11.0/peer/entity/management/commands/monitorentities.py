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

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.core.management import BaseCommand
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _

from peer.entity.models import Entity
from peer.entity.utils import fetch_resource, FetchError


def check_endpoints(entity, verbosity):
    errors = []

    if verbosity > 1:
        print u'Monitoring entity %s' % entity

    if entity.has_metadata():
        for endpoint in entity.endpoints:
            location = endpoint['Location']

            if verbosity > 1:
                print u'\tChecking availability of %s' % location

            try:
                fetch_resource(location, decode=False)
            except FetchError, e:
                errors.append({'endpoint': location, 'exception': e})

    else:
        if verbosity > 1:
            print u'\tNo metadata yet' % entity

    return errors


def mail_problems(user, problems):
    context = {'problems': problems, 'site': Site.objects.get_current()}
    message = render_to_string('entity/endpoint_failures_alert.txt', context)
    subject = _("Some entity's endpoints are down")
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email],
              fail_silently=False)


class Command(BaseCommand):

    help = 'Send alerts for endpoints that are down and have subscribers'

    def handle(self, *args, **options):

        verbosity = int(options.get('verbosity'))

        problems = {}

        # Fetch the problems
        for entity in Entity.objects.filter(subscribers__isnull=False):
            errors = check_endpoints(entity, verbosity)
            if errors:
                for subscriber in entity.subscribers.all():
                    user_problems = problems.setdefault(subscriber.id, [])
                    user_problems.append({'entity': entity, 'errors': errors})

        # Mail them
        for user_id, user_problems in problems.items():
            mail_problems(User.objects.get(id=user_id), user_problems)
