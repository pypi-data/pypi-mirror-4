<%inherit file="/roles/base.mako" />
<%inherit file="/index.mako" />

<%def name="title()">Roles</%def>

<%def name="context_menu_items()">
  <li>${h.link_to("Create a new Role", url('role.new'))}</li>
</%def>

${parent.body()}
