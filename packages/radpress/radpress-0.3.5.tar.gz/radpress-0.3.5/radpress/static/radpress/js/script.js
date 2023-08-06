/* Dear contributor, this code snippet is required to resize pre tag for
 * article div width. If you have a better idea about using horizontal
 * scrolling in pre, please fork radpress repository from github, and send me
 * pull request with your changes. thanks.
 */

// place any jQuery/helper plugins in here, instead of separate, slower script files.
var getParams = function() {
    var params = window.location.href.split('?')[1];
    if (typeof(params) === 'undefined') {
        return {};
    }

    params = params.split('&');
    var paramsObj = {};
    var item;

    $.each(params, function(key, value) {
        item = value.split('=');
        paramsObj[item[0]] = item[1];
    });

    return paramsObj;
};

var getParam = function(key) {
    var value;
    try {
        value = window.RADPESS_PARAMS[key];
        value = decodeURIComponent(value).replace(/\+/g, ' ');
    } catch(e) {
        value = null;
    }

    return value;
};

// Global Variables
window.RADPESS_PARAMS = getParams();

// Highlight table fixings
var postContentDiv = $('.post-content');
var highlighttable = $('td.code pre');

if (highlighttable.length) {
    var preWidth;
    var spaces = parseInt(postContentDiv.css('padding-left').split('px')[0])
            + parseInt(postContentDiv.css('padding-right').split('px')[0])
            + $('td.linenos').width()
            - $('td.code pre').css('padding-left').split('px')[0] / 2;

    $(window).on('load resize', function() {
        preWidth = postContentDiv.width() - spaces;
        $('td.code pre').css('width', preWidth);
    });
}

var searchForm = $('.search-form');
if (searchForm.length) {
    var qName = 'q';
    var q = getParam(qName);

    if (q != '' && q != 'undefined') {
        searchForm.find('input[name="' + qName + '"]').val(q);
    }
}


var shareUrls = $('.meta-info .share a');
if (shareUrls.length) {
    var url;

    $.each(shareUrls, function(key, url) {
        url = $(this).attr('href') + window.location.href + $(this).data('url').replace(/^\/|\/$/g, '') + '/';
        $(this).attr('href', url);
    });

    shareUrls.on('click', function() {
        window.open(
            $(this).attr('href'),
            $(this).text(),
            'width=450,height=300,left=' + (screen.availWidth / 2 - 375) + ',top=' + (screen.availHeight / 2 - 150) + '');
        return false;
    });
}
