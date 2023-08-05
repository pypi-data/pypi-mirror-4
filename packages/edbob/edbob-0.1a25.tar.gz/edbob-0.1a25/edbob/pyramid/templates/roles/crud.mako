<%inherit file="edbob.pyramid:templates/crud.mako" />

<%def name="head_tags()">
  ${parent.head_tags()}
  ${h.stylesheet_link(request.static_url('edbob.pyramid:static/css/perms.css'))}
</%def>

<%def name="context_menu_items()">
  <li>${h.link_to("Back to Roles", url('roles'))}</li>
  % if form.readonly:
      <li>${h.link_to("Edit this Role", url('role.update', uuid=form.fieldset.model.uuid))}</li>
  % elif form.updating:
      <li>${h.link_to("View this Role", url('role.read', uuid=form.fieldset.model.uuid))}</li>
  % endif
  <li>${h.link_to("Delete this Role", url('role.delete', uuid=form.fieldset.model.uuid), class_='delete')}</li>
</%def>

${parent.body()}
