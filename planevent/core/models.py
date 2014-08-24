import json
import math

from sqlalchemy import (
    Column,
    Float,
    String,
    Boolean,
)

from planevent.core.sql import BaseEntity


class Json(dict):
    def __init__(self, s):
        super().__init__(json.loads(s))


class Address(BaseEntity):
    __tablename__ = 'address'
    street = Column(String(50), default='')
    city = Column(String(50), default='')
    postal_code = Column(String(6), default='')
    formatted = Column(String(50), default='')
    longitude = Column(Float)
    latitude = Column(Float)
    validated = Column(Boolean, default=False)

    def distance_to(self, lat, lon):
        # Euclidean space for simplicity and speed. We don't need high
        # precision here
        return math.sqrt(
            (self.latitude - lat) ** 2 + (self.longitude - lon) ** 2
        )
