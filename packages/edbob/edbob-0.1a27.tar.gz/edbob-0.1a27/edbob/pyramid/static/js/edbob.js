
/************************************************************
 *
 * edbob.js
 *
 * This library contains all of Javascript functionality
 * provided directly by edbob.
 *
 * It also attaches some jQuery event handlers for certain
 * design patterns.
 *
 ************************************************************/


var filters_to_disable = [];


function disable_button(button, text) {
    if (text) {
        $(button).html(text + ", please wait...");
    }
    $(button).attr('disabled', 'disabled');
}


function disable_filter_options() {
    for (var i = 0; i <= filters_to_disable.length; ++i) {
        var filter = filters_to_disable.pop();
        var option = $('#add-filter option[value='+filter+']').attr('disabled', true);
    }
}

/*
 * get_dialog(id, callback)
 *
 * Returns a <DIV> element suitable for use as a jQuery dialog.
 *
 * ``id`` is used to construct a proper ID for the element and allows the
 * dialog to be resused if possible.
 *
 * ``callback``, if specified, should be a callback function for the dialog.
 * This function will be called whenever the dialog has been closed
 * "successfully" (i.e. data submitted) by the user, and should accept a single
 * ``data`` object which is the JSON response returned by the server.
 */

function get_dialog(id, callback) {
    var dialog = $('#'+id+'-dialog');
    if (! dialog.length) {
        dialog = $('<div class="dialog" id="'+id+'-dialog"></div>');
    }
    if (callback) {
        dialog.attr('callback', callback);
    }
    return dialog;
}


/*
 * get_lookup_dialog(id, callback, textcol)
 *
 * TODO: Document this.
 */

function get_lookup_dialog(id, callback, textcol) {
    var dialog = get_dialog('lookup-'+id, callback);
    dialog.addClass('lookup');
    dialog.attr('textcol', textcol || 0);
    return dialog;
}


/*
 * get_uuid(obj)
 *
 * Returns the UUID associated with ``obj``, if any can be found.  The object
 * itself is checked, as well its most immediate <TR> parent.
 */

function get_uuid(obj) {

    obj = $(obj);
    if (obj.attr('uuid')) {
        return obj.attr('uuid');
    }
    var tr = obj.parents('tr:first');
    if (tr.attr('uuid')) {
        return tr.attr('uuid');
    }
    return undefined;
}


/*
 * json_success(data)
 *
 * Returns a boolean indicating whether ``data`` represents a successful
 * response from the server, or not.
 */

function json_success(data) {
    return typeof(data) == 'object' && data.ok == 'success';
}


/*
 * loading(element)
 *
 * Used to indicate that data is being retrieved from the server.  ``element``
 * is typically a <div class="grid"> element, though it can be anything.
 */

function loading(element) {
    element.loading(true, {mask: true, text: ''});
}


/*
 * Navigates to another page of results within a grid.
 */

function grid_navigate_page(link, url) {
    var div = $(link).parents('div.grid:first');
    loading(div);
    div.load(url);
}


/*
 * reload_grid_div(div)
 *
 * Reloads a grid's contents.  ``div``, if provied, is assumed to be an element
 * of type <div class="grid">, or else contain such an element.
 */

function reload_grid_div(div) {
    if (! div) {
        div = $('div.grid');
    } else if (! div.hasClass('grid')) {
        div = div.find('div.grid');
    }
    if (! div.length) {
        alert('assert: div should have length');
        return;
    }
    loading(div);
    div.load(div.attr('url'));
}


