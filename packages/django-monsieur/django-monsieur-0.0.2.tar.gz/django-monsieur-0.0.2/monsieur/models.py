from django.db import models

class Tag(models.Model):
    name = models.CharField(max_length=100)
    points = models.ManyToManyField('DataPoint', related_name='tags')

    def __unicode__(self):
        return self.name

class DataPoint(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    count = models.FloatField()
    dt = models.DateTimeField(db_index=True)
    attributes = models.ManyToManyField('DataAttribute', related_name='points')

    def __unicode__(self):
        return '%s=%s' % (self.name, self.count)

class DataAttribute(models.Model):
    id = models.CharField(max_length=200, primary_key=True)
    key = models.CharField(max_length=100)
    value = models.CharField(max_length=100)

    @classmethod
    def make(cls, key, value):
        return '%s=%s' % (key, value)

    @classmethod
    def split(cls, id):
        return id.split('=')

    def __unicode__(self):
        return self.id
