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

from sqlalchemy.ext.declarative import (
    declarative_base,
    AbstractConcreteBase,
)

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
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
    street = Column(String(50))
    city = Column(String(50))
    postal_code = Column(String(6))
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
    __tablename__ = 'account'
    origin_id = Column(String(21), nullable=False)
    provider = Column(String(50), nullable=False)
    name = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    link = Column(String(50))
    gender = Column(String(1))
    created_at = Column(DateTime)
    last_login = Column(DateTime)
    login_count = Column(Integer, default=0)

    settings = relationship('AccountSettings', cascade="delete, all")


class AccountSettings(BaseEntity):
    __tablename__ = 'account_settings'
    account_id = Column(Integer, ForeignKey('account.id'))
    recomendations_range = Column(Integer)

    likings = relationship('AccountLiking', cascade="delete, all")


class Category(BaseEntity):
    __tablename__ = 'category'
    name = Column(String(50), nullable=False, unique=True)
    color = Column(String(6), nullable=False)
    icon_path = Column(String(50))


class Subcategory(BaseEntity):
    __tablename__ = 'subcategory'
    name = Column(String(50), nullable=False, unique=True)
    color = Column(String(6), nullable=False)
    icon_path = Column(String(50))
    category_id = Column(Integer, ForeignKey('category.id'))


class AccountLiking(BaseEntity):
    __tablename__ = 'account_liking'
    account_settings_id = Column(Integer, ForeignKey('account_settings.id'))
    category_id = Column(Integer, ForeignKey('category.id'))
    subcategory_id = Column(Integer, ForeignKey('subcategory.id'))
    level = Column(String(1))

    category = relationship('Category', cascade="delete, all")
    subcategory = relationship('Subcategory', cascade="delete, all")
