<div class="grid${' '+class_ if class_ else ''}" ${grid.url_attrs()|n}>

  <table>
    <thead>
      <tr>
        % if checkboxes:
            <th class="checkbox">${h.checkbox('check-all')}</th>
        % endif
        % for field in grid.iter_fields():
            ${grid.column_header(field)}
        % endfor
        % for col in grid.extra_columns:
            <th>${col.label}</td>
        % endfor
        % if grid.deletable:
            <th>&nbsp;</th>
        % endif
      </tr>
    </thead>

    <tbody>
      % for i, row in enumerate(grid.rows):
          <% grid._set_active(row) %>
          <tr ${grid.row_attrs(i)|n}>
            % if checkboxes:
                <td class="checkbox">${h.checkbox('check-'+grid.model.uuid, disabled=True)}</td>
            % endif
            % for field in grid.iter_fields():
                <td class="${grid.field_name(field)}">${grid.render_field(field, True)|n}</td>
            % endfor
            % for col in grid.extra_columns:
                <td class="${col.name}">${col.callback(row)|n}</td>
            % endfor
            % if grid.deletable:
                <td class="delete">&nbsp;</td>
            % endif
          </tr>
      % endfor
    </tbody>
  </table>
  % if hasattr(grid, 'pager') and grid.pager:
      <div class="pager">
        <p class="showing">
          showing
          ${grid.pager.first_item} thru ${grid.pager.last_item} of ${grid.pager.item_count}
        </p>
        <p class="page-links">
          ${h.select('grid-page-count', grid.pager.items_per_page, (5, 10, 20, 50, 100))}
          per page:&nbsp;
          ${grid.pager.pager('~3~', onclick='return grid_navigate_page($(this));')}
        </p>
      </div>
  % endif
</div>
