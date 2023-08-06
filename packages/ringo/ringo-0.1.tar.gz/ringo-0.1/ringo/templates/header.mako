<div class="navbar navbar-fixed-top">
  <div class="navbar-inner">
    <div class="container">
      <a class="btn btn-navbar" data-toggle="collapse" data-target=".nav-collapse">
        <span class="icon-bar"></span>
        <span class="icon-bar"></span>
        <span class="icon-bar"></span>
      </a>
      <a class="brand" href="/">ringo</a>
      <div class="nav-collapse collapse">
        <p class="navbar-text pull-right"> 
          ##% if h.auth.is_authorized([h.auth.UserIsAuthenticated(h.get_user_from_session(session))]) \
          ##  and h.get_uid_from_session(session) != h.get_uid_of_anonymous_user():
          ##  ${_('Logged in as:')} 
          ##  "${h.get_user_from_session(session).get_username()}"
          ##  | <a class="navbar-link" href="${h.url(controller='authentification', action='logout')}">${_('Logout')}</a>
          ##% endif
        </p>
        <ul class="nav">
          ##<li>
          ##  <a href="/index" alt="${_('Home')}')">${_('Home')}</a></li>
          ##</li>
        </ul>
      </div><!--/.nav-collapse -->
    </div>
  </div>
</div>
