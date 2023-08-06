# -*- coding: utf-8 -*-
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Sequence,
)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Company(Base):

    __tablename__ = 'company'
    name = Column(String)