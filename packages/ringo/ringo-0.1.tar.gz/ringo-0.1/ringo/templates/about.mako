## -*- coding: utf-8 -*-
<%inherit file="/layout.mako" />
<h1>${_('About')}</h1>
<p>${_('This application is based on the ringo application')}</p>
<h2>${_('ringo')} ${h.get_package_version('ringo')}</h2>
<p>${_('ringo is a pyramid template which provides common basic functionality for building highlevel webapplication.')}</p>
<p>${_('source code is available here:')} <a href="http://bitbucket.org/ti/ringo" target="_blank">http://bitbucket.org/ti/ringo</a></p>
<p>${_('documentation available here:')} <a href="https://readthedocs.org/projects/ringo" target="_blank">https://readthedocs.org/projects/ringo</a></p>
<p>${_('ringo is currnently installed in version %s') % h.get_package_version('ringo')}</p>
<h2>${_('license')}</h2>
<p>
This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
</p>
<h2>${_('authors')}</h2>
<ul>
  <li>Torsten Irländer (Maintainer, Developer)</li>
</ul>
