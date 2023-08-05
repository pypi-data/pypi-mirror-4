from pykeg.core import features

from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin
from django.contrib.auth.views import password_reset
from django.contrib.auth.views import password_reset_complete
from django.contrib.auth.views import password_reset_confirm
from django.contrib.auth.views import password_reset_done
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

admin.autodiscover()

try:
  from registration.views import register
  from pykeg.web.kegweb.forms import KegbotRegistrationForm
  USE_DJANGO_REGISTRATION = True
except ImportError:
  USE_DJANGO_REGISTRATION = False

urlpatterns = patterns('',
    ### django admin site
    (r'^admin/', include(admin.site.urls)),

    (r'^favicon.ico$', 'django.views.generic.simple.redirect_to',
      {'url': '/site_media/images/favicon.ico'}),

    ### RESTful api
    (r'^(?P<kbsite_name>)api/', include('pykeg.web.api.urls')),

    ### account
    (r'^account/', include('pykeg.web.account.urls')),

    (r'^accounts/', include('pykeg.web.registration.urls')),
    url(r'^accounts/password/reset/$', password_reset, {'template_name':
     'registration/password_reset.html'}, name="password-reset"),
    (r'^accounts/password/reset/done/$', password_reset_done, {'template_name':
     'registration/password_reset_done.html'}),
    (r'^accounts/password/reset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', password_reset_confirm, {'template_name':
     'registration/password_reset_confirm.html'}),
    (r'^accounts/password/reset/complete/$', password_reset_complete, {'template_name':
     'registration/password_reset_complete.html'}),

    ### socialregistration
    (r'^sr/', include('socialregistration.urls', namespace='socialregistration')),

    ### charts
    (r'^(?P<kbsite_name>)charts/', include('pykeg.web.charts.urls')),

    ### kegadmin
    (r'^(?P<kbsite_name>)kegadmin/', include('pykeg.web.kegadmin.urls')),
)

if features.use_facebook():
  urlpatterns += patterns('',
      ### facebook kegweb stuff
      (r'^(?P<kbsite_name>)fb/', include('pykeg.web.contrib.facebook.urls')),
  )

### accounts and registration
# uses the stock django-registration views, except we need to override the
# registration class for acocunt/register
if USE_DJANGO_REGISTRATION:
  from django.contrib.auth import views as auth_views
  urlpatterns += patterns('',
    url(r'^(?P<kbsite_name>)accounts/register/$', register,
      {'form_class':KegbotRegistrationForm},
      name='registration_register',
    ),
   (r'^accounts/', include('registration.urls')),
  )

if settings.DEBUG:
  urlpatterns += staticfiles_urlpatterns()
  urlpatterns += patterns('',
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': settings.MEDIA_ROOT, }),
  )

### Raven
if settings.HAVE_SENTRY:
  urlpatterns += patterns('',
      (r'^sentry/', include('sentry.web.urls')),
  )

### main kegweb urls
urlpatterns += patterns('',
  (r'^(?P<kbsite_name>)', include('pykeg.web.kegweb.urls')),
)
