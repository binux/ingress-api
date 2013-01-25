#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: set et sw=4 ts=4 sts=4 ff=unix fenc=utf8:
# Author: Binux<i@binux.me>
#         http://binux.me
# Created on 2013-01-24 21:29:41

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()

class Portal(Base):
    __tablename__ = 'portal'

    guid = Column(String, primary_key=True)
    uptime = Column(Integer)
    control = Column(String)
    latE6 = Column(Integer)
    lngE6 = Column(Integer)
    level = Column(Integer)
    energy = Column(Integer)

class GEOCell(Base):
    __table__ = 'geo_cell'

    id = Column(Integer, primary_key=True)
    latE6 = Column(Integer)
    lngE6 = Column(Integer)
    cell = Column(String)

engine = create_engine('sqlite:///aio.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
