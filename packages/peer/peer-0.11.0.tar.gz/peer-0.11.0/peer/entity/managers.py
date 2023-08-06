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

from lxml import etree

from django.db import models

from peer.entity.utils import NAMESPACES, safe_split


class EntityManager(models.Manager):

    def xpath_filters(self, queries):

        result = []

        if not queries:
            return result

        for entity in self.all():
            if not entity.has_metadata():
                continue

            metree = entity.metadata_etree
            match = True
            for query in queries:
                parts = safe_split(query, u'=', u'[', u']')
                if len(parts) == 2:
                    xpath, text = parts
                else:
                    xpath = parts[0]
                    text = None

                try:
                    elements = metree.xpath(xpath, namespaces=NAMESPACES)
                    if not elements:
                        match = False
                        break
                    elif text is not None:
                        text_match = False
                        for element in elements:
                            if element.text == text:
                                text_match = True
                        if not text_match:
                            match = False
                            break

                except etree.XPathEvalError:
                    match = False
                    break

            if match:
                result.append(entity)

        return result

    def text_filters(self, query):
        result = []

        if not query:
            return result

        for entity in self.all():
            if not entity.has_metadata():
                continue

            metadata = entity.metadata.get_revision()
            if not metadata:
                continue

            if query in metadata:
                result.append(entity)

        return result
