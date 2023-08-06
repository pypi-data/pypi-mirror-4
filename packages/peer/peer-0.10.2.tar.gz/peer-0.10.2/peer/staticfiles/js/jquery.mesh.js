/*global jQuery: false, Spinner: false */
// Metadata Editor Shell
(function ($) {
    "use strict";

    $.fn.mesh = function (options) {

        var settings = $.extend({
            validatingMsg: 'Validating metadata ...',
            validMetadataMsg: 'The metadata is valid!',
            invalidMetadataMsg: 'The metadata s not valid!',
            submitButtonLabel: 'Submit changes',
            closeButtonLabel: 'Cancel',
            noMessageAlert: 'Please write a commit message',
            noTOUAcceptedAlert: 'You must accept the terms of use'
        }, options),

            counter = 1,

            makeDialog = function ($form, openHandler) {
                var msg_id = 'dialog-' + counter + '-commit-msg',
                    html = [
                        '<div title="Commit dialog">',
                        '<div><h2>' + settings.validatingMsg + '</h2>',
                        '<p class="spinner"></p>',
                        '<div class="requestResults">',
                        '<label for="' + msg_id + '">' +  settings.noMessageAlert + ':</label>',
                        '<input type="text" id="' + msg_id + '" name="' + msg_id + '" style="width: 90%" />',
                        '<p>and review your changes</p>',
                        '<div style="overflow: auto;"></div>',
                        '</div>',
                        '</div>',
                        '</div>'
                    ];

                counter += 1;

                return $(html.join('')).appendTo($form).dialog({
                    autoOpen: false,
                    modal: true,
                    width: 600,
                    height: 400,
                    open: openHandler
                });
            },

            commit_spinner = new Spinner({
                lines: 12,
                length: 7,
                width: 4,
                radius: 10,
                color: '#000',
                speed: 1,
                trail: 60,
                shadow: false
            });

        return this.each(function () {
            var self = this,
                $form = $(self),
                $dialog = null,
                $results = null,
                $diffViewer = null,
                $commitMsgInput = null,
                resizeDiffViewer = null,
                openHandler = null,
                successHandler = null,
                errorHandler = null,
                submitButtonHandler = null,
                closeButtonHandler = null;

            resizeDiffViewer = function () {
                var height = $dialog.height() - $diffViewer.position().top;
                $diffViewer.height(height);
            };

            successHandler = function (data, textStatus, jqXHR) {
                commit_spinner.stop();
                $dialog.find("h2").text(settings.validMetadataMsg);
                $dialog.find("#dialog-commit-msg").val("");
                $diffViewer.html(data);

                $results.find("label,input,p").show();
                $results.show();

                resizeDiffViewer();

                // Show both buttons
                $dialog.dialog("option", "buttons", [{
                    text: settings.submitButtonLabel,
                    click: submitButtonHandler
                }, {
                    text: settings.closeButtonLabel,
                    click: closeButtonHandler
                }]);
            };

            errorHandler = function (jqXHR, textStatus, errorThrown) {
                commit_spinner.stop();
                $dialog.find("h2").text(settings.invalidMetadataMsg);
                $diffViewer.html(jqXHR.responseText);

                $results.find(">label,>input,>p").hide();
                $results.show();

                resizeDiffViewer();

                // Show only cancel button
                $dialog.dialog("option", "buttons", [{
                    text: settings.closeButtonLabel,
                    click: closeButtonHandler
                }]);
            };

            submitButtonHandler = function () {
                var msg = $dialog.find("input[type=text]").val();
                msg = $.trim(msg);
                if (msg === "") {
                    window.alert(settings.noMessageAlert);
                    $("#dialog-commit-msg").focus();
                    return;
                }

                $commitMsgInput.val(msg);
                $form.submit();

                $dialog.dialog('close');
            };

            closeButtonHandler = function () {
                // Move the errors to the main page
                $dialog.find('.errorlist').each(function (index, element) {
                    var field = $(element).attr('id').replace('-errors', '');
                    $form.find('#id_' + field).parent().prepend(element);
                });
                $dialog.find('.ui-state-error').parent().insertAfter("#header");

                $dialog.dialog('close');
            };

            openHandler = function (event, ui) {
                // Hide the messages at the top of the page
                $('.ui-state-error').parent().remove();
                // Hide the errors at each widget
                $('.errorlist').remove();

                $dialog.dialog("option", "buttons", [{
                    text: settings.closeButtonLabel,
                    click: closeButtonHandler
                }]);
                $results.hide();

                $dialog.find("h2").text(settings.validatingMsg);

                commit_spinner.spin($dialog.find(".spinner").get(0));
                // Hack to avoid the spinner mess with the dialog width
                $dialog.find(".spinner > div").width(0);

                // Put an invalid commit message to pass server validation
                $commitMsgInput.val('commit message');

                if ($form.find('input[type=file]').size() > 0) {
                    // Use jquery.form.js to upload files via ajax
                    $form.ajaxSubmit({
                        dataType: 'html',
                        success: successHandler,
                        error: errorHandler
                    });
                } else {
                    $.ajax({
                        url: $form.attr('action'),
                        type: 'POST',
                        data: $form.serialize(),
                        dataType: 'html',
                        success: successHandler,
                        error: errorHandler
                    });
                }
            };

            // Create the dialog
            $dialog = makeDialog($form, openHandler);

            // Prefetch common DOM fragments
            $results = $dialog.find(".requestResults");
            $diffViewer = $results.find('div');

            $commitMsgInput = $form.find('.commitMessage');
            $commitMsgInput.parent().hide();

            // Form submit buttons trigger the dialog
            $form.find("input[type=submit]").click(function (event) {
                event.preventDefault();
                $dialog.dialog('open');
            });
        });

    };

}(jQuery));