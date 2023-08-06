from django.contrib.contenttypes.models import ContentType
from django.db.models import Manager
from log_register.settings import ERROR, DEBUG, WARNING, SUCCESS, INFO


class LotManager(Manager):
    """
    Manager for Lot model, accessed through Lot.objects
    """

    def singles(self, **kwargs):
        """
        Return all single Lots.
        """
        kwargs['single'] = True
        return self.filter(**kwargs)

    def lot_for_object(self, obj, **kwargs):
        """
        Return all lots for a object
        """
        kwargs['content_type'] = ContentType.objects.get_for_model(obj)
        kwargs['object_id'] = obj.id
        return self.filter(**kwargs)


class LogManager(Manager):
    """
    Manager for Log model, accessed through Log.objects
    """

    def logs_for_level(self, level=INFO, **kwargs):
        """
        Return all log with level 'level', by default 'INFO' (see also log_register.settings)
        """
        kwargs['level'] = level
        return self.filter(**kwargs)

    def errors(self, **kwargs):
        """
        Returns all log with level ERROR
        """
        return self.logs_for_level(ERROR, **kwargs)

    def warnings(self, **kwargs):
        """
        Returns all log with level WARNING
        """
        return self.logs_for_level(WARNING, **kwargs)

    def info(self, **kwargs):
        """
        Returns all log with level INFO
        """
        return self.logs_for_level(INFO, **kwargs)

    def debugs(self, **kwargs):
        """
        Returns all log with level DEBUG
        """
        return self.logs_for_level(DEBUG, **kwargs)

    def success(self, **kwargs):
        """
        Returns all log with level SUCCESS
        """
        return self.logs_for_level(SUCCESS, **kwargs)

    def logs_for_object(self, obj, **kwargs):
        """
        Returns all log where 'obj' is the log_object
        """
        kwargs['content_type'] = ContentType.objects.get_for_model(obj)
        kwargs['object_id'] = obj.id
        return self.filter(**kwargs)


__author__ = 'leandro'
