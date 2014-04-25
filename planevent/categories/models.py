from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
)

from sqlalchemy.orm import relationship

from planevent.core.sql import BaseEntity


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
