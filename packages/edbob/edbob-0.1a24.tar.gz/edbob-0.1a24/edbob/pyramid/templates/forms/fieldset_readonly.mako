<div class="fieldset">
  % for field in fieldset.render_fields.itervalues():
      % if field.requires_label:
          <div class="field-wrapper ${field.name}">
            ${field.label_tag()|n}
            <div class="field">
              ${field.render_readonly()}
            </div>
          </div>
      % endif
  % endfor
</div>
