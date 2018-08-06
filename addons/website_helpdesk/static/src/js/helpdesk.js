flectra.define('website_helpdesk.helpdesk', function (require) {
    "use strict";

    var ajax = require('web.ajax');
    var core = require('web.core');
    var session = require('web.session');
    var _t = core._t;
    $(function () {
        $('.issue_type_selection_field').on('change', function (e) {
            session.rpc("/helpdesk-form/issue_description/" + $(e.target)
                .val()).then(function (data) {
                var teamId = $("select[name='description']");
                document.getElementById('description').value = data.description;
            })
        });
    });
    $(function () {
        $('.uploaded_file').on('change', function (e) {
            var files = e.target.files;
            var file_data = {};
            $('.file_data').remove();
            $('.pip').remove();
            for (var i = 0; i < files.length; i++) {
                var file = files[i];
                var is_image = /^image\/.*/.test(file.type);
                file_data.name = file.name;
                file_data.type = file.type;
                if (!is_image) {
                    display_alert(_t(
                        "Invalid file type. Please select image file"));
                    reset_file();
                    return;
                }
                if (file.size / 1024 / 1024 > 25) {
                    display_alert(_t(
                        "File is too big. File size cannot exceed 25MB"));
                    reset_file();
                    return;
                }
                $('.alert-warning').remove();
                var BinaryReader = new FileReader();
                // file read as DataURL
                BinaryReader.readAsDataURL(file);
                BinaryReader.onloadend = function (upload) {
                    var buffer = upload.target.result;
                    buffer = buffer.split(',')[1];
                    var file_name = 'file_data_' + _.uniqueId([2]);
                    $('#file_upload_data').append($('<input class="form-group file_data" name=' + file_name +
                        ' type="hidden" value="' + buffer + '"/>')
                    );
                    $("<span class=\"pip\" name=\"" + file_name + "\" >" +
                        "<img class=\"imageThumb\" src=\"" + upload.target.result + "\"  title=\"" + file.name + "\"/>" +
                        "<br/><span class=\"remove\">Remove image</span>" +
                        "</span>").insertAfter("#upload");
                    $(".remove").click(function () {
                        $(this).parent(".pip").remove();
                        var file_name = $('[name=' + $(this).parent(".pip").attr("name") +']')
                        $('#upload').val("");
                        $(file_name ).remove();
                    });
                };
            }

        });
    });

    function display_alert(message) {
        $('.alert-warning').remove();
        $('<div class="alert alert-warning" role="alert">' + message + '</div>'
        ).insertBefore($('form'));
    }

    function reset_file() {
        $('#upload').val('');
    }

});
