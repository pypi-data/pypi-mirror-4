<%def name="autocomplete(field_name, service_url, field_value=None, field_display=None, width='300px', callback=None)">
  <div id="${field_name}-container" class="autocomplete-container">
    ${h.hidden(field_name, id=field_name, value=field_value)}
    ${h.text(field_name+'-textbox', id=field_name+'-textbox', value=field_display,
        class_='autocomplete-textbox', style='display: none;' if field_value else '')}
    <div id="${field_name}-display" class="autocomplete-display"${'' if field_value else ' style="display: none;"'|n}>
      <span>${field_display or ''}</span>
      <button type="button" id="${field_name}-change" class="autocomplete-change">Change</button>
    </div>
  </div>
  <script language="javascript" type="text/javascript">
    $(function() {
        var autocompleter_${field_name.replace('-', '_')} = $('#${field_name}-textbox').autocomplete({
            serviceUrl: '${service_url}',
            width: '${width}',
            onSelect: function(value, data) {
                $('#${field_name}').val(data);
                $('#${field_name}-display span').text(value);
                $('#${field_name}-textbox').hide();
                $('#${field_name}-display').show();
                $('#${field_name}-change').focus();
                % if callback:
                    ${callback}(data, value);
                % endif
            },
        });
    });
  </script>
</%def>
