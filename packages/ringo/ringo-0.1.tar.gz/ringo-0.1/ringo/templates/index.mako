## -*- coding: utf-8 -*-
<%inherit file="layout.mako" />

<div class="row-fluid">
% if request.user:
  <div class="span12">
% else: 
  <div class="span9">
% endif
<h1>${_('Getting started')}</h1>
</div>

% if not request.user:
  <div class="span3">
    <div class="well">
    <h4>${_('Login')}</h4>
    <%include file="/auth/login_form.mako" />
    </div>
  </div>
% endif
</div>
