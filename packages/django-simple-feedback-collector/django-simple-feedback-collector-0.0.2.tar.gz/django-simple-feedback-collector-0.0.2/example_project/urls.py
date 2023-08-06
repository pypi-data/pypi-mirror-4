from django.conf.urls import patterns, include
from django.views.generic import TemplateView

urlpatterns = patterns('',
        (r'^feedback/', include('feedback.urls'),),
        (r'^demo/', TemplateView.as_view(template_name='demo.html')),
        )

