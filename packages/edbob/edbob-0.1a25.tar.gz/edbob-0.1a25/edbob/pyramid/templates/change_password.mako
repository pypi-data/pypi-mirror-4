<%inherit file="/base.mako" />

<%def name="title()">Change Password</%def>

<div class="form">
  ${h.form(url('change_password'))}
  ${form.referrer_field()}
  ${form.field_div('current_password', form.password('current_password'))}
  ${form.field_div('new_password', form.password('new_password'))}
  ${form.field_div('confirm_password', form.password('confirm_password'))}
  <div class="buttons">
    ${h.submit('submit', "Change Password")}
  </div>
  ${h.end_form()}
</div>
