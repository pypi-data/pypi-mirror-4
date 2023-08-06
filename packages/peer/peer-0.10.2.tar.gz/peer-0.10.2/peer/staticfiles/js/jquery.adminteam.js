(function( $ ){

    $.fn.superusers = {};  // namespace

    $.fn.superusers.load_superusers = function(list_superusers_url) {
        $.get(list_superusers_url, function (html) {
                $('#superusers-list').html(html);
            }
        );
    };

    $.fn.superusers.select_first_user = function(search_url, add_superuser_url_template) {
        var q = $('input#q').val();
        $.getJSON(search_url + '?term='+q,
            function (resp) {
                for (i in resp) {
                    if (resp[i].value == q) {
                        $.fn.superusers.add_selected_superuser(add_superuser_url_template);
                        $('button#add-superuser').button("disable");
                        return;
                    }
                }
                $('input#q').val(resp[0].value);
                $('#q').autocomplete("close");
                $('button#add-superuser').button("enable");
            }
        );
        return false;
    };

    $.fn.superusers.remove_superuser = function () {
        var url = $(this).attr('id');
        $.get(url, function (html) {
            if (html == 'notsuperuser') {
                $.fn.superusers.message('The selected user was not a member of the admin team.');
            }
            else if (html == 'adminuser') {
                $.fn.superusers.message('The admin user cannot be removed from the admin team.');
            }
            else if (html == 'delegateddomains') {
                $.fn.superusers.message('This user has domains shared with other users.');
            }
            else if (html == 'notdelegate') {
                $.fn.superusers.message("The selected user was not a member of this domain's team.");
            }
            else if (html == 'hasentities') {
                $.fn.superusers.message("The selected user has some entities using this domain.");
            }
            else {
                $('div#superusers-list').html(html);
            }
        });
        return false;
    };

    $.fn.superusers.add_selected_superuser = function (add_superuser_url_template) {
        var username = $('input#q').val();
        var url = add_superuser_url_template.replace('__user__', username);
        $.get(url, function (html) {
            if (html == 'superuser') {
                $.fn.superusers.message(username+' is already in the admin team');
            } else if (html == 'delegate'){
                $.fn.superusers.message(username+' can already use this domain');
            } else {
                $('div#superusers-list').html(html);
                $('button#add-superuser').button("disable");
            }
        });
        return false;
    };

    $.fn.superusers.enable_add_superuser = function () {
        $('button#add-superuser').button("enable");
    };

    $.fn.superusers.disable_add_superuser = function (event) {
        if (event.keyCode == 9) {
            //$('button#add-superuser').focus();
            //return false;
        }
        else if (event.keyCode != 13) {
            $('button#add-superuser').button("disable");
        }
    };

    $.fn.superusers.message = function (msg) {
        $('ul#messages').html('<li>'+msg+'</li>')
                        .fadeIn()
                        .delay(3000)
                        .fadeOut();
    };

})( jQuery );
