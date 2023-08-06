from django.core.cache import cache
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


class CachedManager(models.Manager):

    def get_from_cache(self, id):
        """
        Fetches the snippet from cache, and if for some reason it's missing,
        add it to the cache after retrieval.
        """
        snippet = cache.get('snippet:{0}'.format(id))
        if not snippet:
            snippet = Snippet.objects.get(id=id)
            cache.set('snippet:{0}'.format(id), snippet)
        return snippet


class Snippet(models.Model):
    """
    Model for storing snippets of text for replacement in templates
    """
    id = models.CharField(max_length=100, primary_key=True)
    text = models.TextField()
    objects = CachedManager()

    class Meta:
        ordering = ('id',)

    def __unicode__(self):
        return self.id


@receiver(post_save, sender=Snippet)
def set_cached_business(sender, **kwargs):
    """Update the cached copy of the snippet on creation or change"""
    instance = kwargs.pop('instance')
    cache.set('snippet:{0}'.format(instance.id), instance)


@receiver(post_delete, sender=Snippet)
def clear_cached_business(sender, **kwargs):
    """Remove the cached copy of the snippet after deletion"""
    instance = kwargs.pop('instance')
    cache.delete('snippet:{0}'.format(instance.id))
