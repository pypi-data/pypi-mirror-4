<%inherit file="/grid.mako" />

<%def name="title()">Roles</%def>

<%def name="context_menu_items()">
  % if request.has_perm('roles.create'):
      <li>${h.link_to("Create a new Role", url('role.create'))}</li>
  % endif
</%def>

${parent.body()}
