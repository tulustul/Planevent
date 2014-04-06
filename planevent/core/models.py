from sqlalchemy import (
    Column,
    Float,
    String,
    Boolean,
)

from planevent.core.sql import BaseEntity


class Address(BaseEntity):
    __tablename__ = 'address'
    street = Column(String(50), default='')
    city = Column(String(50), default='')
    postal_code = Column(String(6), default='')
    formatted = Column(String(50), default='')
    longitude = Column(Float)
    latitude = Column(Float)
    validated = Column(Boolean, default=False)
