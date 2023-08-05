<%inherit file="/users/base.mako" />
<%inherit file="/crud.mako" />

<%def name="crud_name()">User</%def>

<%def name="context_menu_items()">
  <li>${h.link_to("Back to Users", url('users.list'))}</li>
</%def>

${parent.body()}
