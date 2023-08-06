// TODO ... cleanup ???
var selectWidgets = { 'GeoExtToolbar':  ['widget'],
                  'QueryOnClick': ['result', 'featurepanel']};
var resultExtGridWidgetId = 9;
var featurePanelSelectorWidgetId = 20;
var resultVectorLayerWidgetId = 44;

var jsonWidgets = null;
$(document).ready(function() {
    $.getJSON(BASE_URL+'widgets/', "request=getWidgetsList",
              function(data){
                  if (data && data.length!=0) {
                      $('#id_type').bind('change', onSelectTypeChange);
                      jsonWidgets = data;
                      $('#id_type').trigger('change');
                  }
              });
});

function onSelectTypeChange()
{
    var selected = $("#id_type option:selected");
    $('input[id^=id_widgetoption_set-][id$=-name]:visible').trigger('change', true);
    $('input[id^=id_widgetoption_set-][id$=-name]:visible').unbind('change');

    for (var widget in selectWidgets) {
        if (widget.toLowerCase() == selected.text().toLowerCase()) {
            $('input[id^=id_widgetoption_set-][id$=-name]:visible').bind('change', {widget:widget}, onInputTextChange);
            $('input[id^=id_widgetoption_set-][id$=-name]:visible').trigger('change');
            break;
        }
    }
}

function onInputTextChange(event, reset)
{
    var valueInput = $(this).attr('id').replace('name','value');
    if (!reset && ($.inArray($(this).val().toLowerCase(), selectWidgets[event.data.widget]) != -1)) {
        var val = $('#'+valueInput).val();
        var selectHtml = '<select id="'+valueInput+'" name="'+valueInput.substr(3)+'"><option value="">---------</option>';
        if (jsonWidgets) {
            for (i = 0; i < jsonWidgets.length; i++) {
                // should be generic some way.... in the future
                if (event.data.widget == 'QueryOnClick') {
                    if ($(this).val().toLowerCase() == 'result') {
                        if (jsonWidgets[i].type != resultExtGridWidgetId &&
                            jsonWidgets[i].type != resultVectorLayerWidgetId)
                            continue
                    }
                    else if ($(this).val().toLowerCase() == 'featurepanel') {
                        if (jsonWidgets[i].type != featurePanelSelectorWidgetId)
                            continue
                    }
                }
                selectHtml += '<option value="'+jsonWidgets[i].id+'">'+jsonWidgets[i].name+'</option>';
                
            }
        }
        selectHtml += '</select>'
        $('#'+valueInput).replaceWith(selectHtml);
        $('#'+valueInput+' option[value='+val+']').attr("selected", "true");
    }
    else {
        var val = $('select[id='+valueInput+'] option:selected').val();
        $('select[id='+valueInput+']').replaceWith('<input type="text" id="'+valueInput+'" name="'+valueInput.substr(3)+'" value="'+val+'"></input>');
    }
}
