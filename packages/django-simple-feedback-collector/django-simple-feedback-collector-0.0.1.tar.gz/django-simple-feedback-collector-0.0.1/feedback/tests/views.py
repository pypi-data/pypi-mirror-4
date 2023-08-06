import json

from django.test import TestCase

from ..models import Campaign


class TestApiView(TestCase):
    urls = 'example_project.urls'

    def setUp(self):
        self.campaign = Campaign(name='My Campaign', slug='mycampaign')
        self.campaign.save()

    def test_empty_submission(self):
        response = self.client.post('/feedback/mycampaign/api/')
        parsed_response = json.loads(response.content)
        self.assertIn("status", parsed_response)
        self.assertEqual("error", parsed_response.get('status'))

    def test_valid_feedback(self):
        feedback = dict(identifier='Ross',
                        location="Scranton",
                        text="good work!")
        response = self.client.post('/feedback/mycampaign/api/',
                                    feedback,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        parsed_response = json.loads(response.content)
        self.assertIn("status", parsed_response)
        self.assertEqual("ok", parsed_response.get('status'))

    def tearDown(self):
        self.campaign.delete()
