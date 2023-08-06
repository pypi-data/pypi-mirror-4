from django.test import TestCase

from ..models import Campaign, Feedback
from ..forms import FeedbackForm

class TestFeedbackSubmission(TestCase):
    def setUp(self):
        self.campaign = Campaign(name= 'My Campaign', slug='mycampaign')

    def test_feedback_form_processing(self):
        """
        test form submission
        """
        campaign = self.campaign
        form = FeedbackForm({'identifier': 'fake@example.com', 'location': 'toledo',
                            'text': 'No, sir; I didn\'t like it'})

        
        self.assertTrue(form.is_valid())
        saved_feedback = form.save(campaign)

        feedback_on_campaign = campaign.feedback_set.all()

        self.assertEqual(feedback_on_campaign.count(), 1)
                            
