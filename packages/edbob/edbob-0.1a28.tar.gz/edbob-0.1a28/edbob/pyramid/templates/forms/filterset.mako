<div class="filterset">
  ${search.begin()}
  ${search.hidden('filters', True)}
  <% visible = [] %>
  % for f in search.sorted_filters():
      <% f = search.filters[f] %>
      <div class="filter" id="filter-${f.name}"${' style="display: none;"' if not search.config.get('include_filter_'+f.name) else ''|n}>
	${search.checkbox('include_filter_'+f.name)}
	<label for="${f.name}">${f.label}</label>
	${f.types_select()}
	${f.value_control()}
      </div>
      % if search.config.get('include_filter_'+f.name):
          <% visible.append(f.name) %>
      % endif
  % endfor
  <div class="buttons">
    ${search.add_filter(visible)}
    ${search.submit('submit', "Search", style='display: none;' if not visible else None)}
    <button type="reset"${' style="display: none;"' if not visible else ''}>Reset</button>
  </div>
  ${search.end()}
  % if visible:
      <script language="javascript" type="text/javascript">
	var filters_to_disable = [
	    % for field in visible:
		'${field}',
	    % endfor
	];
	% if not dialog:
	    $(function() {
		disable_filter_options();
	    });
	% endif
      </script>
  % endif
</div>
