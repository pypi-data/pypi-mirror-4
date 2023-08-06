from django.conf.urls import patterns

urlpatterns = patterns('feedback.views',
            (r'^(?P<campaign_slug>[a-zA-Z0-9-_]+)/api/$', 'accept_feedback_api'),
            )
