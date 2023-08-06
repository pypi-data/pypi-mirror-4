from django.contrib.contenttypes.models import ContentType
from log_register.models import Lot
from log_register.settings import ERROR, DEBUG, SUCCESS, WARNING, INFO


def get_lot_for_objects(obj, force=False):
    """
    This method returns (creates id needed) a Lot object for a object in data base.
    This is useful to register many log for a particular object.
    If (because you do it) there are many particular instance, this method raise a MultipleObjectsReturned
    exception; but, if 'force' is True, the method delete all instances and create a new.
    (This wouldn't happen, if you don't create a Lot instance with single flag set as True)
    """
    content_type = ContentType.objects.get_for_model(obj)
    object_id = obj.id

    try:
        lot = Lot.objects.get(content_type=content_type, object_id=object_id, single=True)
    except Lot.objects.model.MultipleObjectsReturned as e:
        if force:
            lots = Lot.objects.filter(content_type=content_type, object_id=object_id, single=True)
            lots.delete()
        else:
            raise e
        lot = Lot(single=True, lot_object=obj)
        lot.save()

    return lot


def error_of_model(reason, extra_data, log_object):
    """
    This method let you log a error log for a object.
    Note that the flag param 'force' is not available here, because there must be only ONE object to register
    all logs for a particular object.
    """
    log = log_for_model(reason, extra_data, log_object, ERROR)
    return log


def info_of_model(reason, extra_data, log_object):
    """
    This method let you log a info log for a object.
    """
    log = log_for_model(reason, extra_data, log_object, INFO)
    return log


def warning_of_model(reason, extra_data, log_object):
    """
    This method let you log a warning log for a object.
    """
    log = log_for_model(reason, extra_data, log_object, WARNING)
    return log


def debug_of_model(reason, extra_data, log_object):
    """
    This method let you log a debug log for a object.
    """
    log = log_for_model(reason, extra_data, log_object, DEBUG)
    return log


def success_of_model(reason, extra_data, log_object):
    """
    This method let you log a success log for a object.
    """
    log = log_for_model(reason, extra_data, log_object, SUCCESS,)
    return log


def log_for_model(reason, extra_data, log_object, level=INFO,):
    """
    This method let you log a log for a object.
    (By default, the level is a INFO, but you can import and use more levels from
    log_register/settings.py module)
    """
    lot = get_lot_for_objects(log_object, True)
    log = lot.log(reason, extra_data, level, log_object)
    return log


__author__ = 'leandro'
