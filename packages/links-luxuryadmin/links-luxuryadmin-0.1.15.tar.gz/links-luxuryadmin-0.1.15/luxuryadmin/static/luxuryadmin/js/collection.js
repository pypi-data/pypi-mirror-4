var saveProduct = function(button, data, url, callback) {
    button.attr('disabled', 'disabled');
    $.post(url, data, function(response) {
        if(response.success) {
            callback(response, function() {
                window.location.reload();
            });
        } else {
            alert('Saving product failed!');
        }

        button.removeAttr('disabled');
    }, 'json');
}

var updatePhotos = function(url, product_pk, rows, callback) {
    var images = []
    var selected = $("input[@name=image]:checked", rows.parent()).val()
    for (var i = 0, r; r = rows[i]; i++) {
        filename = $('input[type=radio]' , r).val()
        image = {
            filename: filename
        };
        if (selected == filename) {
            image['selected'] = true;
        } else {
            image['selected'] = false;
        }
        images.push(image);
    }
    data = {
        pk: product_pk,
        images: array2json(images)
    }
    $.post(url, data, function(response) {
        callback(response);
    }, 'json');
}

var showInfoRow = function(t) {
    row = t.closest('tr').next();
    t.removeClass('editInfoButton');
    t.addClass('editInfoButtonSelected');
    row.show();
}
var hideInfoRow = function(t) {
    row = t.closest('tr').next();
    t = $('.editInfoButtonSelected', t.closest('tr'));
    t.removeClass('editInfoButtonSelected');
    t.addClass('editInfoButton');
    row.hide();
}

var showImageRow = function(t) {
    row = t.closest('tr').next().next();
    t.removeClass('editImagesButton');
    t.addClass('editImagesButtonSelected');
    row.show();
}

var hideImageRow = function(t) {
    row = t.closest('tr').next().next();
    t = $('.editImagesButtonSelected', t.closest('tr'));
    t.removeClass('editImagesButtonSelected');
    t.addClass('editImagesButton');
    row.hide();
}

var getProducts = function(table, searchField) {
    var src = table.attr('src');
    var q = searchField.val();
    var body = table.find('tbody');
    $.getJSON(src, {
        q: q
    }, function(data) {
        body.empty();
        $.each(data, function(k, product) {
            body.append(ich.productRow(product));
        });
    })
}


$(function() {
    /**
     * File uploads are pretty horrible.
     */
    var table = $('table.products');
    var searchField = $('#tableSearch');
    getProducts(table, searchField);
    searchField.on('keyup', function(event) {
        getProducts(table, searchField);
    })
    $('input[type=file]').on('change', function(event) {
        document.body.style.cursor = "wait";
        var form_data = new FormData();
        var xhr = new XMLHttpRequest();
        var t = $(this);
        var rows = $('table.images tbody');
        var files = event.target.files;
        var uploaded = function(response) {
            var response = $.parseJSON(response);
            for (var i = 0, f; f = response['images'][i]; i++) {
                var row = ich.productImageRow(f);
                rows.append(row);
                document.body.style.cursor = "default";
            }

        };
        for (var i = 0, f; f = files[i]; i++) {
            form_data.append(f.name, f);
        }
        xhr.open('POST', t.attr('url'), true);
        xhr.setRequestHeader("X-CSRFToken", $.cookie('csrftoken'));
        xhr.onreadystatechange = function() {
            if (xhr.readyState === 4 && xhr.status === 200) {
                uploaded(xhr.response);
            }
        };
        xhr.send(form_data);
        form_data = new FormData()
        event.preventDefault();
    })

    $('#saveNewProductButton').on('click', function(event) {
        event.preventDefault();
        var form = $('#newProductInfoForm');
        var data = form.toObject();
        var url = form.attr('action');
        saveProduct($(this), data, url, function(response, callback) {
            var container = $('#newProductImagesContainer');
            var url = container.attr('url');
            var product_pk = response.pk;
            updatePhotos(url, product_pk, $('.productImageRow', container), callback);
        });
    });

    $('.infoUpdateButton').on('click', function(event) {
        event.preventDefault();
        var form = $(this).closest('form');
        var data = form.toObject();
        var url = form.attr('action');
        saveProduct($(this), data, url, function(response, callback) {
            window.location.reload();
        });
    });

    $('table.products tbody').on('change', 'tr input, tr select',
        function(event) {
            event.preventDefault();
            var t = $(this);
            var row = t.closest('tr');
            var cat = $('select[name=category]');
            var data = {
                category: $('select[name=category] option:selected', row).val(),
                featured: $('input[name=featured]:checked', row).val(),
                sold: $('input[name=sold]:checked', row).val(),
                live: $('input[name=live]:checked', row).val()
            };
            saveProduct(t, data, row.attr('action'), function(response, callback) {
                window.location.reload();
            });
        }
    );

    $('.imageUpdateButton').on('click', function(event) {
        event.preventDefault();
        var t = $(this);
        var row = t.closest('tr');
        var rows = $('.productImageRow', row.closest('table').find('tbody'));
        var url = row.attr('url');
        var product_pk = row.attr('product_pk');
        updatePhotos(url, product_pk, rows, function() {
            window.location.reload()
        });
    });

    $('body').on('click', 'tr.productImageRow a.deleteButton',
        function(event) {
            event.preventDefault();
            row = $(this).closest('.productImageRow');
            row.fadeOut(function() {
                row.remove();
            });
    })

    var limit = 400;
    $('.limited').on('keyup', function() {
        var t = $(this);
        var count = $('span.count', t.parent());
        var length = $(this).val().length;
        count.text(length);
        if(length >= limit) {
            t.val(t.val().substring(0, limit));
        }
    })

    $('tr.editInfoRow, tr.editImagesRow').hide();

    // Open edit row.
    $('body').on('click', 'a.editInfoButton', function(event) {
        event.preventDefault();
        showInfoRow($(this));
        hideImageRow($(this));
    });

    // Close edit row.
    $('body').on('click', 'a.editInfoButtonSelected', function(event) {
        event.preventDefault();
        hideInfoRow($(this));
    });

    // Open image row.
    $('body').on('click', 'a.editImagesButton', function(event) {
        event.preventDefault();
        showImageRow($(this));
        hideInfoRow($(this));

    });

    // Close image row.
    $('body').on('click', 'a.editImagesButtonSelected', function(event) {
        event.preventDefault();
        hideImageRow($(this));
    });

    var date_opts = {
        dateFormat: "dd/mm/yy"
    }
    $('.datepicker').datepicker(date_opts);
    if ($('#id_sold:checked').length == 0) {
        $('#id_sold_date').hide();
    }
    $('body').on('change', '#id_sold', function() {
        $this = $(this);
        if ($('#id_sold:checked').length > 0) {
            $('#id_sold_date').show();
            var val = $('#id_sold_date').val()
            if (val == '' || !val) {
                $('#id_sold_date').val(TODAY);
            }
        }
        else {
            $('#id_sold_date').hide();
            $('#id_sold_date').val('');
        }
    })
});

