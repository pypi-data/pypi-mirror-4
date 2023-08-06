<%inherit file="/grid.mako" />

<%def name="title()">Users</%def>

<%def name="context_menu_items()">
  % if request.has_perm('users.create'):
      <li>${h.link_to("Create a new User", url('user.create'))}</li>
  % endif
</%def>

${parent.body()}
