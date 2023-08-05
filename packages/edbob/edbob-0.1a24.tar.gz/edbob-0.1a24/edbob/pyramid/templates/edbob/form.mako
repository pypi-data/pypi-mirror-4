<%inherit file="/base.mako" />

<%def name="context_menu_items()"></%def>

<div class="form-wrapper">

  <ul class="context-menu">
    ${self.context_menu_items()}
  </ul>

  ${form.render()|n}

</div>
