import transaction

from sqlalchemy import (
    Column,
    Index,
    Integer,
    Float,
    Text,
    DateTime,
    Boolean,
    ForeignKey,
)

from sqlalchemy.ext.declarative import (
    declarative_base,
    AbstractConcreteBase,
)

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
    class_mapper,
)

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))

Base = declarative_base()


class BaseEntity(AbstractConcreteBase, Base):
    id = Column(Integer, primary_key=True)

    @classmethod
    def query(cls):
         return DBSession.query(cls)

    @classmethod
    def all(cls):
         return DBSession.query(cls).all()

    @classmethod
    def get(cls, id_):
         return DBSession.query(cls).get(id_)

    def delete(self):
        # TODO
        pass

    def save(self):
        with transaction.manager:
            if self.id is None:
                DBSession.add(self)
        # DBSession.commit()

    def __json__(self, request):
        return self.serialize()

    def serialize(self):
        mapper = class_mapper(self.__class__)
        columns = [c.key for c in mapper.columns if not c.foreign_keys]
        relationships = [c.key for c in mapper.relationships]
        result = dict((c, getattr(self, c)) for c in columns)
        for relation in relationships:
            child = getattr(self, relation)
            if isinstance(child, list):
                child = [c.serialize() for c in child]
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


class Vendor(BaseEntity):
    __tablename__ = 'vendor'
    name = Column(Text)
    description = Column(Text)
    category = Column(Integer)
    added_at = Column(DateTime)
    updated_at = Column(DateTime)

    address_id = Column(Integer, ForeignKey('address.id'))
    logo_id = Column(Integer, ForeignKey('image.id'), nullable=True)

    contacts = relationship("Contact")
    address = relationship("Address")
    logo = relationship("Image")
    gallery = relationship("ImageGallery")


class Address(BaseEntity):
    __tablename__ = 'address'
    street = Column(Text)
    city = Column(Text)
    postal_code = Column(Text)
    longitude = Column(Float)
    latitude = Column(Float)
    validated = Column(Boolean, default=False)


class Contact(BaseEntity):
    __tablename__ = 'contact'
    vendor_id = Column(Integer, ForeignKey('vendor.id'))
    type = Column(Integer)
    value = Column(Text)
    description = Column(Text)


class Image(BaseEntity):
    __tablename__ = 'image'
    path = Column(Text)


class ImageGallery(BaseEntity):
    __tablename__ = 'image_gallery'
    path = Column(Text)
    vendor_id = Column(Integer, ForeignKey('vendor.id'))
