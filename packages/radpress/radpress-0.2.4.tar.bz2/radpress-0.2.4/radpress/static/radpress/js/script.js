/* Dear contributor, this code snippet is required to resize pre tag for
 * article div width. If you have a better idea about using horizontal
 * scrolling in pre, please fork radpress repository from github, and send me
 * pull request with your changes. thanks.
 */

// Global Variables
window.RADPESS_PARAMS = getParams();

// Highlight table fixings
var articleDiv = $('.article');
var articleContentDiv = $('.article-content');
var highlighttable = $('td.code pre');

if (highlighttable.length) {
    var preWidth;
    var spaces = parseInt(articleDiv.css('padding-left').split('px')[0])
               + $('td.linenos').width();

    $(window).on('load resize', function() {
        preWidth = articleContentDiv.width() - spaces;
        $('td.code pre').css('width', preWidth);
    });
}

var searchForm = $('.search-form');
if (searchForm.length) {
    var qName = 'q';
    var q = getParam(qName);

    if (typeof(q) !== 'undefined') {
        searchForm.find('input[name="' + qName + '"]').val(q);
    }
}
