<div ${grid.div_attrs()}>
  <table>
    <thead>
      <tr>
        % if grid.checkboxes:
            <th class="checkbox">${h.checkbox('check-all')}</th>
        % endif
        % for field in grid.iter_fields():
            ${grid.column_header(field)}
        % endfor
        % for col in grid.extra_columns:
            <th>${col.label}</td>
        % endfor
        % if grid.editable:
            <th>&nbsp;</th>
        % endif
        % if grid.deletable:
            <th>&nbsp;</th>
        % endif
      </tr>
    </thead>
    <tbody>
      % for i, row in enumerate(grid.iter_rows(), 1):
          <tr ${grid.get_row_attrs(row, i)}>
            % if grid.checkboxes:
                <td class="checkbox">${grid.checkbox(row)}</td>
            % endif
            % for field in grid.iter_fields():
                <td class="${grid.cell_class(field)}">${grid.render_field(field)}</td>
            % endfor
            % for col in grid.extra_columns:
                <td class="noclick ${col.name}">${col.callback(row)}</td>
            % endfor
            % if grid.editable:
                <td class="noclick edit" url="${grid.get_edit_url(row)}">&nbsp;</td>
            % endif
            % if grid.deletable:
                <td class="noclick delete" url="${grid.get_delete_url(row)}">&nbsp;</td>
            % endif
          </tr>
      % endfor
    </tbody>
  </table>
  % if grid.pager:
      <div class="pager">
        <p class="showing">
          showing ${grid.pager.first_item} thru ${grid.pager.last_item} of ${grid.pager.item_count}
          (page ${grid.pager.page} of ${grid.pager.page_count})
        </p>
        <p class="page-links">
          ${h.select('grid-page-count', grid.pager.items_per_page, grid.page_count_options())}
          per page&nbsp;
          ${grid.page_links()}
        </p>
      </div>
  % endif
</div>
