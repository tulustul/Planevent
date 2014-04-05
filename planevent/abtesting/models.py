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


class Experiment(BaseEntity):
    __tablename__ = 'experiment'
    name = Column(String(150), unique=True)
    description = Column(Text)
    created_at = Column(DateTime)
    started_at = Column(DateTime)
    ended_at = Column(DateTime)
    active = Column(Boolean)
    in_preparations = Column(Boolean)
    winner_name = Column(String(150))

    variations = relationship("Variation", cascade="delete, all")


class Variation(BaseEntity):
    __tablename__ = 'experiment_variation'
    name = Column(String(150))
    description = Column(Text)
    probability = Column(Integer)
    receivers_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    experiment_id = Column(Integer, ForeignKey('experiment.id'))
