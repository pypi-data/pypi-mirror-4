import datetime
from django.db import models

class DictModel(models.Model, dict):

    """
    An abstract model to make Models have dictionary-like interface
    """

    def __iter__(self):
        for i in self.__class__._meta.fields:
            yield i

    def __getitem__(self, key):
        if key in self.fields:
            return getattr(self, key)
        else:
            raise KeyError, '%s is not a field.' % key

    def __setitem__(self, key, value):
        if key in self.fields:
            return setattr(self, key, value)
        else:
            raise KeyError, '%s is not a field.' % key

    def items(self):
        return [(field.name, self[field.name]) for field in self]

    @property
    def fields(self):
        """
        Get a list containing all fields in this model
        """
        if self._fields is None:
            self._fields = [field.name for field in self]
        return self._fields

    def dict(self, convert_datetime_to_timestamp=False):
        """
        Convert a model into dict

        Keyword Arguments:
        convert_datetime_to_timestamp -- convert datetime objects to integer form (unix timestamp) (default False)
        """
        result = dict(self.items())
        if convert_datetime_to_timestamp:
            datetimes = [(key, int(value.strftime('%s'))) for key, value in result.items()
                         if isinstance(value, datetime.datetime) or
                            isinstance(value, datetime.date)]
            result = result.update(dict(datetimes))
        return result

    class Meta:
        abstract = True

class TimestampModel(models.Model):

    """
    Add 2 time fields (create and modify) into model
    """

    createTime = models.DateTimeField(auto_now_add=True)
    modifyTime = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

__all__ = [
    DictModel.__name__,
    TimestampModel.__name__,
]
