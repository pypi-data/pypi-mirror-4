<%inherit file="/users/base.mako" />
<%inherit file="/index.mako" />

<%def name="title()">Users</%def>

<%def name="context_menu_items()">
  <li>${h.link_to("Create a new User", url('user.new'))}</li>
</%def>

${parent.body()}
