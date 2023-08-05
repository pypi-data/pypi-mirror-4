<%def name="global_title()">edbob</%def>
<%def name="title()"></%def>
<%def name="head_tags()"></%def>
<%def name="home_link()"><h1 class="right">${h.link_to("Home", url('home'))}</h1></%def>
<%def name="menu()"></%def>
<%def name="footer()">
  powered by ${h.link_to('edbob', 'http://edbob.org', target='_blank')} v${edbob.__version__}
</%def>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html style="direction: ltr;" xmlns="http://www.w3.org/1999/xhtml" lang="en-us">
  <head>
    <meta http-equiv="content-type" content="text/html; charset=UTF-8" />
    <title>${self.global_title()}${' : ' + capture(self.title) if capture(self.title) else ''}</title>

    ${h.javascript_link(request.static_url('edbob.pyramid:static/js/jquery.js'))}
    ${h.javascript_link(request.static_url('edbob.pyramid:static/js/jquery.ui.js'))}
    ${h.javascript_link(request.static_url('edbob.pyramid:static/js/jquery.loading.js'))}
    ${h.javascript_link(request.static_url('edbob.pyramid:static/js/jquery.autocomplete.js'))}
    ${h.javascript_link(request.static_url('edbob.pyramid:static/js/edbob.js'))}

    ${h.stylesheet_link(request.static_url('edbob.pyramid:static/css/edbob.css'))}
    ${h.stylesheet_link(request.static_url('edbob.pyramid:static/css/grids.css'))}
    ${h.stylesheet_link(request.static_url('edbob.pyramid:static/css/filters.css'))}
    ${h.stylesheet_link(request.static_url('edbob.pyramid:static/css/forms.css'))}
    ${h.stylesheet_link(request.static_url('edbob.pyramid:static/css/autocomplete.css'))}
    ${h.stylesheet_link(request.static_url('edbob.pyramid:static/css/smoothness/jquery-ui-1.8.2.custom.css'))}

    ${self.head_tags()}
  </head>

  <body>

    <div id="container">

      <div id="header">
        ${self.home_link()}
        <h1 class="left">${self.title()}</h1>
        <div id="login" class="right">
          % if request.user:
              logged in as <strong>${request.user.display_name}</strong>
              (${h.link_to("logout", url('logout'))})
          % else:
              ${h.link_to("login", url('login'))}
          % endif
        </div>
      </div><!-- header -->

      <div id="body">
        % if request.session.peek_flash('error'):
            <div id="error-messages">
              % for error in request.session.pop_flash('error'):
                  <div class="error">${error}</div>
              % endfor
            </div>
        % endif
        % if request.session.peek_flash():
            <div id="flash-messages">
              % for msg in request.session.pop_flash():
                  <div class="flash-message">${msg|n}</div>
              % endfor
            </div>
        % endif
        ${self.body()}
      </div><!-- body -->

    </div><!-- container -->

    <div id="footer">
      ${self.footer()}
    </div>

  </body>
</html>
