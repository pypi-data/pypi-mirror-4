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

from django.conf.urls.defaults import patterns, url

from peer.entity.feeds import EntitiesFeed, ChangesFeed

urlpatterns = patterns(
    'peer.entity.views',
    # Global views
    url(r'^$', 'entities_list', name='entities_list'),
    url(r'^rss$', EntitiesFeed(), name='entities_feed'),
    url(r'^add$', 'entity_add', name='entity_add'),

    # Search view
    url(r'^search$', 'search.search_entities', name='search_entities'),

    # Group Views
    url(r'^group/add$',
        'group.entity_group_add', name='entity_group_add'),
    url(r'^group/(?P<entity_group_id>\d+)$',
        'group.entity_group_view', name='entity_group_view'),
    url(r'^group/(?P<entity_group_id>\d+)/edit$',
        'group.entity_group_edit', name='entity_group_edit'),
    url(r'^group/(?P<entity_group_id>\d+)/remove$',
        'group.entity_group_remove', name='entity_group_remove'),

    # Entity basic views
    url(r'^(?P<entity_id>\d+)$', 'entity_view',
        name='entity_view'),
    url(r'^(?P<entity_id>\d+)/remove/$', 'entity_remove',
        name='entity_remove'),
    url(r'^(?P<domain_name>\w+)/add$', 'entity_add_with_domain',
        name='entity_add_with_domain'),

    # Metadata views
    url(r'^(?P<entity_id>\d+)/edit_metadata/$',
        'metadata.edit_metadata', name='edit_metadata'),
    url(r'^(?P<entity_id>\d+)/text_edit_metadata/$',
        'metadata.text_edit_metadata', name='text_edit_metadata'),
    url(r'^(?P<entity_id>\d+)/file_edit_metadata/$',
        'metadata.file_edit_metadata', name='file_edit_metadata'),
    url(r'^(?P<entity_id>\d+)/remote_edit_metadata/$',
        'metadata.remote_edit_metadata', name='remote_edit_metadata'),

    # Team views
    url(r'^(?P<entity_id>\d+)/sharing/$',
        'teams.sharing', name='sharing'),
    url(r'^(?P<entity_id>\d+)/list_delegates/$',
        'teams.list_delegates', name='list_delegates'),
    url(r'^(?P<entity_id>\d+)/make_owner/$',
        'teams.make_owner', name='make_owner'),
    url(r'^(?P<entity_id>\d+)/remove_delegate/(?P<user_id>\d+)$',
        'teams.remove_delegate', name='remove_delegate'),
    url(r'^(?P<entity_id>\d+)/add_delegate/(?P<username>.+)$',
        'teams.add_delegate', name='add_delegate'),


    # Metarefresh views
    url(r'^(?P<entity_id>\d+)/edit_metarefresh/$',
        'metadata_utils.metarefresh_edit', name='metarefresh_edit'),

    # Monitor endpoint views
    url(r'^(?P<entity_id>\d+)/monitoring_prefs/$',
        'metadata_utils.monitoring_prefs', name='monitoring_prefs'),

    # Metadata revision views
    url(r'^(?P<entity_id>\d+)/get_diff/(?P<r1>\w+)/(?P<r2>\w+)$',
        'revisions.get_diff', name='get_diff'),
    url(r'^(?P<entity_id>\d+)/get_revision/(?P<rev>\w+)$',
        'revisions.get_revision', name='get_revision'),
    url(r'^(?P<entity_id>\d+)/latest_metadata/$',
        'revisions.get_latest_metadata', name='get_latest_metadata'),

    # CSS with highlight colors
    url(r'^pygments.css$', 'revisions.get_pygments_css',
        name='get_pygments_css'),

    # Entity feed
    url(r'^(?P<entity_id>\d+)/rss$', ChangesFeed(), name='changes_feed'),
)
