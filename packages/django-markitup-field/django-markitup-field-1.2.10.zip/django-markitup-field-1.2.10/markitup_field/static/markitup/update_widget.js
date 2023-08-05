
//var STATIC_URL = '/static/';
//var MARKITUP_PREVIEW_URL = '/markitup/preview/';

var DICE_MARKUP_SELECTOR = ".dice_markup_editor";
var MARKUP_FORMAT_POSTFIX = '_markup_format';

$(document).ready(function () {
    setup_markitup_editor();
    bind_on_format_change();
});

function bind_on_format_change() {
    var markup_format_selector = 'select[id$=' + MARKUP_FORMAT_POSTFIX + ']';
    $(markup_format_selector).change(setup_markitup_editor);
}

function setup_markitup_editor() {
    var markup_textareas = $(DICE_MARKUP_SELECTOR);

    markup_textareas.each(function() {
        var markup_textarea = $(this);

        if (markup_textarea.hasClass("markItUpEditor")) {
            markup_textarea.markItUpRemove();
        }

        var markup_format = get_format_from_markup_id(this.id);

        if (markup_format === 'text' || markup_format === 'html') {
            markup_format = 'default';
        }
        $.getScript(STATIC_URL + 'markitup/sets/' + markup_format + '/set.js', function() {
//        $.getScript('/static/markitup/sets/' + markup_format + '/set.js', function() {
            mySettings["previewParserPath"] = MARKITUP_PREVIEW_URL;
            markup_textarea.markItUp(mySettings);
            markup_textarea.parent().parent().parent().toggleClass(markup_format);
        });
    });
}

function get_format_from_markup_id(markup_select_id) {
    var markup_format_selector = '#' + markup_select_id + MARKUP_FORMAT_POSTFIX;
    var markup_format = $(markup_format_selector).val();
    return markup_format;
}

// added
// ';markup_format=' + get_format_from_markup_id($$.attr('id')),
// to jquery.markitup.js
//
//function renderPreview() {
//    var phtml;
//    if (options.previewParserPath !== '') {
//        $.ajax( {
//            type: 'POST',
//            url: options.previewParserPath,
////						data: options.previewParserVar+'='+encodeURIComponent($$.val()),
//            data: options.previewParserVar+'='+encodeURIComponent($$.val()) +
//                ';markup_format=' + get_format_from_markup_id($$.attr('id')),
//            success: function(data) {
//                writeInPreview( localize(data, 1) );
//            }
//        } );
//    } else {
//        if (!template) {
//            alert('ajax not template');
//            $.ajax( {
//                url: options.previewTemplatePath,
//                success: function(data) {
//                    writeInPreview( localize(data, 1).replace(/<!-- content -->/g, $$.val()) );
//                }
//            } );
//        }
//    }
//    return false;
//}
