<% _focus_rendered = False %>

<div class="form">
  ${h.form(form.action_url, enctype='multipart/form-data')}

  % for error in form.errors.get(None, []):
      <div class="fieldset-error">${error}</div>
  % endfor

  % for field in form.render_fields.itervalues():

      <div class="field-couple ${field.name}">
        % for error in field.errors:
            <div class="field-error">${error}</div>
        % endfor
        ${field.label_tag()|n}
        <div class="field">
          ${field.render()|n}
        </div>
        % if 'instructions' in field.metadata:
            <span class="instructions">${field.metadata['instructions']}</span>
        % endif
      </div>

      % if (form.focus == field or form.focus is True) and not _focus_rendered:
          % if not field.is_readonly():
              <script language="javascript" type="text/javascript">
                $(function() {
                    $('#${field.renderer.name}').focus();
                });
              </script>
              <% _focus_rendered = True %>
          % endif
      % endif

  % endfor

  % if form.successive:
      <div class="checkbox">
        ${h.checkbox('keep-going', checked=True)}
        <label for="keep-going">Add another after this one</label>
      </div>
  % endif

  <div class="buttons">
    ${h.submit('submit', "Save")}
    <button type="button" class="cancel">Cancel</button>
  </div>
  ${h.end_form()}
</div>

<script language="javascript" type="text/javascript">
  $(function() {
      $('button.cancel').click(function() {
          location.href = '${form.home_url}';
      });
  });
</script>
