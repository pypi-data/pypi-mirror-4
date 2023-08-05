<%inherit file="/base.mako" />

<%def name="context_menu_items()"></%def>

<%def name="form()">
  % if search:
      ${search.render()}
  % else:
      &nbsp;
  % endif
</%def>

<%def name="tools()"></%def>

<div class="grid-wrapper">

  <table class="grid-header">
    <tr>
      <td rowspan="2" class="form">
        ${self.form()}
      </td>
      <td class="context-menu">
        <ul>
          ${self.context_menu_items()}
        </ul>
      </td>
    </tr>
    <tr>
      <td class="tools">
        ${self.tools()}
      </td>
    </tr>
  </table><!-- grid-header -->

  ${grid}

</div><!-- grid-wrapper -->
