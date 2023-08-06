from sqlalchemy import event
from s4u.sqlalchemy import model
from s4u.sqlalchemy.meta import BaseObject


@event.listens_for(BaseObject, 'class_instrument')
def register_model(cls):
    setattr(model, cls.__name__, cls)


@event.listens_for(BaseObject, 'class_uninstrument')
def unregister_model(cls):
    if hasattr(model, cls.__name__):
        delattr(model, cls.__name__)
