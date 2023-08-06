## -*- coding: utf-8 -*-
<%inherit file="/base.mako" />
<div id="wrap">
  <div class="container">
    <%include file="/header.mako" />
    <div id="main">
      ${self.flash_messages()}
      ${next.body()}
    </div>
  </div>
  <div id="push"></div>
</div>
<%include file="/footer.mako" />

## flash messages with css class und fade in options  
<%def name="flash_messages()">  
  % if request.session.peek_flash():  
    <% flash = request.session.pop_flash() %>  
    % for message in flash:  
      <div class="alert ${message.split(';')[0]} fade in">  
        <button type="button" class="close" data-dismiss="alert">&times;</button>
        ${message.split(";")[1]}</div>  
    % endfor  
  % endif  
</%def>
