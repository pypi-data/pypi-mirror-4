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
from subprocess import Popen, PIPE
import logging

logger = logging.getLogger('peer.nagios')


def send_nagios_notification(server, action):
    nagios_msg = ('%(server)s\t%(service)s\t%(level)s\t%(action)s\n' %
                    {'server': server,
                     'service': getattr(settings, 'NSCA_SERVICE', 'peer'),
                     'level': getattr(settings, 'NSCA_NOTIFICATION_LEVEL', 3),
                     'action': action,
                    })
    try:
        p = Popen(settings.NSCA_COMMAND, stdin=PIPE, stderr=PIPE, stdout=PIPE,
                  shell=True)
        p.stdin.write(nagios_msg)
        p.stdin.close()
    except OSError:
        logger.error("OSError with settings.NSCA_COMMAND, maybe it doesn't exist")
    if p.wait() != 0:
        logger.error("settings.NSCA_COMMAND doesn't run correctly\n\n\n%s"
                     % (p.stderr.read()))
