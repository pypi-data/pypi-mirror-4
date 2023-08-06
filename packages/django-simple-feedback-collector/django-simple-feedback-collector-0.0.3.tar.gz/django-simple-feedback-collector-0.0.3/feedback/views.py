import json

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt, get_token

from .forms import FeedbackForm
from .models import Campaign

@csrf_exempt
def accept_feedback_api(request, campaign_slug):
    if request.method == 'POST' and request.is_ajax() == True:
        campaign = get_object_or_404(Campaign, pk=campaign_slug)
        form=FeedbackForm(request.POST)
        if form.is_valid():
            form.save(campaign)
            document = json.dumps({'status':'ok'})
            return HttpResponse(document, mimetype='application/json') 

    document = json.dumps({'status': 'error'})
    return HttpResponse(document, mimetype='application/json') 