$(function() {

    $('div.filter label').live('click', function() {
        var checkbox = $(this).prev();
        if (checkbox.attr('checked')) {
            checkbox.attr('checked', false);
            return false;
        }
        checkbox.attr('checked', true);
        return true;
    });

    $('#add-filter').live('change', function() {
        var div = $(this).parents('div.filters:first');
        var filter = div.find('#filter-'+$(this).val());
        filter.find(':first-child').attr('checked', true);
        filter.show();
        var field = filter.find(':last-child');
        field.select();
        field.focus();
        $(this).find('option:selected').attr('disabled', true);
        $(this).val('add a filter');
        if ($(this).find('option[disabled=false]').length == 1) {
            $(this).hide();
        }
        div.find('input[type=submit]').show();
        div.find('button[type=reset]').show();
    });

    $('div.filters form').live('submit', function() {
        var div = $('div.grid:first');
        var data = $(this).serialize() + '&partial=true';
        loading(div);
        $.post(div.attr('url'), data, function(data) {
            div.replaceWith(data);
        });
        return false;
    });

    $('div.filters form div.buttons button[type=reset]').click(function() {
        var filters = $(this).parents('div.filters:first');
        filters.find('div.filter').each(function() {
            $(this).find('div.value input').val('');
        });
        var url = filters.attr('url');
        var grid = $('div.grid[url='+url+']');
        loading(grid);
        var form = filters.find('form');
        var data = form.serialize() + '&partial=true';
        $.post(url, data, function(data) {
            grid.replaceWith(data);
        });
        return false;
    });

    $('div.grid table th.sortable a').live('click', function() {
        var div = $(this).parents('div.grid:first');
        var th = $(this).parents('th:first');
        var dir = 'asc';
        if (th.hasClass('sorted') && th.hasClass('asc')) {
            dir = 'desc';
        }
        loading(div);
        var url = div.attr('url');
        url += url.match(/\?/) ? '&' : '?';
        url += 'sort=' + th.attr('field') + '&dir=' + dir;
        url += '&page=1';
        url += '&partial=true';
        div.load(url);
        return false;
    });

    $('div.grid.hoverable table tbody tr').live('mouseenter', function() {
        $(this).addClass('hovering');
    });

    $('div.grid.hoverable table tbody tr').live('mouseleave', function() {
        $(this).removeClass('hovering');
    });

    $('div.grid.clickable table tbody tr').live('mouseenter', function() {
        $(this).addClass('hovering');
    });

    $('div.grid.clickable table tbody tr').live('mouseleave', function() {
        $(this).removeClass('hovering');
    });

    $('div.grid.selectable table tbody tr').live('mouseenter', function() {
        $(this).addClass('hovering');
    });

    $('div.grid.selectable table tbody tr').live('mouseleave', function() {
        $(this).removeClass('hovering');
    });

    $('div.grid.checkable table tbody tr').live('mouseenter', function() {
        $(this).addClass('hovering');
    });

    $('div.grid.checkable table tbody tr').live('mouseleave', function() {
        $(this).removeClass('hovering');
    });

    $('div.grid.clickable table tbody td').live('click', function() {
        if (! $(this).hasClass('noclick')) {
            var row = $(this).parents('tr:first');
            var url = row.attr('url');
            if (url) {
                location.href = url;
            }
        }
    });

    $('div.grid table thead th.checkbox input[type=checkbox]').live('click', function() {
        var checked = $(this).is(':checked');
        var table = $(this).parents('table:first');
        table.find('tbody tr').each(function() {
            $(this).find('td.checkbox input[type=checkbox]').attr('checked', checked);
            // if (checked) {
            //     $(this).addClass('selected');
            // } else {
            //     $(this).removeClass('selected');
            // }
        });
    });

    $('div.grid.selectable table tbody tr').live('click', function() {
        var table = $(this).parents('table:first');
        if (! table.hasClass('multiple')) {
            table.find('tbody tr').removeClass('selected');
        }
        $(this).addClass('selected');
    });

    $('div.grid.checkable table tbody tr').live('click', function() {
        var checkbox = $(this).find('td:first input[type=checkbox]');
        checkbox.attr('checked', !checkbox.is(':checked'));
        $(this).toggleClass('selected');
    });

    $('div.grid table tbody td.edit').live('click', function() {
        var url = $(this).attr('url');
        if (url) {
            location.href = url;
        }
    });

    $('div.grid table tbody td.delete').live('click', function() {
        var url = $(this).attr('url');
        if (url) {
            if (confirm("Do you really wish to delete this object?")) {
                location.href = url;
            }
        }
    });

    $('#grid-page-count').live('change', function() {
        var div = $(this).parents('div.grid:first');
        loading(div);
        url = div.attr('url');
        url += url.match(/\?/) ? '&' : '?';
        url += 'per_page=' + $(this).val();
        url += '&partial=true';
        div.load(url);
    });

    $('div.autocomplete-container div.autocomplete-display button.autocomplete-change').live('click', function() {
        var container = $(this).parents('div.autocomplete-container');
        var display = $(this).parents('div.autocomplete-display');
        var textbox = container.find('input.autocomplete-textbox');
        var hidden = container.find('input[type=hidden]');
        display.hide();
        hidden.val('');
        textbox.show();
        textbox.select();
        textbox.focus();
    });

    $('div.dialog form').live('submit', function() {
        var form = $(this);
        var dialog = form.parents('div.dialog:first');
        $.ajax({
            type: 'POST',
            url: form.attr('action'),
            data: form.serialize(),
            success: function(data) {
                if (json_success(data)) {
                    if (dialog.attr('callback')) {
                        eval(dialog.attr('callback'))(data);
                    }
                    dialog.dialog('close');
                } else if (typeof(data) == 'object') {
                    alert(data.message);
                } else {
                    dialog.html(data);
                }
            },
            error: function() {
                alert("Sorry, something went wrong...try again?");
            },
        });
        return false;
    });
    
    $('div.dialog button.close').live('click', function() {
        var dialog = $(this).parents('div.dialog:first');
        dialog.dialog('close');
    });

    $('div.dialog button.cancel').live('click', function() {
        var dialog = $(this).parents('div.dialog:first');
        dialog.dialog('close');
    });

    $('div.dialog.lookup button.ok').live('click', function() {
        var dialog = $(this).parents('div.dialog.lookup:first');
        var tr = dialog.find('div.grid table tbody tr.selected');
        if (! tr.length) {
            alert("You haven't selected anything.");
            return false;
        }
        var uuid = get_uuid(tr);
        var col = parseInt(dialog.attr('textcol'));
        var text = tr.find('td:eq('+col+')').html();
        eval(dialog.attr('callback'))(uuid, text);
        dialog.dialog('close');
    });

});
