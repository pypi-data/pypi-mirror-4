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

from django.db.models import Count
from django.utils.translation import ugettext_lazy as _

from peer.domain.models import Domain

class Filter(object):

    label = None

    def __init__(self, current_value):
        self.current_value = current_value

    def is_empty(self):
        return self.current_value is None

    def get_options(self):
        raise NotImplemented('Abstract method')

    def filter(self, entity):
        if self.current_value is None:
            return True
        else:
            return self._real_filter(entity)

    def _real_filter(self, entities):
        raise NotImplemented('Abstract method')

MAX_DOMAINS = 5


class DomainFilter(Filter):

    name = 'domain'
    label = _(u'By domain')

    def get_options(self):
        # top 5 domains with more entities
        for domain in Domain.objects.annotate(
            num_entities=Count('entity')).exclude(
            num_entities=0).order_by('-num_entities')[:MAX_DOMAINS]:
            yield {
                'value': domain.name,
                'count': domain.num_entities,
                'is_current': self.current_value == domain.name,
                }

    def _real_filter(self, entity):
        return entity.domain.name == self.current_value


def get_filters(GET):
    return [F(GET.get(F.name, None)) for F in [DomainFilter]]


def filter_entities(filters, entities):
    return [entity for entity in entities
            if len(filter(lambda f: f.filter(entity), filters)) > 0]
