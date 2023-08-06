<form class="form-signin" action="/auth/login" method="POST">
<input type="text" name="username" id="username" placeholder="${_('Username')}">
<span class="error"><form:error name="username" format=""></span>
<input type="password" name="password" id="password" placeholder="${_('Password')}">
<span class="error"><form:error name="password" format=""></span>
<br/>
<input type="submit" class="btn btn-primary" value="${_('Sign in')}">
</form>
