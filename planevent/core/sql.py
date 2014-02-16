from sqlalchemy import (
    Column,
    Integer,
)

from sqlalchemy.ext.declarative import (
    declarative_base,
    AbstractConcreteBase,
)

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    class_mapper,
    joinedload,

)

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))

Base = declarative_base()


class BaseEntity(AbstractConcreteBase, Base):
    id = Column(Integer, primary_key=True)

    @classmethod
    def get_query_options(cls, *relations):
        if len(relations) == 1 and relations[0] == '*':
            return [joinedload(c.key) for c in class_mapper(cls).relationships]
        else:
            return [joinedload(relation) for relation in relations]

    @classmethod
    def query(cls, *relations):
        query = DBSession.query(cls)
        return query.options(cls.get_query_options(*relations))

    @classmethod
    def all(cls, *relations):
        return cls.query(*relations).all()

    @classmethod
    def get(cls, id_, *relations):
        return cls.query(*relations).get(id_)

    @classmethod
    def delete(cls, id_):
        DBSession.delete(cls.get(id_))
        DBSession.flush()

    def save(self):
        if self.id is None:
            DBSession.add(self)
        else:
            DBSession.merge(self)
        DBSession.flush()

    def __json__(self, request=None):
        return self.serialize()

    def serialize(self):
        mapper = class_mapper(self.__class__)
        columns = [col.key for col in mapper.columns if not col.foreign_keys]
        relationships = [c.key for c in mapper.relationships]
        result = dict((c, getattr(self, c)) for c in columns)
        for relation in relationships:
            if relation not in self.__dict__:
                continue
            child = getattr(self, relation)
            if isinstance(child, list):
                child = [elem.serialize() for elem in child]
            elif isinstance(child, BaseEntity):
                child = child.serialize()
            result[relation] = child
        return result

    def deserialize(self, dict_):
        if dict_ is None:
            return

        mapper = class_mapper(self.__class__)
        columns = [c.key for c in mapper.columns if not c.foreign_keys]
        relationships = [c for c in mapper.relationships]

        for column in columns:
            if column in dict_.keys():
                setattr(self, column, dict_[column])

        for relation in relationships:
            if relation.key in dict_.keys():
                child_dict = dict_[relation.key]
                if isinstance(child_dict, list):
                    for subchild in child_dict:
                        child = relation.mapper.class_()
                        child.deserialize(subchild)
                        getattr(self, relation.key).append(child)
                else:
                    child = relation.mapper.class_()
                    child.deserialize(child_dict)
                    setattr(self, relation.key, child)
        return self
