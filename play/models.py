from django.db import models

# Create your models here.


class Play(models.Model):
    """
    Playlist model.
    """

    playlist_id = models.IntegerField('Playlist id')
    current_item = models.IntegerField('Current item id')

