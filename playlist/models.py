from django.db import models


class Playlist(models.Model):
    """
    Playlist model.
    """

    name = models.CharField('Playlist name', max_length=128)
    direct = models.BooleanField('Direct play')

    def __str__(self):
        return self.name


class PlaylistItem(models.Model):
    """
    Music item in playlist model.
    """

    playlist = models.ForeignKey(Playlist, verbose_name='Playlist', related_name='playlist_items',
                                 on_delete=models.CASCADE)
    title = models.CharField('Title', max_length=256)
    uri = models.CharField('URI', max_length=1024)

    def __str__(self):
        return self.title
