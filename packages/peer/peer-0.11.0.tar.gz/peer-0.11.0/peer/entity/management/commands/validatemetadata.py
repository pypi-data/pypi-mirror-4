# Copyright 2013 Terena. All rights reserved.

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


from django.core.management.base import BaseCommand, CommandError

from peer.entity.models import Entity
from peer.entity.validation import validate


class Command(BaseCommand):
    args = 'entity_id metadata_file'
    help = 'Validates a metadata file agains an entity'

    def handle(self, *args, **options):
        if len(args) != 2:
            raise CommandError('This command takes exactly 2 arguments')

        entity_id, metadata_file = args

        # get the entity
        try:
            entity = Entity.objects.get(id=int(entity_id))
        except ValueError:
            raise CommandError('The entity_id argument must be an integer')
        except Entity.DoesNotExist:
            raise CommandError('There is no entity with entity_id=%s' % entity_id)

        # load the file
        doc = open(metadata_file, 'r').read()

        # validate the metadata
        errors = validate(entity, doc)
        if errors:
            print('There were errors while validating the entity %s:' % entity)
            for error in errors:
                print(error)
