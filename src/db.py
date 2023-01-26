from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


DeclarativeBase = declarative_base()

class RepresentableTable():
    noRepr = []
    
    def __repr__(self):
        keys = [elem for elem in vars(type(self)).keys() if not elem.startswith("_") and elem not in self.noRepr]
        keys = ["__tablename__"] + keys
        output = [f"{key}: {repr(getattr(self, key))}" for key in keys]
        return "\n".join(output)
        

class Database:
    def __init__(self, Session):
        self.Session = Session

    def __with_session(function):
        def wrapper(self, *args, **kwargs):
            session = None
            result = None

            try:
                session = self.Session()
                result = function(self, session=session, *args, **kwargs)
            except Exception as ex:
                print(ex)
                if session is not None:
                    session.rollback()
            if session is not None:
                session.close()

            return result
        return wrapper
    

    @__with_session
    def __get(self, object, session=None):
        return session.query(object)

    @__with_session
    def __add(self, object, session=None):
        session.add(object)
        session.commit()

    @__with_session
    def __delete(self, object, session=None):
        if object is not None:
            object = session.merge(object)
            session.delete(object)
            session.commit()
    
    @__with_session
    def __update(self, object, changed_field, session=None):
        if object is not None:
            object = session.merge(object)
            for key in changed_field.keys():
                if hasattr(object, key):
                    setattr(object, key, changed_field[key])
            session.commit()

    @__with_session
    def __append_childs(self, object, childs, session=None):
        if object is not None:
            object = session.merge(object)
            for key in childs.keys():
                if hasattr(object, key):
                    getattr(object, key).append(childs[key])
            session.commit()


    def get(self, value, object, by):
        return self.__get(object).filter(by == value).first()

    def get_all(self, object):
        return self.__get(object).all()
    
    def add(self, object):
        self.__add(object)

    def delete(self, object):
        self.__delete(object)

    def update(self, object, changed_fields):
        self.__update(object, changed_fields)

    def append_childs(self, object, childs):
        self.__append_childs(object, childs)