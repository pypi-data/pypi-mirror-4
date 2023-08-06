$(document).ready(function() {
    // hide the last row of all inline groups, it doesn't save anyway. (django 1.2.1)
    $('.inline-group').each(function(index) {
        $('tr:last', $(this)).hide();
    });
});