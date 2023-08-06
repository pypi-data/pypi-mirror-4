<div class="footer navbar navbar-fixed-bottom">
  <div class="navbar-inner">
    ##% if h.auth.is_authorized([h.auth.UserIsAuthenticated(h.get_user_from_session(session)), \
    ##                           h.auth.UserHasRole(h.get_user_from_session(session), 'admin')]) \
    ##     and h.get_uid_from_session(session) != h.get_uid_of_anonymous_user():
    <ul class="nav">
      <li class="dropdown">
        <a href="#" class="dropdown-toggle" data-toggle="dropdown">
          <img src="/static/images/icons/16x16/applications-system.png" alt="${_('Administration')}"/>${_('Administration')}<b class="caret"></b></a>
        <ul class="dropdown-menu">
          <li class="divider"></li>
          #####################
          #### ADMINSTRATION ##
          #####################
          ##${render_admin_menu(h.UserItem)}
          ##<li class="divider"></li>
          ##${render_admin_menu(h.UsergroupItem)}
          ##<li class="divider"></li>
          ##${render_admin_menu(h.ModulItem)}
          ##<li class="divider"></li>
          ##${render_admin_menu(h.RoleItem)}
        </ul>
      </li>
    </ul>
    ##% endif
    <ul class="nav pull-right">
      <li>
        <a href="/contact" alt="${_('Contact')}">${_('Contact')}</a>
      </li>
      <li>
        <a href="/about" alt="${_('About')}">${_('About')}</a>
      </li>
      <li>
        <a href="#" class="muted">ringo version 1.0</a>
      </li>
    </ul>
  </div>
</div>

##<%def name="render_admin_menu(item)">
##  ##% if h.auth.is_authorized([h.auth.UserHasPermission(h.get_user_from_session(session), item, h.actions.READ)]) and item.get_item_modul().show == True:
##  ##  <li>
##  ##    <a href="${h.url(controller=item.get_item_modul().get_controller_url(), action='list')+'?reset=1'}">${item.get_item_modul().get_name(plural=True)} ${_('Overview')}</a>
##  ##  </li>
##  ##  % if h.auth.is_authorized([h.auth.UserHasPermission(h.get_user_from_session(session), item, h.actions.CREATE)]):
##  ##    <li><a href="${h.url(controller=item.get_item_modul().get_controller_url(), action='create')}">${_('Create %s') % item.get_item_modul().get_name()}</a></li>
##  ##  % endif
##  ##% endif
##</%def>
