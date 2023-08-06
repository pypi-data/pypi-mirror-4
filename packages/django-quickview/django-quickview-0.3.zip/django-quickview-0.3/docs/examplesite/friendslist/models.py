from django.db import models
from django.contrib.auth.models import User

class FriendManager(models.Manager):
    def get_query_set(self):
        return super(FriendManager, self).get_query_set().select_related().order_by('-added')

class Friend(models.Model):

    class Meta:
        get_latest_by = 'added'

    name = models.CharField(max_length = 100)
    email = models.EmailField(null = True, blank = True)
    address = models.CharField(max_length = 100)
    city = models.CharField(max_length = 100)
    zip_code = models.CharField(max_length = 20)
    country = models.CharField(max_length = 100)
    phone = models.CharField(max_length = 100)
    added_by = models.ForeignKey(User, null=True, blank=True)
    added = models.DateTimeField(auto_now=True, auto_now_add=True)

    objects = FriendManager()

class Comment(models.Model):
    friend = models.ForeignKey(Friend, related_name="comments")
    text = models.TextField()
    author = models.CharField(max_length=100)


class Spew(models.Model):
    text = models.CharField(max_length=150)
    author = models.ForeignKey(User)
    added = models.DateTimeField(auto_now=True, auto_now_add=True)

    def __unicode__(self):
        return '"%s" says %s at %s' % (self.text, self.author.username, self.added)
