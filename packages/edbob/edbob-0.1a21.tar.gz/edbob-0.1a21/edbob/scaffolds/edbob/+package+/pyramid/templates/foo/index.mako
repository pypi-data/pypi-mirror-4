<%inherit file="/foo/base.mako" />
<%inherit file="/index.mako" />

<%def name="title()">Foo</%def>

<%def name="menu()">
  % if request.has_perm('foo.create'):
      <p>${h.link_to("Create a new Foo", url('foo.new'))}</p>
  % endif
</%def>

${parent.body()}
