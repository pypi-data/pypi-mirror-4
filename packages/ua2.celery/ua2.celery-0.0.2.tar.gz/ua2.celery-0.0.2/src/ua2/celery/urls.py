"""
All views accept extra parameter: auth_decorator

Example:
from django.contrib.auth.decorators import login_required
urlpatterns += patterns('',
   (r'^celery/', include('ua2.celery.urls'), {'auth_decorator': login_required}),
)

With this decorator each request passing through authorization

"""
from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('ua2.celery.views',
    url('^status/(?P<task_id>.*)/$', 'task_status', name='ua2-celery-task-status'),
)
