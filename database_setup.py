
from sqlalchemy import Column, ForeignKey, Integer, String, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class Place(Base):
    __tablename__ = 'places'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    phones = Column(String, nullable=True)
    hours = Column(String, nullable=True)
    rating = Column(Float, default=0)
    num_ratings = Column(Integer, default=0)
    comments = relationship('Comment', backref='place', lazy=True)

class Comment(Base):
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True)
    text = Column(String, nullable=False)
    place_id = Column(Integer, ForeignKey('places.id'), nullable=False)


class Event(Base):
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    date = Column(String(100), nullable=False)
    location = Column(String(200), nullable=False)

engine = create_engine('sqlite:///main.db')
Base.metadata.create_all(engine)
