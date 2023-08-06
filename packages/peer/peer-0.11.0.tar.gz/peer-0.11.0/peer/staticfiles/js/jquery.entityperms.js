(function( $ ){

    $.fn.delegates = {};  // namespace

    $.fn.delegates.load_delegates = function(list_delegates_url) {
        $.get(list_delegates_url, function (html) {
                $('#delegates-list').html(html);
                $('form.change-owner-form').submit($.fn.delegates.change_owner);
            }
        );
    };

    $.fn.delegates.select_first_user = function(search_url, add_delegate_url_template) {
        var q = $('input#q').val();
        $.getJSON(search_url + '?term='+q,
            function (resp) {
                for (i in resp) {
                    if (resp[i].value == q) {
                        $.fn.delegates.add_selected_delegate(add_delegate_url_template);
                        $('button#add-delegate').button("disable");
                        return;
                    }
                }
                $('input#q').val(resp[0].value);
                $('#q').autocomplete("close");
                $('button#add-delegate').button("enable");
            }
        );
        return false;
    };

    $.fn.delegates.remove_delegate = function () {
        var url = $(this).attr('id');
        $.get(url, function (html) {
            $('div#delegates-list').html(html);
            $('form.change-owner-form').submit($.fn.delegates.change_owner);
        });
        return false;
    };

    $.fn.delegates.add_selected_delegate = function (add_delegate_url_template) {
        var entity_id = $('input#entity_id').val();
        var username = $('input#q').val();
        var url = add_delegate_url_template.replace('__user__', username);
        $.get(url, function (html) {
            if (html == 'delegate') {
                $.fn.delegates.team_perm_message(username+' can already edit this entity');
            } else if (html == 'owner') {
                $.fn.delegates.team_perm_message(username+' is the owner this entity');
            } else {
                $('div#delegates-list').html(html);
                $('button#add-delegate').button("disable");
                $('form.change-owner-form').submit($.fn.delegates.change_owner);
            }
        });
        return false;
    };

    $.fn.delegates.enable_add_delegate = function () {
        $('button#add-delegate').button("enable");
    };

    $.fn.delegates.disable_add_delegate = function (event) {
        if (event.keyCode != 13) {
            $('button#add-delegate').button("disable");
        }
    };

    $.fn.delegates.change_owner = function () {
        if (confirm('Only the owner can edit the team permissions of an entity,\n'+
                   'and there can be only one owner for each entity.\n'+
                   'Therefore, you will not be able to undo this action.\n\n'+
                   'Do you confirm that you want to hand over the ownership of this entity? ')) {
            return true;
        } else {
            return false;
        }
    };

    $.fn.delegates.team_perm_message = function (msg) {
        $('ul#messages').html('<li>'+msg+'</li>')
                        .fadeIn()
                        .delay(3000)
                        .fadeOut();
    }

})( jQuery );
