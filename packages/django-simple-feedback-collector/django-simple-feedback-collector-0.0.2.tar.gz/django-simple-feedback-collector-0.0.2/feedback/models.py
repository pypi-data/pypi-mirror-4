from django.db import models

class Campaign(models.Model):
    """
    A campaign is a named bucket for feedback-- it's just a name and a slug.
    """
    name = models.CharField(max_length=255)
    slug = models.SlugField(primary_key=True)


class Feedback(models.Model):
    """
    Saves submitted feedback, optionally with an identifier and location.
    (both loosely defined)
    """
    identifier = models.CharField(max_length=1000, blank=True)
    location = models.CharField(max_length=1000, blank=True)
    text = models.TextField(blank=True)
    campaign = models.ForeignKey(Campaign, null=True, blank=True)

