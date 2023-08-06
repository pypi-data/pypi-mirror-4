

function hideCells(input, parentSelector) {
    var cls = input.value;
    var checked = input.checked;
    if (checked) {
        $(cls).removeClass('hidden');
    } else {
        $(cls).addClass('hidden');
    }
    $(parentSelector).each(
        function () {
            var visible = $(this).find('> .cell:not(.dummy):not(.hidden)');
            var s = visible.size();
            visible.css('width', (100.0 - s + 1)/s + '%');
        }
    );
    $('.item-inner.day').each(
        function () {
            var n = $(this);
            var p = n.closest('li.day');
            var day = {};
            day.date = Y.Lang.trim(n.text().slice(0, n.text().indexOf('–')));
            Y.log(day.date);
            day.tree_count = p.find('.cell.tree:not(.dummy):not(.hidden)').size();
            day.build_count = p.find('.cell.tree:not(.dummy):not(.hidden) .cell.build:not(.dummy):not(.hidden)').size();
            day.test_count = p.find('.cell.tree:not(.dummy):not(.hidden) .cell.build:not(.dummy):not(.hidden) .cell.test:not(.dummy):not(.hidden)').size();
            n.text(dayText(day));
        }
    );
}

function dayText (day) {
    return day.date + ' – ' + day.test_count + ' tests of '
                + day.build_count + ' builds on ' + day.tree_count + ' trees';
}
