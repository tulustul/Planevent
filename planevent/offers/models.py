from sqlalchemy import (
    Column,
    Integer,
    Text,
    String,
    DateTime,
    Boolean,
    ForeignKey,
)

from sqlalchemy.orm import relationship

from planevent.core.sql import BaseEntity
from planevent import redisdb


class OfferTag(BaseEntity):
    __tablename__ = 'offer_tags'
    offer_id = Column(Integer, ForeignKey('offer.id'))
    tag_id = Column(Integer, ForeignKey('tag.id'))

    tag = relationship('Tag', cascade="delete, all")


class Offer(BaseEntity):
    VIEW_COUNT = 'offerviewcount:{}'  # .format(offer_id)

    __tablename__ = 'offer'
    name = Column(String(150))
    description = Column(Text)
    category_id = Column(Integer, ForeignKey('category.id'))
    added_at = Column(DateTime)
    updated_at = Column(DateTime)
    promotion = Column(Integer)
    price_min = Column(Integer)
    price_max = Column(Integer)
    preview_image_url = Column(String(150))
    to_complete = Column(Boolean)

    address_id = Column(Integer, ForeignKey('address.id'))
    logo_id = Column(Integer, ForeignKey('image.id'), nullable=True)

    category = relationship("Category", cascade="delete, all")
    contacts = relationship("Contact", cascade="delete, all")
    address = relationship("Address", cascade="delete, all")
    logo = relationship("Image", cascade="delete, all")
    gallery = relationship("ImageGallery", cascade="delete, all")
    tags = relationship('Tag',
                        secondary=OfferTag.__table__,
                        cascade="delete, all")

    @property
    def views_count(self):
        return redisdb.redis_db.get(self.VIEW_COUNT.format(self.id))

    def increment_views_count(self):
        redisdb.redis_db.incr(self.VIEW_COUNT.format(self.id))


class Contact(BaseEntity):
    __tablename__ = 'contact'
    offer_id = Column(Integer, ForeignKey('offer.id'))
    type = Column(Integer)
    value = Column(String(50))
    description = Column(Text)


class Image(BaseEntity):
    __tablename__ = 'image'
    path = Column(String(50))


class ImageGallery(BaseEntity):
    __tablename__ = 'image_gallery'
    path = Column(String(50))
    offer_id = Column(Integer, ForeignKey('offer.id'))


class Tag(BaseEntity):
    __tablename__ = 'tag'
    name = Column(String(50), nullable=False, unique=True)
    references_count = Column(Integer, default=0)


class Category(BaseEntity):
    __tablename__ = 'category'
    name = Column(String(50), nullable=False, unique=True)
    color = Column(String(6), nullable=False)
    icon_path = Column(String(50))

    subcategories = relationship('Subcategory', cascade="delete, all")


class Subcategory(BaseEntity):
    __tablename__ = 'subcategory'
    name = Column(String(50), nullable=False, unique=True)
    color = Column(String(6), nullable=False)
    icon_path = Column(String(50))
    category_id = Column(Integer, ForeignKey('category.id'))
    # TODO
    # add optional automatic tags
    # add optional automatic age restriction + bool if age restriction is
    # validated (in offer)
