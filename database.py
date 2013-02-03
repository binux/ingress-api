#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: set et sw=4 ts=4 sts=4 ff=unix fenc=utf8:
# Author: Binux<i@binux.me>
#         http://binux.me
# Created on 2013-01-24 21:29:41

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

import utils

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
    ignore = Column(Boolean, default=False)
    group = Column(String)

    @property
    def latlng(self):
        return utils.LatLng(self.latE6*1e-6, self.lngE6*1e-6)

    def __repr__(self):
        return '<DBPortal#%s %s+%d @%f,%f>' % (self.guid, self.control, self.level, self.latE6*1e-6, self.lngE6*1e-6)

class GEOCell(Base):
    __tablename__ = 'geo_cell'
    __table_args__ = (
        UniqueConstraint('latE6', 'lngE6', 'cell'),
        {},
    )

    latE6 = Column(Integer, primary_key=True)
    lngE6 = Column(Integer, primary_key=True)
    cell = Column(String, primary_key=True)

LogBase = declarative_base()
class HackLog(LogBase):
    __tablename__ = 'hack_log'

    id = Column(Integer, primary_key=True)
    guid = Column(String)
    time = Column(DateTime, default=func.now())
    enemy = Column(Integer)
    resonators = Column(String)
    mods = Column(String)
    level = Column(Float)
    
    damage = Column(Integer, default=0)
    res1 = Column(Integer, default=0)
    res2 = Column(Integer, default=0)
    res3 = Column(Integer, default=0)
    res4 = Column(Integer, default=0)
    res5 = Column(Integer, default=0)
    res6 = Column(Integer, default=0)
    res7 = Column(Integer, default=0)
    res8 = Column(Integer, default=0)
    buster1 = Column(Integer, default=0)
    buster2 = Column(Integer, default=0)
    buster3 = Column(Integer, default=0)
    buster4 = Column(Integer, default=0)
    buster5 = Column(Integer, default=0)
    buster6 = Column(Integer, default=0)
    buster7 = Column(Integer, default=0)
    buster8 = Column(Integer, default=0)
    shield6 = Column(Integer, default=0)
    shield8 = Column(Integer, default=0)
    shield10 = Column(Integer, default=0)
    key = Column(Integer, default=0)

engine = create_engine('sqlite:///aio.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

engine_log = create_engine('sqlite:///log.db')
LogBase.metadata.create_all(engine_log)
LogSession = sessionmaker(bind=engine_log)
