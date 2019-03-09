from django.db import models


class Playlist(models.Model):
    """
    Playlist model.
    """

    name = models.CharField('Playlist name', max_length=128)

    def __str__(self):
        return self.name


class PlaylistItem(models.Model):
    """
    Music item in playlist model.
    """

    playlist = models.ForeignKey(Playlist, verbose_name='Playlist', related_name='playlist_items',
                                 on_delete=models.CASCADE)
    title = models.CharField('Title')
    uri = models.CharField('URI')

    def __str__(self):
        return self.title
