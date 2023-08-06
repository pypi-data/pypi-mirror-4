## -*- coding: utf-8 -*-
<%inherit file="/layout.mako" />
<div class="row-fluid">
  <div class="span4 offset4">
    <div class="well">
      <h4>Login</h4>
      ${form.begin(request.resource_url(request.root, 'auth/login'), class_='form-signing')}
      ${form.text("username", size=30, placeholder=_('Username'))}
      ##<span class="error">${form.errorlist("username")}</span>
      ${form.text("password", size=30, placeholder=_('Password'))}
      ##<span class="error">${form.errorlist("password")}</span>
      <br/>
      ${form.submit("submit", _('Login'), class_="btn btn-primary")}
    </form>
    </div>
  </div>
</div>
