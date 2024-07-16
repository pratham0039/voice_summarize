from django.db import models

class Video(models.Model):
    file = models.FileField(upload_to='videos/')
    transcription = models.TextField(blank=True, null=True)
    summary = models.TextField(blank=True, null=True)
