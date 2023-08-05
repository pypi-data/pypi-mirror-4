# This silly stuff is just for testing

from django.db import models

class MdlUser(models.Model):
    inactive = models.BooleanField()
    username = models.CharField(unique=True, max_length=255)
    some_date = models.DateField(blank=True, null=True)

class Moo(models.Model):
    name = models.CharField(max_length=255)
    users = models.ManyToManyField(MdlUser, blank=True,null=True)
    just_one = models.ForeignKey(MdlUser, blank=True,null=True, related_name="one_moo")
    def __unicode__(self):
        return unicode(self.name)

class MooBar(models.Model):
    MooFK = models.ForeignKey(Moo, related_name="just_one_moo")
    Moos = models.ManyToManyField(Moo)
    def __unicode__(self):
        return unicode('I am a moobar')