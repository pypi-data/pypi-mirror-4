Log Register Documentation
==========================

:Author:
    Leandro Gomez <leandro.gz73@gmail.com>
:Version: 0.1.3

::

    pip install django-log-register==0.1.3


Django Log Register is a simple application for Django.
It's a simple way to save this error, warning, success, info, and debug log; everything in database.
You can reference to another model in database, to be able to know who makes you system fails.

``Lot``: It's a lot of logs where you can register error, warning, info, debug or success logs (See details below).
``Log``: This is a error, a warning or another message level (by default the same of django message) with the reason.

``Examples:``

Suppose that you want to register each successful creation of a model, or its fail if it's not created

    creation_logs = Lot()
    for n in range(10):
        try:
            obj = SomeModel(attr=1, attr=2)
            obj.save()
            creation_logs.success("A obj have been created!") #Only the reason param is required!
        except Exception as e:
            creation_logs.error("A obj have not been created!")
    creation_logs.close() #Don't forget to close the Lot, this can indicate you if the process finished fine.

Now suppose the same context, but you want the real exception and some context to can find a solution.

    creation_logs = Lot()
    for n in range(10):
        try:
            attr1 = some_calculated_value()
            attr2 = 20
            obj = SomeModel(attr1=attr1, attr2=attr2)
            obj.save()
            creation_logs.success(
                        "A obj have been created!",
                        "with attr1=%(attr1)s and attr2=%(attr2)s" % dict(attr1=attr1, attr2=attr2)
                        ) #You can add some extra_data if you wish or need it

        except Exception as e:
            context = "attr1=%(attr1)s and attr2=%(attr2)s" % dict(attr1=attr1, attr2=attr2)
            creation_logs.error(str(e), context)
            #make a str(e) is my favourite way to register a error log, and let the extra_data provide me
            # what I need to solve the problem.
    creation_logs.close()

Now suppose that you are updating many instances of models, and can register which model update has fail.

    creation_logs = Lot()
        for id in range(5):
            try:
                obj = MyModel.objects.get(id=id)
                making_something(obj)
                creation_logs.success("A obj have been update!")
            except SomeException as e:
                context = "model=%(model)s and id=%(id)s" % dict(model=model, id=id)
                if 'obj' in locals()::
                    creation_logs.error(str(e), context, log_object=obj)
                else:
                    creation_logs.error(str(e), context)
    creation_logs.close()

But you maybe want to even logs for a object in the same Lot; so... you can make this:

    from lot_register.actions import get_lot_for_objects

    obj1 = MyModel()
    onj2 = MySecondModel()

    lot = get_lot_for_objects(obj1)

    # make something with obj1 and obj2
    lot.log("I make something with my obj1 with another obj2!!", "some extra data",log_object=obj2)
    #or...
    try:
        obj1.make_something(obj2)
    except:
        lot.error("Something went wrong", log_object=obj2)
