
var getPages = function(table, searchField) {
    var src = table.attr('src');
    var q = searchField.val();
    var body = table.find('tbody');
    $.getJSON(src, {
        q: q
    }, function(data) {
        body.empty();
        $.each(data, function(k, page) {
            var row = ich.pageRow(page);
            body.append(row);
        });
    })
};


$(function() {
    var table = $('table.pages');
    var searchField = $('#tableSearch');
    getPages(table, searchField);
    searchField.on('keyup', function(event) {
        getPages(table, searchField);
    })
})