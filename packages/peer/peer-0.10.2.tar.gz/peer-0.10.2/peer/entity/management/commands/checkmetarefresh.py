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

from django.core.management.base import BaseCommand

from peer.entity.models import Entity


DELTA = {'D': datetime.timedelta(days=1),
         'M': datetime.timedelta(days=30),
         'W': datetime.timedelta(weeks=1),
         }


class Command(BaseCommand):

    help = 'Checks for updates in metadata'

    def handle(self, *args, **options):
        now = datetime.datetime.now()
        for entity in Entity.objects.exclude(metarefresh_frequency='N'):
            delta = DELTA[entity.metarefresh_frequency]
            last_run = entity.metarefresh_last_run
            if now > last_run + delta:
                msg = entity.metarefresh()
                if msg.startswith('Error: '):
                    entity.owner.email_user(
                        u'Error updating PEER metadata',
                        EMAIL_BODY % (entity.id, entity.entityid, msg),
                        )
                print msg


EMAIL_BODY ="""
The following error has been detected while updating the metadata of the
instance with id %s from url %s:

%s
"""

