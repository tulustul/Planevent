from sqlalchemy import (
    Column,
    Text,
    String,
    DateTime,
    Boolean,
)

from planevent.core.sql import BaseEntity


class Feedback(BaseEntity):
    __tablename__ = 'feedback'
    email = Column(String(50))
    created_at = Column(DateTime, nullable=False)
    checked = Column(Boolean, nullable=False)
    title = Column(Text, nullable=False)
    content = Column(Text)
