<%inherit file="/base.mako" />

<%def name="title()">Login</%def>

<%def name="head_tags()">
  ${parent.head_tags()}
  ${h.stylesheet_link(request.static_url('edbob.pyramid:static/css/login.css'))}
  ${self.logo_styles()}
</%def>

<%def name="logo_styles()">
  <style type="text/css">

    #login-logo {
        background-image: url(${request.static_url('edbob.pyramid:static/img/logo.jpg')});
        background-size: 350px auto;
        height: 114.25px;
        margin: 25px auto;
        width: 350px;
    }

  </style>
</%def>

<div id="login-logo"></div>

<div class="form">
  ${h.form('')}
##  <input type="hidden" name="login" value="True" />
  <input type="hidden" name="referrer" value="${referrer}" />

  % if error:
      <div class="error">${error}</div>
  % endif

  <div class="field-wrapper">
    <label for="username">Username:</label>
    <input type="text" name="username" id="username" value="" />
  </div>

  <div class="field-wrapper">
    <label for="password">Password:</label>
    <input type="password" name="password" id="password" value="" />
  </div>

  <div class="buttons">
    ${h.submit('submit', "Login")}
    <input type="reset" value="Reset" />
  </div>

  ${h.end_form()}
</div>

<script language="javascript" type="text/javascript">

$(function() {

    $('form').submit(function() {
        if (! $('#username').val()) {
            with ($('#username').get(0)) {
            select();
            focus();
            }
            return false;
        }
        if (! $('#password').val()) {
            with ($('#password').get(0)) {
            select();
            focus();
            }
            return false;
        }
        return true;
    });

    $('#username').focus();

});

</script>
