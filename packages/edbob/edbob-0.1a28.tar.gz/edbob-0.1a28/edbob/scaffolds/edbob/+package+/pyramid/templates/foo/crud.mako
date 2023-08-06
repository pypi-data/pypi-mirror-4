<%inherit file="/foo/base.mako" />
<%inherit file="/crud.mako" />

<%def name="menu()">
  <p>${h.link_to("Back to Foo", url('foo.list'))}</p>
</%def>

${parent.body()}
