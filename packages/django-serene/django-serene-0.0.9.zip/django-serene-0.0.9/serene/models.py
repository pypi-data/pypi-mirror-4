from django.db.models import *


class Model(Model):
    last_modified = DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    @permalink
    def get_absolute_url(self):
        raise NotImplementedError("Please implement get_absolute_url() for each model.")