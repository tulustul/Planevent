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

    def deserialize(self):
        pass


class Vendor(BaseEntity):
    __tablename__ = 'vendor'
    name = Column(Text)
    description = Column(Text)
    category = Column(Integer)
    added_at = Column(DateTime)
    updated_at = Column(DateTime)

    address_id = Column(Integer, ForeignKey('address.id'))
    logo_id = Column(Integer, ForeignKey('image.id'), nullable=True)
    gallery_id = Column(Integer, ForeignKey('gallery.id'))

    contacts = relationship("Contact")
    address = relationship("Address")
    logo = relationship("Image")
    gallery = relationship("Gallery")


class Address(BaseEntity):
    __tablename__ = 'address'
    first_line = Column(Text)
    second_line = Column(Text)
    longitude = Column(Float)
    latitude = Column(Float)
    validated = Column(Boolean)


class Contact(BaseEntity):
    __tablename__ = 'contact'
    vendor_id = Column(Integer, ForeignKey('vendor.id'))
    type = Column(Integer)
    value = Column(Text)
    description = Column(Text)


class Image(BaseEntity):
    __tablename__ = 'image'
    gallery_id = Column(Integer, ForeignKey('gallery.id'), nullable=True)
    path = Column(Text)


class Gallery(BaseEntity):
    __tablename__ = 'gallery'
    images = relationship("Image")
