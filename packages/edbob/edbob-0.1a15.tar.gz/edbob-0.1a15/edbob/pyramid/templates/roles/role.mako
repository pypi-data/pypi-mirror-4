<%inherit file="/roles/base.mako" />
<%inherit file="/crud.mako" />

<%def name="crud_name()">Role</%def>

<%def name="head_tags()">
  ${parent.head_tags()}
  ${h.stylesheet_link(request.static_url('edbob.pyramid:static/css/perms.css'))}
</%def>

<%def name="menu()">
  <p>${h.link_to("Back to Roles", url('roles.list'))}</p>
</%def>

${parent.body()}
