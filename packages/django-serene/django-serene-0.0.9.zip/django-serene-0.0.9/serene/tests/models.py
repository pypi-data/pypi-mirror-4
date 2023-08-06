from django.db import models as django_models
from serene import models as serene_models


class DummyModel(serene_models.Model):
    name = serene_models.CharField(max_length=1024)

    def __unicode__(self):
        return self.name

class DummierModel(django_models.Model):
    name = django_models.CharField(max_length=1024)

    def __unicode__(self):
        return self.name

class Brand(serene_models.Model):
    name = serene_models.CharField(max_length=1024)
    code = serene_models.CharField(max_length=1024)

    def __unicode__(self):
        return self.name

    @serene_models.permalink
    def get_absolute_url(self):
        return ('brand_instance', (), {'id': self.id})

class Product(serene_models.Model):
    name = serene_models.CharField(max_length=1024)
    code = serene_models.CharField(max_length=1024)
    color = serene_models.CharField(max_length=1024)
    brand = serene_models.ForeignKey(Brand)

    def __unicode__(self):
        return self.name

    @serene_models.permalink
    def get_absolute_url(self):
        return ('product_instance', (), {'id': self.id})