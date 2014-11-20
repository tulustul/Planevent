from collections import namedtuple
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
    String,
    DateTime,
    Boolean,
    ForeignKey,
)

from sqlalchemy.orm import relationship

from planevent.core.sql import BaseEntity
from planevent.core.models import Address
from planevent.categories.models import Subcategory
from planevent import settings


class Account(BaseEntity):
    class Role:
        ANONYMOUS = 1
        NORMAL = 2
        EDITOR = 3
        ADMIN = 4

    class PasswordToShort(Exception):
        pass

    __tablename__ = 'account'
    name = Column(String(50))
    email = Column(String(50))
    first_name = Column(String(50))
    last_name = Column(String(50))
    link = Column(String(50))
    gender = Column(String(1), default='U', nullable=False)
    created_at = Column(DateTime)
    last_login = Column(DateTime)
    login_count = Column(Integer, default=0)
    role = Column(Integer, default=Role.NORMAL)
    password_protected = Column(Boolean, default=False)
    avatar = Column(String(200))

    settings_id = Column(Integer, ForeignKey('account_settings.id'))
    credentials_id = Column(Integer, ForeignKey('account_credentials.id'))

    credentials = relationship('AccountCrendentials', cascade="delete, all")
    settings = relationship('AccountSettings', cascade="delete, all")
    likings = relationship('AccountLiking', cascade="delete, all")

    @classmethod
    def create(cls, **kwargs):
        account = cls(
            created_at=datetime.now(),
            login_count=0,
            settings=AccountSettings(
                address=Address(),
            ),
            credentials=AccountCrendentials(),
            **kwargs
        )

        if not account.name:
            account._build_username()

        account.save()

        for subcategory in Subcategory.all():
            liking = AccountLiking(
                account_id=account.id,
                subcategory=subcategory,
            )
            liking.save()

        return account

    @classmethod
    def get_by_email(cls, email, *relations):
        return cls.query(*relations) \
            .filter(cls.email == email) \
            .first()

    @classmethod
    def get_by_provider(cls, provider_name, id_in_provider):
        credentials = (
            AccountCrendentials.query()
            .filter(AccountCrendentials.provider == provider_name)
            .filter(AccountCrendentials.origin_id == id_in_provider)
            .first()
        )
        if credentials:
            return cls.query().filter(
                cls.credentials_id == credentials.id
            ).first()
        else:
            return None

    def _build_username(self):
        if self.first_name:
            self.name = self.first_name
            if self.last_name:
                self.name += self.last_name
        elif self.email:
            self.name = self.email

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
        self.password_protected = True

    def check_password(self, password):
        password_hash = self._generate_password_hash(password)
        return password_hash == self.credentials.password_hash

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
    Recommendations = namedtuple(
        'Recommendations',
        ('lat', 'lon', 'distance'),
    )

    __tablename__ = 'account_settings'
    use_recommendations = Column(Boolean, default=True)
    recomendations_range = Column(Integer, default=10)
    address_id = Column(Integer, ForeignKey('address.id'))

    address = relationship("Address", cascade="delete, all")

    @property
    def recommendations(self):
        if self.address and self.address.validated:
            return self.Recommendations(
                lat=self.address.latitude,
                lon=self.address.longitude,
                distance=self.recomendations_range,
            )
        else:
            return None


class AccountLiking(BaseEntity):
    class Level:
        DISLIKE = 1
        MEH = 2
        LIKE = 3
        LOVE = 4

    __tablename__ = 'account_liking'

    account_id = Column(Integer, ForeignKey('account.id'))
    subcategory_id = Column(Integer, ForeignKey('subcategory.id'))
    level = Column(Integer, default=Level.MEH)

    subcategory = relationship('Subcategory', cascade="delete, all")
