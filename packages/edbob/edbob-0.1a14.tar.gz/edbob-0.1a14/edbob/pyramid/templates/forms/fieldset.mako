<% _focus_rendered = False %>

% for error in fieldset.errors.get(None, []):
    <div class="fieldset-error">${error}</div>
% endfor

% for field in fieldset.render_fields.itervalues():

    % if field.requires_label:
        <div class="field-wrapper ${field.name}">
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

        % if not _focus_rendered and (fieldset.focus == field or fieldset.focus is True):
            % if not field.is_readonly() and getattr(field.renderer, 'needs_focus', True):
                <script language="javascript" type="text/javascript">
                  $(function() {
                      % if hasattr(field.renderer, 'focus_name'):
                          $('#${field.renderer.focus_name}').focus();
                      % else:
                          $('#${field.renderer.name}').focus();
                      % endif
                  });
                </script>
                <% _focus_rendered = True %>
            % endif
        % endif
    % endif

% endfor
