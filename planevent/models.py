import hashlib
import os
import uuid
from datetime import (
    datetime,
    timedelta,
)

from sqlalchemy import (
    Column,
    Integer,
    Float,
    Text,
    String,
    DateTime,
    Boolean,
    ForeignKey,
)

from sqlalchemy.orm import relationship

from planevent.core.sql import BaseEntity
from planevent import settings


class VendorTag(BaseEntity):
    __tablename__ = 'vendor_tags'
    vendor_id = Column(Integer, ForeignKey('vendor.id'))
    tag_id = Column(Integer, ForeignKey('tag.id'))

    tag = relationship('Tag', cascade="delete, all")


class Vendor(BaseEntity):
    __tablename__ = 'vendor'
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
                        secondary=VendorTag.__table__,
                        cascade="delete, all")


class Address(BaseEntity):
    __tablename__ = 'address'
    street = Column(String(50), default='')
    city = Column(String(50), default='')
    postal_code = Column(String(6), default='')
    formatted = Column(String(50), default='')
    longitude = Column(Float)
    latitude = Column(Float)
    validated = Column(Boolean, default=False)


class Contact(BaseEntity):
    __tablename__ = 'contact'
    vendor_id = Column(Integer, ForeignKey('vendor.id'))
    type = Column(Integer)
    value = Column(String(50))
    description = Column(Text)


class Image(BaseEntity):
    __tablename__ = 'image'
    path = Column(String(50))


class ImageGallery(BaseEntity):
    __tablename__ = 'image_gallery'
    path = Column(String(50))
    vendor_id = Column(Integer, ForeignKey('vendor.id'))


class Tag(BaseEntity):
    __tablename__ = 'tag'
    name = Column(String(50), nullable=False, unique=True)
    references_count = Column(Integer, default=0)


class Account(BaseEntity):
    class Type:
        NORMAL = 1
        EDITOR = 2
        ADMIN = 3

    class PasswordToShort(Exception):
        pass

    __tablename__ = 'account'
    name = Column(String(50))
    email = Column(String(50), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    link = Column(String(50))
    gender = Column(String(1))
    created_at = Column(DateTime)
    last_login = Column(DateTime)
    login_count = Column(Integer, default=0)
    role = Column(Integer, default=Type.NORMAL)
    settings_id = Column(Integer, ForeignKey('account_settings.id'))
    credentials_id = Column(Integer, ForeignKey('account_credentials.id'))

    credentials = relationship('AccountCrendentials', cascade="delete, all")
    settings = relationship('AccountSettings', cascade="delete, all")
    likings = relationship('AccountLiking', cascade="delete, all")

    @classmethod
    def create(cls, **kwargs):
        return cls(
            created_at=datetime.now(),
            login_count=0,
            settings=AccountSettings(
                address=Address(),
            ),
            credentials=AccountCrendentials(),
            **kwargs
        )

    @classmethod
    def get_by_email(cls, email, *relations):
        return cls.query(*relations) \
            .filter(cls.email == email) \
            .first()

    def _generate_password_hash(self, password):
        hash = hashlib.sha256()
        hash.update((password + self.credentials.password_salt).encode('utf8'))
        return hash.hexdigest()

    def set_password(self, password):
        if len(password) < settings.MINIMUM_PASSWORD_LENGTH:
            raise self.PasswordToShort()

        salt = hashlib.sha256()
        salt.update(os.urandom(32))
        self.credentials.password_salt = salt.hexdigest()
        self.credentials.password_hash = self._generate_password_hash(password)

    def check_password(self, password):
        return self._generate_password_hash(password) == \
            self.credentials.password_hash

    def generate_recall_password_token(self):
        self.credentials.recall_token = uuid.uuid4().hex
        self.credentials.recall_token_expiry = datetime.now() + timedelta(
            hours=settings.RECALL_PASSWORD_TOKEN_EXPIRATION_TIME
        )


class AccountCrendentials(BaseEntity):
    __tablename__ = 'account_credentials'
    origin_id = Column(String(50))
    provider = Column(String(50))
    password_hash = Column(String(64))
    password_salt = Column(String(64))
    recall_token = Column(String(50))
    recall_token_expiry = Column(DateTime)


class AccountSettings(BaseEntity):
    __tablename__ = 'account_settings'
    recomendations_range = Column(Integer, default=10)
    address_id = Column(Integer, ForeignKey('address.id'))

    address = relationship("Address", cascade="delete, all")


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
    # validated (in vendor)


class AccountLiking(BaseEntity):
    __tablename__ = 'account_liking'
    account_id = Column(Integer, ForeignKey('account.id'))
    category_id = Column(Integer, ForeignKey('category.id'))
    subcategory_id = Column(Integer, ForeignKey('subcategory.id'))
    level = Column(String(1))

    category = relationship('Category', cascade="delete, all")
    subcategory = relationship('Subcategory', cascade="delete, all")
