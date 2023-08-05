<%inherit file="/crud.mako" />

<%def name="crud_name()">Person</%def>

<%def name="context_menu_items()">
  <li>${h.link_to("Back to People", url('people'))}</li>
</%def>

${parent.body()}

## % if fieldset.edit:
##     <h2>User Info</h2>
##     % if user:
##     ${user.render()|n}
##     <div class="buttons">
##       <button type="button" onclick="location.href = '${url('user.edit', uuid=user.model.uuid)}';">Edit User</button>
##     </div>
##     % else:
##     <p>This person does not have a user account.</p>
##     ${h.form(url('user.new'))}
##     ${h.hidden('User--person_uuid', value=fieldset.model.uuid)}
##     ${h.hidden('User--username')}
##     <div class="buttons">
##       ${h.submit('submit', "Create User")}
##     </div>
##     ${h.end_form()}
##     % endif
## % endif
