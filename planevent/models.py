from sqlalchemy import (
    Column,
    Index,
    Integer,
    Float,
    Text,
    ForeignKey,
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
    )

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class User(object):
    __tablename__ = 'user'
    name = Column(Text)


class Vendor(Base):
    __tablename__ = 'vendor'
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    description = Column(Text)
    address = Column(Integer, ForeignKey('address.id'))
    category = Column(Integer)
    contacts = relationship("Contact")
    logo = Column(Integer, ForeignKey('image.id'))
    gallery = Column(Integer, ForeignKey('gallery.id'))


class Address(Base):
    __tablename__ = 'address'
    id = Column(Integer, primary_key=True)
    first_line = Column(Text)
    second_line = Column(Text)
    longitude = Column(Float)
    latitude = Column(Float)


class Contact(Base):
    __tablename__ = 'contact'
    id = Column(Integer, primary_key=True)
    vendor_id = Column(Integer, ForeignKey('vendor.id'))
    contact_type = Column(Integer)
    contact_value = Column(Text)
    contact_description = Column(Text)


class Image(Base):
    __tablename__ = 'image'
    id = Column(Integer, primary_key=True)
    gallery_id = Column(Integer, ForeignKey('gallery.id'), nullable=True)
    path = Column(Text)


class Gallery(Base):
    __tablename__ = 'gallery'
    id = Column(Integer, primary_key=True)
    images = relationship("Image")
