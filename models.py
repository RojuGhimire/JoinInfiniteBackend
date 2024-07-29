import datetime
from sqlalchemy import ARRAY, Column, Float, ForeignKey, Integer, String, DateTime, Boolean
from database import Base
from enum import Enum
from sqlalchemy.orm import relationship
from sqlalchemy import Enum as SQLAlchemyEnum


class UserRole(str, Enum):
    organizer = 'organizer'
    user = 'user'

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(200), nullable=False)
    role = Column(String(20), nullable=False, server_default=UserRole.user)
    age = Column(String(3), nullable=False, server_default='18')
    address = Column(String(100), nullable=False)
    photo_url = Column(String, nullable=True)
    interested_genre=Column(ARRAY(String),nullable=True)
    refresh_token = Column(String(450),nullable=True)
    refresh_token_expiry = Column(DateTime,nullable=True)
    latitude = Column(Float,nullable=True)
    longitude = Column(Float,nullable=True)
    created_date = Column(DateTime, default=datetime.datetime.now)
    


class Event(Base):
    __tablename__ = "event"
    id = Column(Integer, primary_key=True)
    event_name = Column(String(255), index=True)
    description = Column(String)
    date = Column(DateTime)
    location_latitude = Column(Float)
    location_longitude = Column(Float)
    location_address=Column(String, nullable=True)
    created_date = Column(DateTime, default=datetime.datetime.now)
    organizer_id = Column(Integer, ForeignKey('users.id'))
    photo_url = Column(String)
    genre = Column(String)
    organizer = relationship(User)

class UserInteraction(Base):
    __tablename__ = "user_interaction"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    event_id = Column(Integer, ForeignKey('event.id'))
    interested = Column(Boolean, default=False)
    liked = Column(Boolean, default=False)
    created_date = Column(DateTime, default=datetime.datetime.now)

    user = relationship(User)
    event = relationship(Event)


# Import necessary modules
    
class NotificationType(str, Enum):
    EventLiked ="EVENT_LIKED"
    EventInterested = "EVENT_INTERESTED"
    EventCreated = "EVENT_CREATED"


class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    event_id=Column(Integer, ForeignKey('event.id'))
    message = Column(String)
    notification_type = Column(SQLAlchemyEnum(NotificationType), nullable=False)
    created_date = Column(DateTime, default=datetime.datetime.now)

    user = relationship(User)
    event=relationship(Event)
