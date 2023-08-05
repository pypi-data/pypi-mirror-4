
var getCategories = function(table, searchField) {
    var src = table.attr('src');
    var q = searchField.val();
    var body = table.find('tbody');
    $.getJSON(src, {
        q: q
    }, function(data) {
        body.empty();
        $.each(data, function(k, category) {
            var row = ich.categoryRow(category);
            body.append(row);
        });
    })
};


$(function() {
    var table = $('table.categories');
    var searchField = $('#tableSearch');
    getCategories(table, searchField);
    searchField.on('keyup', function(event) {
        getCategories(table, searchField);
    })
})