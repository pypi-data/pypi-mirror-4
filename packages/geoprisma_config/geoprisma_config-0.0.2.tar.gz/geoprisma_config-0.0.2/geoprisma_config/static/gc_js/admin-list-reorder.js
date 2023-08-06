$(document).ready(function() {
    // Set this to the name of the column holding the position
    pos_field = 'order';
    
    // Determine the column number of the position field
    pos_col = null;
    
    // loop though inline-group fielset
    $('.inline-group').each(function(index) {
        
        cols = $('tbody tr:first', $(this)).children();

        for (i = 0; i < cols.length; i++) {
            inputs = $(cols[i]).find('input[name*=' + pos_field + ']')
            
            if (inputs.length > 0) {
                // Found!
                pos_col = i;
                break;
            }
        }
        
        if (pos_col == null) {
            return;
        }
        
        // Some visual enhancements
        header = $('thead tr', $(this)).children()[pos_col]
        $(header).css('width', '1em')
        $(header).children('a').text('#')
        
        // Hide position field
        $('tbody tr', $(this)).each(function(index) {
            pos_td = $(this).children()[pos_col]
            input = $(pos_td).children('input').first()
            //input.attr('type', 'hidden')
            input.hide()
            
            label = $('<strong>' + input.attr('value') + '</strong>')
            $(pos_td).append(label)
        });
        
        // Determine sorted column and order
        sorted = $('thead th:contains("Order")', $(this));
        sorted_col = $('thead th', $(this)).index(sorted)+1;
        sort_order = sorted.hasClass('descending') ? 'desc' : 'asc';
        
        if (sorted_col != pos_col) {
            // Sorted column is not position column, bail out
            console.info("Sorted column is not %s, bailing out", pos_field);
            return;
        }
        
        $('tbody tr.has_original', $(this)).css('cursor', 'move')
        
        // Make tbody > tr sortable
        $('tbody', $(this)).sortable({
            axis: 'y',
            items: 'tr.has_original',
            cursor: 'move',
            update: function(event, ui) {
                item = ui.item
                items = $(this).find('tr.has_original').get()
                
                if (sort_order == 'desc') {
                    // Reverse order
                    items.reverse()
                }
                
                $(items).each(function(index) {
                    pos_td = $(this).children()[pos_col]
                    input = $(pos_td).children('input').first()
                    label = $(pos_td).children('strong').first()
                    
                    input.attr('value', index+1)
                    label.text(index+1)
                });
                
                // Update row classes
                $(this).find('tr').removeClass('row1').removeClass('row2')
                $(this).find('tr:even').addClass('row1')
                $(this).find('tr:odd').addClass('row2')
            }
        });
    });
});
