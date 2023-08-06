from django.forms import ModelForm

from .models import Campaign, Feedback


class FeedbackForm(ModelForm):
    class Meta:
        model = Feedback
        include = ['identifier','location', 'text']

    def save(self, campaign):
        feedback = super(FeedbackForm, self).save()
        feedback.campaign = campaign
        feedback.save()
