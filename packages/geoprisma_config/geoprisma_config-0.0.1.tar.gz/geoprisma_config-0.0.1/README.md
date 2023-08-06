Geoprisma Config
================

Tool to configure geoprisma maps using a prostgresql database. It's made to be installed in a django app.

Geoprisma is a library used for webmapping made by MapGears. You can find the code at http://www.geoprisma.org

Quick start
-----------

Contrib Admin is required.

1. Add "geoprisma_config" to your INSTALLED_APPS setting like this::

      INSTALLED_APPS = (
          ...
          'geoprisma_config',
      )

2. Include the geoprisma_config URLconf in your project urls.py like this::

      url(r'^geoprisma_config/', include('geoprisma_config.urls')),

3. Run `python manage.py syncdb` to create the geoprisma_config models.

4. Start the development server and visit http://127.0.0.1:8000/admin/
  to manage your geoprisma configs (you'll need the Admin app enabled).

Production Setup
----------------

Staticfiles is needed to work, so check https://docs.djangoproject.com/en/dev/howto/static-files/ for support.

Tested
------

This app have been tested with Django 1.3, tests for django 1.4 and 1.5 are on the way.
Django 1.2 might be ok if you add django-staticfiles app. Check https://docs.djangoproject.com/en/dev/howto/static-files/

BSD License
=======

Copyright (c) 2013, Solution Globale Informatique & Nippour
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
1. Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.
3. All advertising materials mentioning features or use of this software
   must display the following acknowledgement:
   This product includes software developed by the Solution Globale Informatique and Nippour.
4. Neither the name of the Solution Globale Informatique and Nippour nor the
   names of its contributors may be used to endorse or promote products
   derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY Solution Globale Informatique AND Nippour ''AS IS'' AND ANY
EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL Solution Globale Informatique or Nippour BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.