var container = $('#zen-container');
var containerMargin = 50;
var containerHeight;
var formDiv = container.find('#zen-mode');
var previewDiv = container.find('#zen-preview');
var textarea = container.find('textarea');
var buttons = previewDiv.find('.button-group');

var generateContent = function() {
    var data = formDiv.find('form').serialize();

    $.ajax({
        url: formDiv.find('form').data('preview-url'),
        data: data,
        type: 'POST',
        success: function(response) {
            previewDiv.find('.cover-image').html('<img src="' + response.image_url + '" />');
            previewDiv.find('.title.space').html(response.title);
            previewDiv.find('.content.space').html(response.content);
        }
    });
};

var resizeContent = function() {
    containerHeight = $(window).height() - containerMargin * 2;
    previewDiv.find('#zen-preview-content').height(containerHeight - previewDiv.find('.button-group').height());
    textarea.height(containerHeight);
};

// set container margin
container.css('padding', containerMargin + 'px');

// connect signals
$(window).on('load resize', function() {
    resizeContent();
});

$(window).on('load', function() {
    generateContent();
});

textarea.trigger('focus');
textarea.on('keyup', function(e) {
    if (e.keyCode == 13) {
        generateContent();
    }
});

buttons.find('.zen-button-save').on('click', function() {
    formDiv.find('form').submit();
});

var alerts = $('.alert');
if (alerts.length) {
    setTimeout(function() {
        alerts.fadeOut();
    }, 3000);
}
