from datetime import datetime

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
from planevent.accounts.models import Account
from planevent import redisdb


class OfferTag(BaseEntity):
    __tablename__ = 'offer_tags'
    offer_id = Column(Integer, ForeignKey('offer.id'))
    tag_id = Column(Integer, ForeignKey('tag.id'))

    tag = relationship('Tag', cascade="delete, all")


class Offer(BaseEntity):
    VIEW_COUNT = 'offerviewcount:{}'  # .format(offer_id)

    class Status(object):
        ACTIVE = 1
        INACTIVE = 2
        DELETED = 3

    STATUSES_MAP = {
        1: 'ACTIVE',
        2: 'INACTIVE',
        3: 'DELETED',
    }

    __tablename__ = 'offer'
    name = Column(String(150))
    short_description = Column(String(200))
    description = Column(Text)
    category_id = Column(Integer, ForeignKey('category.id'))
    added_at = Column(DateTime)
    updated_at = Column(DateTime)
    promotion = Column(Integer)
    price_min = Column(Integer)
    price_max = Column(Integer)
    preview_image_url = Column(String(150))
    to_complete = Column(Boolean)
    status = Column(Integer, nullable=False)

    author_id = Column(Integer, ForeignKey('account.id'), nullable=False)
    address_id = Column(Integer, ForeignKey('address.id'))
    logo_id = Column(Integer, ForeignKey('image.id'), nullable=True)

    author = relationship("Account", cascade="delete, all")
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

    def user_can_edit(self, user_dict):
        if user_dict:
            return (
                user_dict['id'] == self.author_id or
                user_dict['role'] == Account.Role.ADMIN
            )
        else:
            return False

    def save(self):
        self.updated_at = datetime.now()
        super().save()

    def serialize(self):
        dict_ = super().serialize()
        dict_['status'] = self.STATUSES_MAP[self.status]
        return dict_

    def deserialize(self, dict_):
        super().deserialize(dict_)
        self.status = next(
            key for key, value in self.STATUSES_MAP.items()
            if value == self.status
        )
        return self


class Contact(BaseEntity):
    __tablename__ = 'contact'
    offer_id = Column(Integer, ForeignKey('offer.id'))
    type = Column(String(20))
    value = Column(String(50))
    description = Column(Text)


class Image(BaseEntity):
    __tablename__ = 'image'
    path = Column(String(50))


class ImageGallery(BaseEntity):
    __tablename__ = 'image_gallery'
    path = Column(String(50))
    description = Column(Text())
    offer_id = Column(Integer, ForeignKey('offer.id'))


class Tag(BaseEntity):
    __tablename__ = 'tag'
    name = Column(String(50), nullable=False, unique=True)
    references_count = Column(Integer, default=0)
