<%inherit file="/grid.mako" />

<%def name="title()">People</%def>

<%def name="context_menu_items()">
##   % if request.has_perm('people.create'):
##       <li>${h.link_to("Create a new Person", url('person.new'))}</li>
##   % endif
</%def>

${parent.body()}
