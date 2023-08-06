# -*- coding: utf-8 -*-
from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Sequence,
)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Person(Base):

    __tablename__ = 'person'
    firstname = Column(String)
    lastname = Column(String)
    id = Column(Integer,index = True, primary_key = True)
    addresses = relationship('Address', backref = 'person', primaryjoin = 'Address.person_id==Person.id')

class Address(Base):

    __tablename__ = 'address'
    street = Column(String)
    city = Column(String)
    country = Column(String)
    zip = Column(String)
    id = Column(Integer,index = True, primary_key = True)
    person_id = Column(Integer, ForeignKey('person.id'), nullable = False)