import datetime

from django.db import models
from djangorestframework.serializer import Serializer, _SkipField, _fields_to_dict, _fields_to_list, _serializers


# Inject/Override methods in djangorestframework Serializer.
# Necessary because OnTheFlySerializer is based on djangorestframework Serializer.
def links(self, instance):
    try:
        if isinstance(instance, dict) and instance.get('links'):
            # links already exists
            return instance['links']
        else:
            return {
                'self': {
                    'href': instance.get_absolute_url(),
                    'rel': 'self',
                    'title': unicode(instance),
                }
            }
    except (AttributeError, NotImplementedError):
        raise _SkipField
Serializer.links = links

def title(self, instance):
    if isinstance(instance, models.Model):
        return unicode(instance)
    else:
        return instance['title']
Serializer.title = title

Serializer._serialize = Serializer.serialize
def serialize(self, obj):
    if isinstance(obj, (datetime.datetime, datetime.date, datetime.time,)):
        return obj.isoformat()
    else:
        return self._serialize(obj)
Serializer.serialize = serialize

Serializer._get_fields = Serializer.get_fields
def get_fields(self, obj):
    return _fields_to_list(self._get_fields(obj))
Serializer.get_fields = get_fields

Serializer._get_related_serializer = Serializer.get_related_serializer
def get_related_serializer(self, key):
    fields = self.fields
    if not fields:
        include = self.include or ()
        exclude = self.exclude or ()
        fields = set(include) - set(exclude)

    info = _fields_to_dict(fields).get(key, None)

    # If an element in `fields` is a 2-tuple of (str, tuple)
    # then the second element of the tuple is the fields to
    # set on the related serializer
    if isinstance(info, (list, tuple)):
        class OnTheFlySerializer(Serializer):
            fields = info
        return OnTheFlySerializer

    # If an element in `fields` is a 2-tuple of (str, Serializer)
    # then the second element of the tuple is the Serializer
    # class to use for that field.
    elif isinstance(info, type) and issubclass(info, Serializer):
        return info

    # If an element in `fields` is a 2-tuple of (str, str)
    # then the second element of the tuple is the name of the Serializer
    # class to use for that field.
    #
    # Black magic to deal with cyclical Serializer dependancies.
    # Similar to what Django does for cyclically related models.
    elif isinstance(info, str) and info in _serializers:
        return _serializers[info]

    # Otherwise use `related_serializer` or fall back to `Serializer`
    return getattr(self, 'related_serializer') or Serializer
Serializer.get_related_serializer = get_related_serializer
# End djangorestframework method injection/override


class RelatedSerializer(Serializer):

    def serialize_model(self, instance):
        """
        serialize_model serializes both Model and dict.
        """
        if isinstance(instance, models.Model):
            return {
                'id': instance.id,
                'title': unicode(instance),
                'links': {
                    'self': {
                        'href': instance.get_absolute_url(),
                        'rel': 'self',
                        'title': unicode(instance),
                    }
                },
            }
        else:
            return super(RelatedSerializer, self).serialize_model(instance)