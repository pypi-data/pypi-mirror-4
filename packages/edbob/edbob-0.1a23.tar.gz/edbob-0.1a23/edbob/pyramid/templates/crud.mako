<%inherit file="/form.mako" />

<%def name="title()">${"New "+form.pretty_name if form.creating else form.pretty_name+' : '+h.literal(str(form.fieldset.model))}</%def>

<%def name="head_tags()">
  ${parent.head_tags()}
  <script type="text/javascript">
    $(function() {
        $('a.delete').click(function() {
            if (! confirm("Do you really wish to delete this object?")) {
                return false;
            }
        });
    });
  </script>
</%def>

${parent.body()}
